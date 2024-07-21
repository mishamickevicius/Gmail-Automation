from .forms import EmailForm

from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.models import User

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import google.generativeai as genai


import os
import base64
import email


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        user = request.user.username
        is_logged_in = True
    else:
        is_logged_in = False
        user = None
    return render(request, 'main/home.html',
                  {
                      'username': user,
                      'is_logged_in': is_logged_in,
                  })


def gmail_auth(request):
    if not request.user.is_authenticated:
        return redirect('../accounts/login')

    # Create a flow to get authorization from user
    flow = Flow.from_client_config(
        settings.CLIENT_SECRETS,
        scopes=[
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid',
            'https://mail.google.com/'
        ],
        redirect_uri=request.build_absolute_uri(reverse('gmail-auth-callback'))
    )
    # Get authorization url
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    # Store the state in session to verify callback
    request.session['state'] = state

    return redirect(auth_url)


def gmail_auth_callback(request):
    # Get state
    state = request.session.get('state')
    flow = Flow.from_client_config(
        settings.CLIENT_SECRETS,
        scopes=[
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/userinfo.email',
            'openid',
            'https://mail.google.com/'
        ],
        state=state,
        redirect_uri=request.build_absolute_uri(reverse('gmail-auth-callback'))
    )

    # Allow Inscure Transport i.e. using http not https
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes,
        # 'authorize': credentials.authorize,
    }
    return redirect('home-page')


def read_emails(request):
    if not request.user.is_authenticated:
        return redirect('../accounts/login')
    try:
        creds_dict = request.session['credentials']
        creds = Credentials.from_authorized_user_info(info=creds_dict)
    # If credentials are not in session then go to auth
    except KeyError:
        return redirect("gmail-auth")

    try:
        # Calling Gmail API
        service = build("gmail", 'v1', credentials=creds)
        email_list = service.users().messages().list(userId="me", maxResults=10, labelIds=['CATEGORY_PERSONAL']).execute().get('messages')
        emails = []
        for msg in email_list:
            email_id = msg['id']
            email_data = service.users().messages().get(userId='me', id=email_id).execute()
            headers = email_data['payload']['headers']
            subject = [h['value'] for h in headers if h['name'] == 'Subject'][0]
            emails.append({
                'id': email_data['id'],
                'sender': next(h for h in email_data['payload']['headers'] if h['name'] == 'From')['value'],
                'subject': next(h for h in email_data['payload']['headers'] if h['name'] == 'Subject')['value'],
                'snippet': email_data['snippet'],
                'date': next(h for h in email_data['payload']['headers'] if h['name'] == 'Date')['value'],
            })

        return render(request, "main/emails.html", {'emails': emails, 'is_logged_in': True})
    except HttpError as error:
        print(f"error has occurred: {error}")
        return render(request, 'main/error.html', {'error': error})


def show_email(request, email_id):
    if not request.user.is_authenticated:
        return redirect('../accounts/login')
    try:
        creds_dict = request.session['credentials']
        creds = Credentials.from_authorized_user_info(info=creds_dict)
    # If credentials are not in session then go to auth
    except KeyError:
        return redirect("gmail-auth")

    service = build("gmail", "v1", credentials=creds)
    try:
        result = service.users().messages().get(userId='me', id=email_id, format='raw').execute()
        msg_str = base64.urlsafe_b64decode(result['raw'].encode('ASCII')).decode('UTF-8')
        msg = email.message_from_string(msg_str)
        email_subject = msg['subject']
        email_from = msg['from']
        email_to = msg['to']
        email_date = msg['date']
        email_body = ""

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    email_body = part.get_payload(decode=True).decode('utf-8')
                elif part.get_content_type() == 'text/html':
                    email_body = part.get_payload(decode=True).decode('utf-8')
        else:
            email_body = msg.get_payload(decode=True).decode('utf-8')

        context = {
            'subject': email_subject,
            'from': email_from,
            'to': email_to,
            'date': email_date,
            'body': email_body,
            'is_logged_in': True,
            'email_id':email_id,
        }
        return render(request, 'main/show_email.html', context)
    except Exception as e:
        return render(request, 'main/error.html', {'error': e})


def reply_email(request, email_id):
    if not request.user.is_authenticated:
        return redirect('../accounts/login')
    try:
        creds_dict = request.session['credentials']
        creds = Credentials.from_authorized_user_info(info=creds_dict)
    # If credentials are not in session then go to auth
    except KeyError:
        return redirect("gmail-auth")

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                # Send Email
                service = build('gmail', 'v1', credentials=creds)
                message = email.message.EmailMessage()
                message.set_content(form.cleaned_data['message'])
                message['To'] = form.cleaned_data['to']
                message['From'] = request.user.email
                message['Subject'] = form.cleaned_data['subject']

                encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

                create_message = {'raw': encoded_message}
                send_message = service.users().messages().send(userId='me', body=create_message).execute()

                return redirect("read-emails")
            except HttpError as error:
                print(f"Error has occured: {error}")
                return render(request, 'main/error.html', {'error': error})

    # For GET Method
    # Get generated response from Gemini API
    genai.configure(api_key=settings.GEMINI_API_KEY.replace("/", ""))
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Get email for context to model
    service = build("gmail", "v1", credentials=creds)
    result = service.users().messages().get(userId='me', id=email_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(result['raw'].encode('ASCII')).decode('UTF-8')
    response = model.generate_content(f"Write a response from the recipient to this email: {msg_str}. "
                                      f"If there is many messages in one then write a response for the most recent one."
                                      f"Do not include the subject line or RE: in the response.")
    form = EmailForm(initial={'message': str(response.text).format()})
    return render(request, 'main/reply.html', {
        "api_response": response,
        "is_logged_in": True,
        "email_form": form
    })
