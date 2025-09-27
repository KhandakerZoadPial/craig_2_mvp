from django.urls import path
from . import views

urlpatterns = [
    path('<str:service_name>/<path:service_path>', views.dynamic_proxy_handler),
]