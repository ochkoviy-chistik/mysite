from django.shortcuts import render, redirect

from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login as login_auth
from django.template.loader import render_to_string
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages

from django.contrib.auth import get_user_model
from .tokens import account_activation_token

from . import forms

# Create your views here.

User = get_user_model()


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

    return redirect('/login/')


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
        messages.success(request, f'Для завершения регистрации подтвердите почту {user.email}.')
    else:
        messages.error(request, 'Что-то пошло не так :(')


def sign_up(request):
    context = {}

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activate_email(request, user, form.cleaned_data.get('email'))
            return redirect('/login/')

    else:
        form = forms.RegisterForm()

    context['form'] = form
    return render(request, 'registration/signup.html', context)


def login(request):
    context = {}

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(email=email, password=password)

            if user is not None:

                if user.is_active:
                    login_auth(request, user)
                    messages.success(request, 'Вы успешно вошли в аккаунт!')

                    next_url = request.GET.get('next')

                    if next_url is not None:
                        return redirect(next_url)

                    return redirect('/')

                else:
                    messages.error(request, 'Аккаунт не активирован!')

            else:
                messages.error(request, 'Неверный логин или пароль!')

    else:
        form = forms.LoginForm()

    context['form'] = form

    return render(request, 'registration/login.html', context)


class StyledPasswordResetView (PasswordResetView):
    form_class = forms.FloatPasswordResetForm


class StyledPasswordResetConfirmView (PasswordResetConfirmView):
    form_class = forms.SetFloatPasswordForm
