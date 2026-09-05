from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from core.mixins import EmpresaFormMixin, EmpresaQuerysetMixin

from .forms import BodegaForm, ProductoForm
from .models import Bodega, MovimientoInventario, Producto, StockPorBodega


class ProductoListView(EmpresaQuerysetMixin, ListView):
    model = Producto
    template_name = "productos/producto_list.html"
    context_object_name = "productos"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q) | qs.filter(codigo__icontains=q)
        return qs.order_by("nombre")


class ProductoCreateView(EmpresaFormMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/producto_form.html"
    success_url = reverse_lazy("productos:lista")


class ProductoUpdateView(EmpresaQuerysetMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/producto_form.html"
    success_url = reverse_lazy("productos:lista")


class MovimientoInventarioListView(EmpresaQuerysetMixin, ListView):
    model = MovimientoInventario
    template_name = "productos/movimiento_list.html"
    context_object_name = "movimientos"
    paginate_by = 30


class BodegaListView(EmpresaQuerysetMixin, ListView):
    model = Bodega
    template_name = "productos/bodega_list.html"
    context_object_name = "bodegas"

    def get_queryset(self):
        return super().get_queryset().order_by("nombre")


class BodegaCreateView(EmpresaFormMixin, CreateView):
    model = Bodega
    form_class = BodegaForm
    template_name = "productos/bodega_form.html"
    success_url = reverse_lazy("productos:bodegas")


class BodegaUpdateView(EmpresaQuerysetMixin, UpdateView):
    model = Bodega
    form_class = BodegaForm
    template_name = "productos/bodega_form.html"
    success_url = reverse_lazy("productos:bodegas")


class StockPorBodegaListView(EmpresaQuerysetMixin, ListView):
    """Reporte de existencias de cada producto desglosado por bodega (HU-14)."""

    model = StockPorBodega
    template_name = "productos/stock_por_bodega.html"
    context_object_name = "filas"

    def get_queryset(self):
        return (
            StockPorBodega.objects.filter(producto__empresa=self.request.empresa)
            .select_related("producto", "bodega")
            .order_by("producto__nombre", "bodega__nombre")
        )
