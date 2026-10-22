from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from backend.views import ProductListView, RegisterView, LoginView, CartView, OrderView


def profile_view(request):
    return HttpResponse(
        "Вы успешно вошли в систему. Перейдите на <a href='/api/products/'>список товаров</a> или в <a href='/api/cart/'>корзину</a>.")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    # Добавляем страницу, на которую перенаправляет после входа
    path('accounts/profile/', profile_view, name='profile'),

    path('api/products/', ProductListView.as_view(), name='product-list'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/cart/', CartView.as_view(), name='cart'),
    path('api/orders/', OrderView.as_view(), name='orders'),
]