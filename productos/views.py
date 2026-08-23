from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from core.mixins import EmpresaFormMixin, EmpresaQuerysetMixin

from .forms import ProductoForm
from .models import MovimientoInventario, Producto


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
