from django.urls import path

from . import views

app_name = "contabilidad"

urlpatterns = [
    path("libro-diario/", views.TransaccionListView.as_view(), name="libro_diario"),
    path("balance/", views.BalanceComprobacionView.as_view(), name="balance"),
]
