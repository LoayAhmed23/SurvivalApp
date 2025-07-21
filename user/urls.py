from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)
from user import views

app_name = 'user'

urlpatterns = [
    path('register/', views.CreateUserView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.UserProfileView.as_view(), name='profile'),

    path(
         'change-password/',
         views.ChangePasswordView.as_view(),
         name='change_password'
    ),
    path(
         'password-reset/',
         views.PasswordResetRequestView.as_view(),
         name='password-reset-request'
    ),
    path(
         'password-reset-confirm/',
         views.PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'
    ),

]
