from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from core.mixins import EmpresaFormMixin, EmpresaQuerysetMixin

from .forms import TerceroForm
from .models import Tercero


class TerceroListView(EmpresaQuerysetMixin, ListView):
    model = Tercero
    template_name = "clientes/tercero_list.html"
    context_object_name = "terceros"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(razon_social__icontains=q) | qs.filter(numero_documento__icontains=q)
        return qs.order_by("razon_social")


class TerceroCreateView(EmpresaFormMixin, CreateView):
    model = Tercero
    form_class = TerceroForm
    template_name = "clientes/tercero_form.html"
    success_url = reverse_lazy("clientes:lista")


class TerceroUpdateView(EmpresaQuerysetMixin, UpdateView):
    model = Tercero
    form_class = TerceroForm
    template_name = "clientes/tercero_form.html"
    success_url = reverse_lazy("clientes:lista")
