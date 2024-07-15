from .forms import LoginForm, UserCreationForm

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


# Create your views here.

def login_view(request):
    # Check if form is POSTED
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']  # Get data out of form and try to authenticate
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:  # If no authentication then return message to user
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    # If method is GET then render login form
    return render(request, 'users/login.html', {'form': form})


def signup_view(request):
    # Check if Form is POSTED
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')
