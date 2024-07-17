from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings

from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

import os

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

    print("Gmail_auth is running")
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

    print("Gmail_auth is done")
    return redirect(auth_url)


def gmail_auth_callback(request):
    print("Gmail_auth_callback is running")
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
        'scopes': credentials.scopes
    }
    print("Credentials: ", request.session['credentials'])
    return HttpResponse('Authorization complete, credentials stored in session')


def read_emails(request):
    if not request.user.is_authenticated:
        return redirect('../accounts/login')
    try:
        creds = request.session['credentials']
    # If credentials are not in session then go to auth
    except KeyError:
        return redirect("gmail-auth")

    try:
        # Calling Gmail API
        service = build("gmail", 'v1', credentials=creds)
        results = service.users().messages().list(userId="me").execute()
        emails = results.get("messages")