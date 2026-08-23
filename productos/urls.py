from django.urls import path

from . import views

app_name = "productos"

urlpatterns = [
    path("", views.ProductoListView.as_view(), name="lista"),
    path("nuevo/", views.ProductoCreateView.as_view(), name="crear"),
    path("<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="editar"),
    path("movimientos/", views.MovimientoInventarioListView.as_view(), name="movimientos"),
]
