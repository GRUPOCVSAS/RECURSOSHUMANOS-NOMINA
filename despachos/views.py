from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .models import Despacho, Transportista, Vehiculo, SeguimientoDespacho
from .forms import (
    DespachoForm, TransportistaForm, VehiculoForm,
    SeguimientoForm, FiltroDespachoForm
)


@login_required
def dashboard(request):
    hoy = timezone.now().date()
    total = Despacho.objects.count()
    pendientes = Despacho.objects.filter(estado='pendiente').count()
    en_transito = Despacho.objects.filter(estado='en_transito').count()
    entregados_hoy = Despacho.objects.filter(estado='entregado', fecha_despacho=hoy).count()
    ultimos = Despacho.objects.select_related('transportista', 'vehiculo')[:10]
    por_estado = Despacho.objects.values('estado').annotate(total=Count('id'))
    context = {
        'total': total,
        'pendientes': pendientes,
        'en_transito': en_transito,
        'entregados_hoy': entregados_hoy,
        'ultimos': ultimos,
        'por_estado': {item['estado']: item['total'] for item in por_estado},
    }
    return render(request, 'despachos/dashboard.html', context)


@login_required
def lista_despachos(request):
    form = FiltroDespachoForm(request.GET or None)
    qs = Despacho.objects.select_related('transportista', 'vehiculo', 'creado_por')
    if form.is_valid():
        if form.cleaned_data.get('estado'):
            qs = qs.filter(estado=form.cleaned_data['estado'])
        if form.cleaned_data.get('buscar'):
            q = form.cleaned_data['buscar']
            qs = qs.filter(
                Q(numero__icontains=q) |
                Q(destino__icontains=q) |
                Q(destinatario__icontains=q) |
                Q(origen__icontains=q)
            )
        if form.cleaned_data.get('fecha_desde'):
            qs = qs.filter(fecha_despacho__gte=form.cleaned_data['fecha_desde'])
        if form.cleaned_data.get('fecha_hasta'):
            qs = qs.filter(fecha_despacho__lte=form.cleaned_data['fecha_hasta'])
    return render(request, 'despachos/lista.html', {'despachos': qs, 'form': form})


@login_required
def detalle_despacho(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    seguimiento_form = SeguimientoForm()
    if request.method == 'POST':
        seguimiento_form = SeguimientoForm(request.POST)
        if seguimiento_form.is_valid():
            seg = seguimiento_form.save(commit=False)
            seg.despacho = despacho
            seg.registrado_por = request.user
            seg.save()
            despacho.estado = seg.estado
            despacho.save()
            messages.success(request, 'Seguimiento registrado correctamente.')
            return redirect('despachos:detalle', pk=pk)
    return render(request, 'despachos/detalle.html', {
        'despacho': despacho,
        'seguimiento_form': seguimiento_form,
    })


@login_required
def crear_despacho(request):
    if request.method == 'POST':
        form = DespachoForm(request.POST)
        if form.is_valid():
            despacho = form.save(commit=False)
            despacho.creado_por = request.user
            despacho.save()
            SeguimientoDespacho.objects.create(
                despacho=despacho,
                estado=despacho.estado,
                observacion='Despacho creado',
                registrado_por=request.user,
            )
            messages.success(request, f'Despacho {despacho.numero} creado exitosamente.')
            return redirect('despachos:detalle', pk=despacho.pk)
    else:
        form = DespachoForm()
    return render(request, 'despachos/form.html', {'form': form, 'titulo': 'Nuevo Despacho'})


@login_required
def editar_despacho(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    if request.method == 'POST':
        form = DespachoForm(request.POST, instance=despacho)
        if form.is_valid():
            form.save()
            messages.success(request, 'Despacho actualizado correctamente.')
            return redirect('despachos:detalle', pk=pk)
    else:
        form = DespachoForm(instance=despacho)
    return render(request, 'despachos/form.html', {'form': form, 'titulo': 'Editar Despacho', 'despacho': despacho})


@login_required
def eliminar_despacho(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    if request.method == 'POST':
        numero = despacho.numero
        despacho.delete()
        messages.success(request, f'Despacho {numero} eliminado.')
        return redirect('despachos:lista')
    return render(request, 'despachos/confirmar_eliminar.html', {'despacho': despacho})


# --- Transportistas ---

@login_required
def lista_transportistas(request):
    transportistas = Transportista.objects.annotate(total_despachos=Count('despachos'))
    return render(request, 'despachos/transportistas/lista.html', {'transportistas': transportistas})


@login_required
def crear_transportista(request):
    if request.method == 'POST':
        form = TransportistaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transportista creado exitosamente.')
            return redirect('despachos:transportistas')
    else:
        form = TransportistaForm()
    return render(request, 'despachos/transportistas/form.html', {'form': form, 'titulo': 'Nuevo Transportista'})


@login_required
def editar_transportista(request, pk):
    transportista = get_object_or_404(Transportista, pk=pk)
    if request.method == 'POST':
        form = TransportistaForm(request.POST, instance=transportista)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transportista actualizado.')
            return redirect('despachos:transportistas')
    else:
        form = TransportistaForm(instance=transportista)
    return render(request, 'despachos/transportistas/form.html', {'form': form, 'titulo': 'Editar Transportista'})


# --- Vehículos ---

@login_required
def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.select_related('transportista').annotate(total_despachos=Count('despachos'))
    return render(request, 'despachos/vehiculos/lista.html', {'vehiculos': vehiculos})


@login_required
def crear_vehiculo(request):
    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehículo creado exitosamente.')
            return redirect('despachos:vehiculos')
    else:
        form = VehiculoForm()
    return render(request, 'despachos/vehiculos/form.html', {'form': form, 'titulo': 'Nuevo Vehículo'})


@login_required
def editar_vehiculo(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)
    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehículo actualizado.')
            return redirect('despachos:vehiculos')
    else:
        form = VehiculoForm(instance=vehiculo)
    return render(request, 'despachos/vehiculos/form.html', {'form': form, 'titulo': 'Editar Vehículo'})
