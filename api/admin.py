from django.contrib import admin
from .models import Planilla, Tarifa, Ingreso, Egreso, ControlBoleto


@admin.register(Planilla)
class PlanillaAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'fecha_creacion', 'nombre_archivo']
    list_filter = ['status', 'fecha_creacion']
    search_fields = ['nombre_archivo', 'error_procesamiento']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'tamaño_archivo']
    
    fieldsets = (
        ('Información Principal', {
            'fields': ('imagen', 'status', 'nombre_archivo', 'tamaño_archivo')
        }),
        ('Procesamiento', {
            'fields': ('datos_extraidos', 'error_procesamiento')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ['concepto', 'precio', 'cantidad', 'subtotal', 'planilla']
    list_filter = ['planilla', 'fecha_creacion']
    search_fields = ['concepto']
    readonly_fields = ['fecha_creacion']


@admin.register(Ingreso)
class IngresoAdmin(admin.ModelAdmin):
    list_display = ['concepto', 'monto', 'planilla', 'fecha_creacion']
    list_filter = ['planilla', 'fecha_creacion']
    search_fields = ['concepto', 'observaciones']
    readonly_fields = ['fecha_creacion']


@admin.register(Egreso)
class EgresoAdmin(admin.ModelAdmin):
    list_display = ['concepto', 'monto', 'planilla', 'fecha_creacion']
    list_filter = ['planilla', 'fecha_creacion']
    search_fields = ['concepto', 'observaciones']
    readonly_fields = ['fecha_creacion']


@admin.register(ControlBoleto)
class ControlBoletoAdmin(admin.ModelAdmin):
    list_display = ['numero_inicial', 'numero_final', 'cantidad_vendidos', 'boletos_faltantes', 'planilla']
    list_filter = ['planilla', 'fecha_creacion']
    search_fields = ['numero_inicial', 'numero_final']
    readonly_fields = ['total_boletos', 'boletos_faltantes', 'fecha_creacion']
