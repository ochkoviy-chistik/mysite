from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from accounts import forms
from accounts.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .tokens import account_activation_token


# Create your views here.


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'SUCCESS')
    else:
        messages.error(request, 'ERROR')

    return redirect('/login')


def activate_email(request, user, to_email):
    mail_subj = 'Activate user.'
    message = render_to_string(
        'registration/activate_account.html',
        {
            'user': user.username,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http'
        }
    )
    email = EmailMessage(mail_subj, message, to=[to_email])

    if email.send():
        messages.success(request, 'SUCCESS')
    else:
        messages.error(request, 'ERROR')


def index(request):
    return render(request, 'main.html', {})


def profile(request):
    context = {}
    return render(request, 'profile.html', context)


def sign_up(request):
    context = {}

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect('/')

    else:
        form = forms.RegisterForm()

    context['form'] = form
    return render(request, 'registration/signup.html', context)
