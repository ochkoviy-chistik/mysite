from accounts import views
from django.urls import path
from django.contrib.auth.views import LogoutView, \
    PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView


urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.sign_up, name='sign_up'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('reset/', views.StyledPasswordResetView.as_view(), name='password_reset'),
    path('reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
