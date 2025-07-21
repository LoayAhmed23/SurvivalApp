from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user objects"""

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'is_active')
        read_only_fields = ('id', 'is_active')


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for creating user objects"""
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'password_confirm')

    def validate(self, attrs):
        """Validate that passwords match"""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)

        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        
        return attrs

    def create(self, validated_data):
        """Create and return a new user"""
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, min_length=8)

    def validate(self, attrs):
        """Validate that new passwords match"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError('New passwords do not match')

        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting reset password url"""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate that user exists"""
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No active user exists with this email")

        return value


class SetNewPasswordSerializer(serializers.Serializer):
    """Serializer for reseting password"""
    email = serializers.EmailField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField(min_length=8)

    def validate(self, attrs):
        """Validate reset token and that new passwords match"""
        user = User.objects.get(email=attrs['email'], is_active=True)

        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid or expired reset token")

        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError('New passwords do not match')

        attrs['user'] = user
        return attrs

    def save(self):
        """Save the new password"""
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'is_active', 'is_staff', 'is_superuser']
        read_only_fields = ['id', 'email']
