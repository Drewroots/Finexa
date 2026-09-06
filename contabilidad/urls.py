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
    path("conciliacion/", views.conciliacion_lista, name="conciliacion"),
    path("conciliacion/<int:pk>/marcar/", views.conciliacion_marcar_manual, name="conciliacion_marcar"),
    path("puc/", views.puc_referencia, name="puc_referencia"),
    path("puc/descargar/", views.puc_descargar_csv, name="puc_descargar"),
    path("puc/auxiliar/nuevo/<str:clase>/", views.puc_auxiliar_crear, name="puc_auxiliar_crear"),
    path("puc/auxiliar/<int:pk>/editar/", views.puc_auxiliar_editar, name="puc_auxiliar_editar"),
]
