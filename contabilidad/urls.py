from django.urls import path

from . import views

app_name = "contabilidad"

urlpatterns = [
    path("libro-diario/", views.TransaccionListView.as_view(), name="libro_diario"),
    path("balance/", views.BalanceComprobacionView.as_view(), name="balance"),
    path("estado-resultados/", views.estado_resultados, name="estado_resultados"),
    path("balance-general/", views.balance_general, name="balance_general"),
    path("cierre/", views.cierre_mensual, name="cierre"),
    path("cierre/<int:pk>/marcar/", views.cierre_marcar_tarea, name="cierre_marcar"),
]
