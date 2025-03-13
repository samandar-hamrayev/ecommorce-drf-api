from django.urls import path
from .views import (
    RegisterAPIView,
    ConfirmEmailAPIView,
    LogoutAPIView,
    ProfileAPIView,
    UserListView,
    UserDetailView,
    UpdatePasswordView,
    ResetPassworView,
    ResetPasswordConfirmView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('confirm-email/', ConfirmEmailAPIView.as_view(), name='confirm-email'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('update-password/', UpdatePasswordView.as_view(), name='update-password'),
    path('reset-password/', ResetPassworView.as_view(), name='reset-password'),
    path('reset-password-confirm/', ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
    # admins
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>', UserDetailView.as_view(), name='user-detail'),
]