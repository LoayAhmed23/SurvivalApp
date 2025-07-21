from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404


from user.permissions import IsAdminUser
from user.serializers import (
    UserSerializer,
    CreateUserSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer,
    AdminUserSerializer
)


User = get_user_model()


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user profile"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class ChangePasswordView(APIView):
    """Change user password"""

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {'message': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """Logout user by blacklisting the refresh token"""

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetRequestView(APIView):
    """Send reset password url to user's email"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])

        token = PasswordResetTokenGenerator().make_token(user)
        reset_url = request.build_absolute_uri(
            reverse('user:password-reset-confirm')
            + f'?email={user.email}&token={token}'
        )

        subject = 'Your Password Reset Link'
        message = (
            f'{reset_url}\n\n'+'This is the rest password link'
        )
        send_mail(subject, message, None, [user.email])

        return Response(
            {'message': 'Password reset link sent.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    """Changes the user's password"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = SetNewPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': 'Password has been reset successfully.'},
            status=status.HTTP_200_OK
        )


class UserAdminViewSet(viewsets.ModelViewSet):
    """Admin view to manage users"""
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        return AdminUserSerializer
