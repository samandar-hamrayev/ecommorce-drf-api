from rest_framework import serializers
from .models import User
import random
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'gender', 'avatar', 'born_date', 'full_name', 'created', 'updated']
        read_only_fields = ['full_name', "email", "id"]

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.born_date = validated_data.get("born_date", instance.born_date)
        instance.save()
        return instance
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        code = random.randint(100000, 999999)
        user.confirmation_code = code
        user.save()

        send_mail(
            'Email Confirmation',
            f'Your confirmation code is: {code}',
            EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        return user


class UserConfirmEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    confirmation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        confirmation_code = data.get('confirmation_code')
        user = User.objects.filter(email=email).first()

        if not user:
            raise serializers.ValidationError("User with this email does not exist")
        if str(user.confirmation_code) != confirmation_code:
            raise serializers.ValidationError("Invalid confirmation code")

        user.is_active = True
        user.confirmation_code = None
        user.save()
        return data