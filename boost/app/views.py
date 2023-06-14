import datetime
from io import BytesIO

from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as login_auth
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import HttpResponseForbidden

from accounts import forms
from accounts.models import User

from app.disk_invoker import unique_name_generator, DiskInvoker, COMMANDS
from app.forms import DocCreationForm, DocEditForm, CommentForm, TagsSortForm, SearchForm
from app.models import Doc
from app.tokens import account_activation_token
from app.sort_docs import SortDocs


# Create your views here.

DISK_TOKEN = 'y0_AgAAAAAs42RnAADLWwAAAADkSmq8xdq1CK6VQqCG_Jye3CX-lBg-4iQ'
DISK_PATH = '/BOOST/'


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


def index(request):
    context = {}

    if request.GET.get('drop'):
        return redirect('/')

    sort_docs = SortDocs(request)
    sort_docs.convert()
    docs = sort_docs.make_request()

    context['sort_form'] = TagsSortForm(
        initial={
            'studies': sort_docs.studies,
            'sort_type': sort_docs.sort_type_get,
            'subjects': sort_docs.subjects,
        }
    )
    context['search_form'] = SearchForm(
        initial={
            'q': sort_docs.search
        }
    )
    context['docs'] = docs
    context['has_docs'] = True

    return render(request, 'main.html', context)


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


def profile(request, pk):
    context = {}
    user_profile = User.objects.get(pk=pk)
    docs = Doc.objects.filter(
        author=user_profile
    )

    if request.GET.get('drop'):
        return redirect(f'/id{request.user.pk}')

    sort_docs = SortDocs(request)
    sort_docs.convert()
    docs = sort_docs.make_request(docs)

    context['sort_form'] = TagsSortForm(
        initial={
            'studies': sort_docs.studies,
            'sort_type': sort_docs.sort_type_get,
            'subjects': sort_docs.subjects,
        }
    )
    context['search_form'] = SearchForm(
        initial={
            'q': sort_docs.search
        }
    )

    context['user_profile'] = user_profile
    context['docs'] = docs
    context['has_docs'] = True

    return render(request, 'profile.html', context)


def profile_edit(request, pk):
    context = {}

    if request.user.pk != pk:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = forms.UserChangeForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()

            messages.success(request, 'Изменения успешно сохранены!')

            return redirect('/')

    else:
        form = forms.UserChangeForm(
            initial={
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        )

    context['form'] = form

    return render(request, 'profile_edit.html', context)


def bookmarks(request):
    context = {}

    docs = request.user.bookmarks.all()

    if request.GET.get('drop'):
        return redirect('/bookmarks')

    sort_docs = SortDocs(request)
    sort_docs.convert()
    docs = sort_docs.make_request(docs)

    context['sort_form'] = TagsSortForm(
        initial={
            'studies': sort_docs.studies,
            'sort_type': sort_docs.sort_type_get,
            'subjects': sort_docs.subjects,
        }
    )
    context['search_form'] = SearchForm(
        initial={
            'q': sort_docs.search
        }
    )
    context['docs'] = docs
    context['has_docs'] = True

    return render(request, 'bookmarked_docs.html', context)


def doc_page(request, pk):
    doc = Doc.objects.get(pk=pk)
    context = {
        'doc': doc
    }

    form = CommentForm()

    if request.method == 'POST':
        if request.POST.get('delete'):
            disk_invoker = DiskInvoker(token=DISK_TOKEN)
            disk_invoker.run(COMMANDS.DELETE, path=doc.path)
            doc.delete()
            return redirect('/')

        if form.is_valid():
            pass

    context['form'] = form

    return render(request, 'doc_page.html', context)


def doc_page_edit(request, pk):
    context = {}
    doc = Doc.objects.get(pk=pk)

    if request.user.username != doc.author.username:
        return HttpResponseForbidden()

    form = DocEditForm(
        initial={
            'title': doc.title.lower(),
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
                disk_invoker.run(COMMANDS.DELETE, path=doc.path)

                path = DISK_PATH + unique_name_generator()

                disk_invoker = DiskInvoker(token=DISK_TOKEN)
                response_file = BytesIO(
                    [i for i in request.FILES['file'].chunks()][0]
                )
                disk_invoker.run(COMMANDS.UPLOAD, path=path, file=response_file)
                disk_invoker.run(COMMANDS.PUBLISH, path=path)

                doc.link = disk_invoker.run(COMMANDS.INFO, path=path)['public_url']
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
            return redirect('/login/')

    else:
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

            disk_invoker.run(COMMANDS.UPLOAD, path=path, file=response_file)
            disk_invoker.run(COMMANDS.PUBLISH, path=path)
            info = disk_invoker.run(COMMANDS.INFO, path=path)

            doc = Doc(
                title=form.cleaned_data.get('title').lower(),
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

            return redirect(f'/document{doc.pk}')

    else:
        form = DocCreationForm()

    context['form'] = form
    return render(request, 'create_docs.html', context)
