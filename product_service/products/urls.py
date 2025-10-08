from django.urls import path
from .views import product_list_create_view, product_detail_view

urlpatterns = [
    path('products/', product_list_create_view, name='product-list-create'),
    path('products/<int:pk>/', product_detail_view, name='product-detail'),
]