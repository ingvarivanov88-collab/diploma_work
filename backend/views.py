from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from .models import Product, Cart, CartItem, Order, OrderItem, Contact
from .serializers import ProductSerializer, UserSerializer
from .tasks import send_order_confirmation_task, send_invoice_to_admin_task


# 1. Список всех товаров
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True).prefetch_related('parameters')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


# 2. Регистрация
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


# 3. Авторизация
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


# 4. Корзина
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()
        data = [{"id": item.id, "product": item.product.name, "quantity": item.quantity} for item in items]
        return Response({"cart_items": data})

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Товар добавлен в корзину"}, status=status.HTTP_201_CREATED)


# 5. Заказы
class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        contact_id = request.data.get('contact_id')
        try:
            contact = Contact.objects.get(id=contact_id, user=request.user)
        except Contact.DoesNotExist:
            return Response({"error": "Адрес не найден"}, status=status.HTTP_404_NOT_FOUND)

        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, status='new')

        # Собираем данные для фоновых задач (чтобы не передавать объекты БД)
        items_data = []
        for item in cart.items.all():
            items_data.append({
                "product": item.product.name,
                "quantity": item.quantity,
                "price": str(item.product.price)
            })
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

        # --- ЗАПУСКАЕМ ФОНОВЫЕ ЗАДАЧИ ---
        user_email = request.user.email
        if user_email:
            send_order_confirmation_task.delay(user_email, order.id, items_data)

        send_invoice_to_admin_task.delay(order.id, items_data, request.user.username)

        # Очищаем корзину
        cart.items.all().delete()

        return Response({"message": "Заказ оформлен", "order_id": order.id}, status=status.HTTP_201_CREATED)

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        data = []
        for order in orders:
            items = [{"product": i.product.name, "quantity": i.quantity} for i in order.items.all()]
            data.append({"id": order.id, "status": order.status, "created_at": order.created_at, "items": items})
        return Response(data)