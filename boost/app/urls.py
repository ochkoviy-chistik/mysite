from django.contrib.auth.decorators import login_required
from . import views
from .ajax_queryes import ajax_notes
from django.urls import path


urlpatterns = [
    path('', views.index, name='main'),

    path('docs/', views.docs_page, name='docs'),
    path('id<int:pk>/', login_required(views.profile, login_url='/login/'), name='profile'),
    path('id<int:pk>/edit/', login_required(views.profile_edit, login_url='/login/'), name='edit'),
    path('bookmarks/', login_required(views.bookmarks, login_url='/login/'), name='bookmarks'),

    path('document<int:pk>/', login_required(views.doc_page, login_url='/login/'), name='doc_page'),
    path('document<int:pk>/edit/', login_required(views.doc_page_edit, login_url='/login/'), name='doc_page'),
    path('create/', login_required(views.create_docs, login_url='/login/'), name='create_docs'),

    path('document<int:pk>/getdata', ajax_notes.get_data, name='data_get_ajax'),
    path('documents/postlikedata', ajax_notes.like_post, name='like_post_ajax'),
    path('documents/postdislikedata', ajax_notes.dislike_post, name='dislike_post_ajax'),
    path('documents/postcommentdata', ajax_notes.comment_post, name='comment_post_ajax'),
    path('documents/postbookmarkdata', ajax_notes.bookmark_post, name='bookmark_post_ajax'),
    path('documents/deletecomment', ajax_notes.delete_comment, name='delete_comment_ajax'),
]
