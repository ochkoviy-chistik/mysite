from accounts import views
from django.urls import path
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.sign_up, name='sign_up'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]
