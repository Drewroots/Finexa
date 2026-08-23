class EmpresaActualMiddleware:
    """Expone request.empresa como atajo del tenant del usuario autenticado."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.empresa = None
        if request.user.is_authenticated:
            request.empresa = getattr(request.user, "empresa", None)
        return self.get_response(request)
