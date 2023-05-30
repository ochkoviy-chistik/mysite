from django.shortcuts import render, redirect
from accounts import forms
from accounts.models import User

# Create your views here.


def index(request):
    return render(request, 'main.html', {})


def profile(request):
    context = {}
    return render(request, 'profile.html', context)


def sign_up(request):
    context = {}

    if request.POST:
        form = forms.RegisterForm(request.POST)
        form.save()

        return redirect('/')

    context['form'] = forms.RegisterForm()
    return render(request, 'registration/signup.html', context)
