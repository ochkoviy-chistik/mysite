import datetime
from io import BytesIO
import dotenv

from django.contrib import messages

from django.shortcuts import render, redirect

from django.http import HttpResponseForbidden

from .disk_invoker import unique_name_generator, DiskInvoker, COMMANDS
from .forms import DocCreationForm, DocEditForm, CommentForm, TagsSortForm, SearchForm
from .models import Doc
from .sort_docs import SortDocs

from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.

DISK_TOKEN = dotenv.get_key(r'.env', 'DISK_TOKEN')
DISK_PATH = dotenv.get_key(r'.env', 'DISK_PATH')


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

    for i in range(len(docs)):
        docs[i].title = docs[i].title.capitalize()

    context['docs'] = docs
    context['has_docs'] = True

    return render(request, 'main.html', context)


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

    for i in range(len(docs)):
        docs[i].title = docs[i].title.capitalize()

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

    for i in range(len(docs)):
        docs[i].title = docs[i].title.capitalize()

    context['docs'] = docs
    context['has_docs'] = True

    return render(request, 'bookmarked_docs.html', context)


def doc_page(request, pk):
    doc = Doc.objects.get(pk=pk)
    doc.title = doc.title.capitalize()

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
            'title': str(doc.title).capitalize(),
            'description': doc.description,
            'subjects': doc.subjects.all(),
            'studies': doc.studies.all(),
        }
    )
    if request.method == 'POST':
        form = DocEditForm(request.POST, request.FILES)

        if form.is_valid():
            doc.title = str(form.cleaned_data.get('title')).lower()
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
                title=str(form.cleaned_data.get('title')).lower(),
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
