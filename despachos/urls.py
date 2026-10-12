from django.urls import path
from . import views

app_name = 'despachos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('despachos/', views.lista_despachos, name='lista'),
    path('despachos/nuevo/', views.crear_despacho, name='crear'),
    path('despachos/<int:pk>/', views.detalle_despacho, name='detalle'),
    path('despachos/<int:pk>/editar/', views.editar_despacho, name='editar'),
    path('despachos/<int:pk>/eliminar/', views.eliminar_despacho, name='eliminar'),
    path('transportistas/', views.lista_transportistas, name='transportistas'),
    path('transportistas/nuevo/', views.crear_transportista, name='crear_transportista'),
    path('transportistas/<int:pk>/editar/', views.editar_transportista, name='editar_transportista'),
    path('vehiculos/', views.lista_vehiculos, name='vehiculos'),
    path('vehiculos/nuevo/', views.crear_vehiculo, name='crear_vehiculo'),
    path('vehiculos/<int:pk>/editar/', views.editar_vehiculo, name='editar_vehiculo'),
    path('importar/', views.importar_excel, name='importar'),
]
