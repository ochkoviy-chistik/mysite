from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('documents/', views.documents, name='documents'),
    path('is-authorize/', views.is_authorize, name='is_authorize'),
    path('user-info/', views.get_user_info, name='user_info'),
    path('logout/', views.logout, name='logout'),
    path('login/', views.login, name='login'),
]
