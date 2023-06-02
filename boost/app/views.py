import datetime
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from accounts import forms

from app.disk_invoker import unique_name_generator, DiskInvoker
from app.forms import DocCreationForm, DocEditForm
from accounts.models import User
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponseForbidden

from app.models import Doc
from app.tokens import account_activation_token
from io import BytesIO
import dotenv


# Create your views here.

DISK_TOKEN = dotenv.get_key(r'.env', 'DISK_TOKEN')
DISK_PATH = dotenv.get_key(r'.env', 'DISK_PATH')


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
    context = {
        'docs': Doc.objects.all().order_by('-pk')
    }
    return render(request, 'main.html', context)


def profile(request):
    context = {}
    return render(request, 'profile.html', context)


def doc_page(request, pk):
    doc = Doc.objects.get(pk=pk)
    context = {
        'doc': doc
    }

    if request.method == 'POST' and request.POST.get('delete'):
        disk_invoker = DiskInvoker(token=DISK_TOKEN)
        disk_invoker.run('delete', path=doc.path)
        doc.delete()

        return redirect('/')

    return render(request, 'doc_page.html', context)


def doc_page_edit(request, pk):
    context = {}
    doc = Doc.objects.get(pk=pk)

    if request.user.username != doc.author.username:
        return HttpResponseForbidden()

    form = DocEditForm(
        initial={
            'title': doc.title,
            'description': doc.description,
            'subjects': doc.subjects.all(),
            'studies': doc.studies.all(),
        }
    )
    if request.method == 'POST':
        form = DocEditForm(request.POST, request.FILES)

        if form.is_valid():
            doc.title = form.cleaned_data.get('title')
            doc.description = form.cleaned_data.get('description')

            if 'preview' in request.FILES:
                doc.preview = request.FILES['preview']
            else:
                doc.preview = 'media/default_images/default_document.png'

            if 'file' in request.FILES:
                disk_invoker = DiskInvoker(token=DISK_TOKEN)
                disk_invoker.run('delete', path=doc.path)

                path = DISK_PATH + unique_name_generator()

                disk_invoker = DiskInvoker(token=DISK_TOKEN)
                response_file = BytesIO(
                    [i for i in request.FILES['file'].chunks()][0]
                )
                disk_invoker.run('upload', path=path, file=response_file)
                disk_invoker.run('publish', path=path)

                doc.link = disk_invoker.run('get_info', path=path)['public_url']
                doc.path = path

            doc.save()

            doc.studies.set(form.cleaned_data.get('studies'))
            doc.subjects.set(form.cleaned_data.get('subjects'))

            return redirect('/')

    context['form'] = form
    context['doc'] = doc

    return render(request, 'doc_edit.html', context)


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

    form = forms.RegisterForm()

    context['form'] = form
    return render(request, 'registration/signup.html', context)


def create_docs(request):
    context = {}

    if request.method == 'POST':
        form = DocCreationForm(request.POST, request.FILES)

        if form.is_valid():
            path = DISK_PATH+unique_name_generator()

            disk_invoker = DiskInvoker(token=DISK_TOKEN)
            response_file = BytesIO(
                [i for i in request.FILES['file'].chunks()][0]
            )

            disk_invoker.run('upload', path=path, file=response_file)
            disk_invoker.run('publish', path=path)
            info = disk_invoker.run('get_info', path=path)

            doc = Doc(
                title=form.cleaned_data.get('title'),
                link=info['public_url'],
                path=path,
                description=form.cleaned_data.get('description'),
                author=request.user,
                date=datetime.datetime.now()
            )

            if 'preview' in request.FILES:
                doc.preview = request.FILES['preview']

            doc.save()
            doc.studies.set(form.cleaned_data.get('studies'))
            doc.subjects.set(form.cleaned_data.get('subjects'))

            return redirect('/')

    else:
        form = DocCreationForm()

    context['form'] = form
    return render(request, 'create_docs.html', context)
