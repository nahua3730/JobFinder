from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def signup(request):
    # Placeholder for User Story 1
    return render(request, 'users/signup.html') 

def login_view(request):
    # We will use Django's built-in auth views later, but this maps the URL for now
    return render(request, 'users/login.html')

def logout_view(request):
    # Placeholder
    return redirect('jobs:home')