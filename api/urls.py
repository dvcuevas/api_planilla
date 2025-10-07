from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlanillaViewSet, TarifaViewSet, IngresoViewSet,
    EgresoViewSet, ControlBoletoViewSet
)

# Crear router para los ViewSets
router = DefaultRouter()
router.register(r'planillas', PlanillaViewSet, basename='planilla')
router.register(r'tarifas', TarifaViewSet, basename='tarifa')
router.register(r'ingresos', IngresoViewSet, basename='ingreso')
router.register(r'egresos', EgresoViewSet, basename='egreso')
router.register(r'control-boletos', ControlBoletoViewSet, basename='control-boleto')

urlpatterns = [
    path('', include(router.urls)),
]
