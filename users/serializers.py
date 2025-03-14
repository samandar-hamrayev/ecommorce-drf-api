from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings

from . import utils
from .models import User, EmailVerification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'gender', 'avatar', 'born_date', 'full_name',
            'is_staff', 'is_superuser', 'is_active', 'created', 'updated'
        ]
        read_only_fields = ['id', 'email', 'full_name', 'created', 'updated']

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        if not request_user.is_superuser and not request_user.is_staff:
            validated_data.pop('is_staff', None)
            validated_data.pop('is_superuser', None)
            validated_data.pop('is_active', None)
        return super().update(instance, validated_data)


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        verification = EmailVerification.objects.create(user=user)
        send_mail(
            'Email Confirmation',
            f'Your confirmation code is: {verification.code}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return user

class UserConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        code = data['confirmation_code']
        try:
            user = User.objects.get(email=email)
            verification = user.email_verification
        except (User.DoesNotExist, EmailVerification.DoesNotExist):
            raise serializers.ValidationError("Invalid email or code")
        if not verification.is_valid() or verification.code != code:
            raise serializers.ValidationError("Invalid or expired code")
        return data

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.is_active = True
        user.save()
        user.email_verification.is_used = True
        user.email_verification.save()
        return user

class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email not found")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        verification, _ = EmailVerification.objects.get_or_create(user=user)
        verification.code = str(utils.generate_verification_code())
        verification.expires = utils.get_expiry_time()
        verification.is_used = False
        verification.save()
        send_mail(
            "Password Reset Code",
            f"Code to reset your password: {verification.code}",
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
            verification = user.email_verification
        except (User.DoesNotExist, EmailVerification.DoesNotExist):
            raise serializers.ValidationError("Invalid email or code")
        if not verification.is_valid() or verification.code != data['confirmation_code']:
            raise serializers.ValidationError("Invalid or expired code")
        return data

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        user.email_verification.is_used = True
        user.email_verification.save()
        return user