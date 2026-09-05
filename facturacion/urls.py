from django.urls import path

from . import views

app_name = "facturacion"

urlpatterns = [
    path("", views.FacturaListView.as_view(), name="lista"),
    path("nueva/", views.factura_crear, name="crear"),
    path("<int:pk>/", views.FacturaDetailView.as_view(), name="detalle"),
    path("<int:pk>/emitir/", views.factura_emitir, name="emitir"),
    path("<int:pk>/pagar/", views.factura_pagar, name="pagar"),
    path("<int:pk>/nota/", views.factura_nota, name="nota"),
]
