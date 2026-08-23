from django.contrib.auth.mixins import LoginRequiredMixin


class EmpresaQuerysetMixin(LoginRequiredMixin):
    """Restringe cualquier ListView/DetailView/UpdateView a los datos del tenant actual."""

    def get_queryset(self):
        return super().get_queryset().filter(empresa=self.request.empresa)


class EmpresaFormMixin(LoginRequiredMixin):
    """Asigna automáticamente la empresa del usuario al crear un registro."""

    def form_valid(self, form):
        form.instance.empresa = self.request.empresa
        return super().form_valid(form)
