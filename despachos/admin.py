from django.contrib import admin
from .models import Despacho, Transportista, Vehiculo, SeguimientoDespacho


@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'fecha_despacho', 'origen', 'destino', 'destinatario', 'estado', 'transportista']
    list_filter = ['estado', 'fecha_despacho']
    search_fields = ['numero', 'destino', 'destinatario']
    date_hierarchy = 'fecha_despacho'


@admin.register(Transportista)
class TransportistaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'identificacion', 'telefono', 'email', 'activo']
    search_fields = ['nombre', 'identificacion']


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'marca', 'modelo', 'capacidad_kg', 'transportista', 'activo']


@admin.register(SeguimientoDespacho)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ['despacho', 'estado', 'registrado_por', 'fecha']
    list_filter = ['estado']
