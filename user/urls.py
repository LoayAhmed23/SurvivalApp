from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenObtainPairView,
)
from rest_framework.routers import DefaultRouter
from user import views


app_name = 'user'

router = DefaultRouter()
router.register('admin/users', views.UserAdminViewSet, basename='admin-user')


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
    path('', include(router.urls)),
]
