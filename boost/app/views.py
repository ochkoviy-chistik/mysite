import datetime

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.conf import settings

from accounts import forms
from app.third_party.ImageManager import ImageManager

from app.forms import DocCreationForm, DocEditForm, CommentForm, TagsSortForm, SearchForm
from app.models import Doc
from app.third_party.sort_docs import SortDocs


User = get_user_model()


# Create your views here.


def index(request):
    context = {}

    return render(request, 'index.html', context)


def docs_page(request):
    context = {}

    if request.GET.get('drop'):
        return redirect('/docs')

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

    return render(request, 'docs.html', context)


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
        manager = ImageManager(request.user.avatar.path)
        form = forms.UserChangeForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            if 'avatar' in request.FILES:
                request.user.avatar = request.FILES['avatar']

            else:
                manager.delete()
                request.user.avatar = settings.DEFAULT_AVATAR

            form.save()

            messages.success(request, 'Изменения успешно сохранены!')

            return redirect(f'/id{request.user.pk}')

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
            manager = ImageManager(doc.preview.path)
            manager.delete()
            doc.delete()

            return redirect('/docs')

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
        manager = ImageManager(doc.preview.path)
        form = DocEditForm(request.POST, request.FILES)

        if form.is_valid():
            doc.title = str(form.cleaned_data.get('title')).lower()
            doc.description = form.cleaned_data.get('description')

            if 'preview' in request.FILES:
                doc.preview = request.FILES['preview']

            else:
                manager.delete()
                doc.preview = settings.DEFAULT_PREVIEW

            if 'file' in request.FILES:
                file = request.FILES['file'].chunks()
                doc.use_file(file)

            doc.save()

            doc.studies.set(form.cleaned_data.get('studies'))
            doc.subjects.set(form.cleaned_data.get('subjects'))

            return redirect(f'/document{doc.pk}')

    context['form'] = form
    context['doc'] = doc

    return render(request, 'doc_edit.html', context)


def create_docs(request):
    context = {}

    if request.method == 'POST':
        form = DocCreationForm(request.POST, request.FILES)

        if form.is_valid():
            doc = Doc(
                title=str(form.cleaned_data.get('title')).lower(),
                description=form.cleaned_data.get('description'),
                author=request.user,
                date=datetime.datetime.now()
            )

            if 'preview' in request.FILES:
                doc.preview = request.FILES['preview']

            file = request.FILES['file'].chunks()

            doc.use_file(file)
            doc.save()

            doc.studies.set(form.cleaned_data.get('studies'))
            doc.subjects.set(form.cleaned_data.get('subjects'))

            return redirect(f'/document{doc.pk}')

    else:
        form = DocCreationForm()

    context['form'] = form
    return render(request, 'create_docs.html', context)
