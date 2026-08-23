from django.urls import path

from . import views

app_name = "clientes"

urlpatterns = [
    path("", views.TerceroListView.as_view(), name="lista"),
    path("nuevo/", views.TerceroCreateView.as_view(), name="crear"),
    path("<int:pk>/editar/", views.TerceroUpdateView.as_view(), name="editar"),
]
