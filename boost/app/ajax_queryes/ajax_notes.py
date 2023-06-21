import datetime

from django.http import JsonResponse
import json

from app.third_party.notes import Like, Dislike, Comment
from app.models import Doc


def get_data(request, pk):
    likes = Like.objects.filter(
        doc__pk=pk
    )
    dislikes = Dislike.objects.filter(
        doc__pk=pk
    )
    comments_response = Comment.objects.filter(
        doc__pk=pk
    ).order_by('-pk')
    bookmark = request.user.bookmarks.filter(
        pk=pk
    ).exists()

    comments = {
        'count': comments_response.count(),
        'data': [],
    }

    for comment in comments_response:
        comments['data'].append(
            {
                'pk': comment.pk,
                'text': comment.text,
                'author': str(comment.author),
                'date': comment.date,
            }
        )

    context = {
        'likes': likes.count(),
        'dislikes': dislikes.count(),
        'comments': comments,
        'bookmark': bookmark,
        'is_liked': likes.filter(author=request.user).exists(),
        'is_disliked': dislikes.filter(author=request.user).exists(),
    }

    return JsonResponse(context)


def like_post(request):
    if request.method == 'POST':
        data = json.load(request)

        doc = Doc.objects.get(pk=data['doc'])
        like = Like.objects.filter(
            doc=doc,
        )
        user_like = like.filter(author=request.user)

        likes = like.count()

        if not user_like.exists():
            Like(doc=doc, author=request.user).save()
            likes += 1
        else:
            user_like.delete()
            likes -= 1

        dislikes = Dislike.objects.filter(doc=doc).count()

        doc.likes = likes
        doc.dislikes = dislikes
        doc.save()

    return JsonResponse({})


def dislike_post(request):
    if request.method == 'POST':
        data = json.load(request)

        doc = Doc.objects.get(pk=data['doc'])
        dislike = Dislike.objects.filter(
            doc=doc,
        )
        user_dislike = dislike.filter(author=request.user)

        dislikes = dislike.count()

        if not user_dislike.exists():
            Dislike(doc=doc, author=request.user).save()
            dislikes += 1
        else:
            user_dislike.delete()
            dislikes -= 1

        likes = Like.objects.filter(doc=doc).count()

        doc.likes = likes
        doc.dislikes = dislikes
        doc.save()

    return JsonResponse({})


def comment_post(request):

    if request.method == 'POST':
        data = json.load(request)

        doc = Doc.objects.get(pk=data['doc'])

        comment = Comment(
            text=data['text'],
            doc=doc,
            author=request.user,
            date=datetime.datetime.now()
        )
        comment.save()

        doc.comments = Comment.objects.filter(doc=doc).count()
        doc.save()

    return JsonResponse({})


def bookmark_post(request):

    if request.method == 'POST':
        data = json.load(request)
        doc = Doc.objects.get(pk=int(data['doc']))

        chosen_bookmarks = request.user.bookmarks.filter(pk=doc.pk)

        if chosen_bookmarks.exists():
            for bookmark in chosen_bookmarks:
                request.user.bookmarks.remove(bookmark)
        else:
            bookmarks = request.user.bookmarks
            bookmarks.set(list(bookmarks.all()) + [doc])

    return JsonResponse({})


def delete_comment(request):

    if request.method == 'POST':
        data = json.load(request)

        Comment.objects.get(pk=data['comment']).delete()
        doc = Doc.objects.get(pk=data['doc'])
        doc.comments -= 1
        doc.save()

    return JsonResponse({})
