from django.urls import path

from . import views

app_name = "nomina"

urlpatterns = [
    path("", views.EmpleadoListView.as_view(), name="empleados"),
    path("nuevo/", views.EmpleadoCreateView.as_view(), name="empleado_crear"),
    path("<int:pk>/", views.EmpleadoDetailView.as_view(), name="empleado_detalle"),
    path("<int:pk>/editar/", views.EmpleadoUpdateView.as_view(), name="empleado_editar"),
    path("<int:pk>/liquidar/", views.liquidar, name="liquidar"),
    path("liquidacion/<int:pk>/", views.LiquidacionDetailView.as_view(), name="liquidacion_detalle"),
]
