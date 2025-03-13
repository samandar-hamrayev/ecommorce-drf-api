from rest_framework import serializers
from .models import User, EmailVerification
import random
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'gender', 'avatar', 'born_date', 'full_name',
            'is_staff', 'is_superuser', 'is_active', 'created', 'updated'
        ]
        read_only_fields = ['full_name', 'email', 'id', 'created', 'updated']

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
        if not verification.is_valid() or verification.code != confirmation_code:
            raise serializers.ValidationError("Invalid or expired confirmation code")

        user.is_active = True
        user.save()
        verification.delete()
        return data