from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from .models import Product
from .serializers import ProductSerializer, UserSerializer


# 1. Список всех товаров (доступно всем)
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).prefetch_related('parameters')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


# 2. Регистрация пользователя
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


# 3. Авторизация (логин)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({"message": "Успешный вход", "username": user.username})
        else:
            return Response({"error": "Неверный логин или пароль"}, status=status.HTTP_401_UNAUTHORIZED)