from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='dashboard:index', permanent=False)),
    path('', include('core.urls')),
    path('clientes/', include('clientes.urls')),
    path('productos/', include('productos.urls')),
    path('contabilidad/', include('contabilidad.urls')),
    path('facturas/', include('facturacion.urls')),
    path('dashboard/', include('dashboard.urls')),
]
