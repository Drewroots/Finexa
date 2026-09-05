from django.urls import path

from . import views

app_name = "productos"

urlpatterns = [
    path("", views.ProductoListView.as_view(), name="lista"),
    path("nuevo/", views.ProductoCreateView.as_view(), name="crear"),
    path("<int:pk>/editar/", views.ProductoUpdateView.as_view(), name="editar"),
    path("movimientos/", views.MovimientoInventarioListView.as_view(), name="movimientos"),
    path("bodegas/", views.BodegaListView.as_view(), name="bodegas"),
    path("bodegas/nueva/", views.BodegaCreateView.as_view(), name="bodega_crear"),
    path("bodegas/<int:pk>/editar/", views.BodegaUpdateView.as_view(), name="bodega_editar"),
    path("stock-por-bodega/", views.StockPorBodegaListView.as_view(), name="stock_por_bodega"),
]
