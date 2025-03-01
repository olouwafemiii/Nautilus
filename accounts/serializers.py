from django.contrib.auth import authenticate
from django.conf import settings
from django.contrib.auth.tokens import (PasswordResetTokenGenerator, default_token_generator,)
from django.core.validators import validate_email
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User
from .utils import send_reset_password_email, generate_hex_id

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "is_active"
        ]

        extra_kwargs = {
            "id": {"read_only": True, "help_text": "User unique identifier"},
            "email": {"required": True, "help_text": "Email address"},
            "first_name": {"required": True, "help_text": "First name"},
            "last_name": {"required": True, "help_text": "Last name"},
            "date_joined": {"read_only": True, "help_text": "Date joined"},
            "last_login": {"read_only": True, "help_text": "Last login"}
        }

class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "is_active",
        ]

        extra_kwargs = {
            "id": {"read_only": True, "help_text": "User unique identifier"},
            "email": {"required": True, "help_text": "Email address"},
            "first_name": {"required": True, "help_text": "First name"},
            "last_name": {"required": True, "help_text": "Last name"},
            "date_joined": {"read_only": True, "help_text": "Date joined"},
            "last_login": {"read_only": True, "help_text": "Last login"},
            "is_active": {"read_only": True, "help_text": "Active"},
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False, style={'input_type': 'password'}, help_text="Password"
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', generate_hex_id(9))
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        user = User.objects.create_user(**validated_data, password=password)
        user.is_active = True
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "is_active",
        ]
        read_only_fields = ["email", "is_active", "last_login", "date_joined"]

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance


class UserRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name'
        )

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email"]

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not user:
            raise AuthenticationFailed("Invalid credentials. Please try again.")
        tokens = user.tokens()
        return {
            "access_token": str(tokens.get("access")),
            "refresh_token": str(tokens.get("refresh"))
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uuid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = settings.FRONTEND_URL
            abs_link = f"{current_site}/change-password?token={token}&uuid={uuid}"
            send_reset_password_email(
                email=user.email,
                full_name=user.get_full_name(),
                reset_password_link=abs_link,
            )
        return attrs


class CheckTokenSerializer(serializers.Serializer):
    uuid = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)

    def validate(self, attrs):
        uuid = attrs.get("uuid")
        token = attrs.get("token")

        try:
            user_id = force_str(urlsafe_base64_decode(uuid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link.")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid reset link.")

        return user


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, help_text="Password", write_only=True)
    confirm_password = serializers.CharField(
        max_length=100, min_length=6, write_only=True
    )
    uuid = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        uuid = attrs.get("uuid")
        token = attrs.get("token")

        # Check if passwords match
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))

        try:
            user_id = force_str(urlsafe_base64_decode(uuid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid uuid.")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid token.")

        if user.check_password(password):
            raise serializers.ValidationError(
                "New password must be different from the old one."
            )
        user.is_active = True
        user.set_password(password)
        user.full_clean()
        user.save()
        return user

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100, min_length=6)
    new_password = serializers.CharField(max_length=100, min_length=6)
    confirm_password = serializers.CharField(max_length=100, min_length=6)

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")
        user = self.context["request"].user

        if not user.check_password(old_password):
            raise serializers.ValidationError("Incorrect old password.")
        if new_password == old_password:
            raise serializers.ValidationError("New password must be different.")
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        user.set_password(new_password)
        user.full_clean()
        user.save()
        return user

class ChangeEmailSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6)
    new_email = serializers.CharField(max_length=100, min_length=6)

    def validate(self, attrs):
        password = attrs.get("password")
        new_email = attrs.get("new_email")
        user = self.context["request"].user

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
        if new_email == user.email:
            raise serializers.ValidationError("New email must be different.")
        try:
            validate_email(new_email)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        user.email = new_email
        user.full_clean()
        user.save()
        return user


class ValidateEmailSerializer(serializers.Serializer):
    uuid = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)

    def validate(self, attrs):
        uuid = attrs.get("uuid")
        token = attrs.get("token")
        try:
            user_id = force_str(urlsafe_base64_decode(uuid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid activation link.")

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid activation link.")

        if user.is_verified:
            raise serializers.ValidationError("User is already verified.")

        user.is_verified = True
        user.save()
        return user
