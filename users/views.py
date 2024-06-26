from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views import generic
from rest_framework.views import APIView
from . import serializers
from . import models
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


User = get_user_model()


class SignUpView(APIView):
    serializer_class = serializers.SignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email').lower()
        full_name = serializer.validated_data.get('first_name') + " " + serializer.validated_data.get('last_name')
        user = serializer.save()
        user_type = serializer.validated_data.get('user_type')
        user.user_type = user_type
        user.username = email.split('@')[0]
        user.save()
        return Response({'status': 'True', 'message': 'user created successfully.', 'data': serializer.data})



class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        user_email = self.request.data.get('email').lower()
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_active:
            return Response({'error': 'User not active. Contact admin to activate your account.'}, status=status.HTTP_400_BAD_REQUEST)
        self.request.data['email'] = user_email
        return super().post(request, *args, **kwargs)


class GetUserView(APIView):
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(request.user)
        return Response({"status": True, "message": "user retrieved successfully", "data": serializer.data})
