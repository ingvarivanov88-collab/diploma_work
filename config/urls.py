from django.contrib import admin
from django.urls import path
from backend.views import ProductListView, RegisterView, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/', ProductListView.as_view(), name='product-list'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
]