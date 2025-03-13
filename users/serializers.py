from django.conf import settings
from django.contrib.auth.hashers import check_password
from rest_framework import serializers
from .models import User, EmailVerification
import random
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER
from .models import get_expiry_time, generate_verification_code


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'gender', 'avatar', 'born_date', 'full_name',
            'is_staff', 'is_superuser', 'is_active', 'created', 'updated'
        ]
        read_only_fields = ['full_name', 'email', 'id', 'created', 'updated']

    def create(self, validated_data):
        request_user = self.context['request'].user

        if not request_user.is_superuser:
            validated_data.pop('is_staff', None)
            validated_data.pop('is_superuser', None)
            validated_data.pop('is_active', None)

        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        request_user = self.context['request'].user

        admin_only_fields = ['is_staff', 'is_superuser', 'is_active']

        if not request_user.is_staff:
            for field in admin_only_fields:
                validated_data.pop(field, None)

        if validated_data.get('is_superuser', False) and not request_user.is_superuser:
            raise serializers.ValidationError({"is_superuser": "You don't have permission to make yourself superuser."})

        for field in self.Meta.read_only_fields:
            if field in validated_data:
                raise serializers.ValidationError({field: f"You can't modify {field}."})

        if request_user.is_staff and not request_user.is_superuser:
            restricted_fields = ['is_superuser']
            for field in restricted_fields:
                validated_data.pop(field, None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()
        return instance


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        verification = EmailVerification.objects.create(user=user)

        try:
            send_mail(
                'Email Confirmation',
                f'Your confirmation code is: {verification.code}',
                EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
        except Exception as exc:
            user.delete()
            raise serializers.ValidationError(f"Failed to send email: {exc}")
        return user


class UserConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        confirmation_code = data.get('confirmation_code')
        try:
            user = User.objects.get(email=email)
            verification = EmailVerification.objects.get(user=user)
        except (User.DoesNotExist, EmailVerification.DoesNotExist):
            raise serializers.ValidationError("Invalid email or code")
        if verification.is_used or not verification.is_valid() or verification.code != confirmation_code:
            raise serializers.ValidationError("Invalid or expired confirmation code")

        user.is_active = True
        user.save()
        verification.is_used = True
        verification.save()
        return data

class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        request_user = self.context['request'].user
        if not check_password(value, request_user.password):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def update_password(self):
        request_user = self.context['request'].user
        request_user.set_password(self.validated_data['new_password'])
        request_user.save()
        return request_user

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with email not found ")
        return value


    def save(self, **kwargs):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        verification, _ = EmailVerification.objects.get_or_create(user=user)


        verification.code =  generate_verification_code()
        verification.expires = get_expiry_time()
        verification.is_used = False
        verification.save()

        send_mail(
            "Password reset code",
            f"Code to reset your password: {verification.code}",
            EMAIL_HOST_USER,
            [user.email],
            fail_silently=False
        )

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email']
        confirmation_code = data['confirmation_code']

        try:
            user = User.objects.get(email=email)
            verification = EmailVerification.objects.get(user=user)
        except (User.DoesNotExist, EmailVerification.DoesNotExist) as exc:
            raise serializers.ValidationError("Email or code is incorrect")

        if not verification.is_valid():
            raise serializers.ValidationError("The code is invalid or expired")

        if verification.code != confirmation_code:
            raise serializers.ValidationError("The verification code is incorrect.")

        return data

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.save()

        verification = EmailVerification.objects.get(user=user)
        verification.is_used = True
        verification.save()

