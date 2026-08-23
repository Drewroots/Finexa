from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .services import asistente_responder, calcular_kpis


@login_required
def index(request):
    kpis = calcular_kpis(request.empresa)
    return render(request, "dashboard/index.html", {"kpis": kpis})


@login_required
@require_POST
def asistente(request):
    pregunta = request.POST.get("pregunta", "")
    respuesta = asistente_responder(request.empresa, pregunta)
    return JsonResponse({"respuesta": respuesta})
