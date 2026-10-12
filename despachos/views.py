from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from decimal import Decimal
import pandas as pd

from .models import Despacho, Transportista, Vehiculo, SeguimientoDespacho
from .forms import (
    DespachoForm, TransportistaForm, VehiculoForm,
    SeguimientoForm, FiltroDespachoForm, ImportarExcelForm,
)


@login_required
def dashboard(request):
    hoy = timezone.now().date()
    totales = Despacho.objects.aggregate(
        total_ventas=Sum('valor_venta'),
        total_saldo=Sum('saldo'),
        count=Count('id'),
    )
    total_ventas = totales['total_ventas'] or 0
    total_saldo = totales['total_saldo'] or 0
    total_cobrado = total_ventas - total_saldo
    pct_cobrado = (total_cobrado / total_ventas * 100) if total_ventas else 0

    pendientes = Despacho.objects.filter(estado='pendiente').count()
    en_transito = Despacho.objects.filter(estado='en_transito').count()
    entregados_hoy = Despacho.objects.filter(estado='entregado', fecha_despacho=hoy).count()

    # Top vendedores
    top_vendedores = (
        Despacho.objects
        .exclude(vendedor1='')
        .values('vendedor1')
        .annotate(total=Sum('valor_venta'), cantidad=Count('id'))
        .order_by('-total')[:10]
    )

    # Top zonas
    top_zonas = (
        Despacho.objects
        .exclude(zona='')
        .values('zona')
        .annotate(total=Sum('valor_venta'), cantidad=Count('id'))
        .order_by('-total')[:8]
    )

    # Top mensajeros
    top_mensajeros = (
        Despacho.objects
        .filter(transportista__isnull=False)
        .values('transportista__nombre')
        .annotate(total=Sum('valor_venta'), cantidad=Count('id'))
        .order_by('-total')[:8]
    )

    # Ventas por día
    ventas_por_dia = (
        Despacho.objects
        .values('fecha_despacho')
        .annotate(total=Sum('valor_venta'), cantidad=Count('id'))
        .order_by('fecha_despacho')
    )

    ultimos = Despacho.objects.select_related('transportista')[:10]

    context = {
        'total_ventas': total_ventas,
        'total_saldo': total_saldo,
        'total_cobrado': total_cobrado,
        'pct_cobrado': pct_cobrado,
        'total_registros': totales['count'] or 0,
        'pendientes': pendientes,
        'en_transito': en_transito,
        'entregados_hoy': entregados_hoy,
        'top_vendedores': top_vendedores,
        'top_zonas': top_zonas,
        'top_mensajeros': top_mensajeros,
        'ventas_por_dia': list(ventas_por_dia),
        'ultimos': ultimos,
    }
    return render(request, 'despachos/dashboard.html', context)


@login_required
def lista_despachos(request):
    form = FiltroDespachoForm(request.GET or None)
    qs = Despacho.objects.select_related('transportista', 'vehiculo', 'creado_por')
    if form.is_valid():
        if form.cleaned_data.get('estado'):
            qs = qs.filter(estado=form.cleaned_data['estado'])
        if form.cleaned_data.get('tipo'):
            qs = qs.filter(tipo=form.cleaned_data['tipo'])
        if form.cleaned_data.get('zona'):
            qs = qs.filter(zona__icontains=form.cleaned_data['zona'])
        if form.cleaned_data.get('mensajero'):
            qs = qs.filter(transportista__nombre__icontains=form.cleaned_data['mensajero'])
        if form.cleaned_data.get('buscar'):
            q = form.cleaned_data['buscar']
            qs = qs.filter(
                Q(numero__icontains=q) |
                Q(destinatario__icontains=q) |
                Q(destino__icontains=q) |
                Q(zona__icontains=q) |
                Q(vendedor1__icontains=q) |
                Q(cedula__icontains=q) |
                Q(celular__icontains=q)
            )
        if form.cleaned_data.get('fecha_desde'):
            qs = qs.filter(fecha_despacho__gte=form.cleaned_data['fecha_desde'])
        if form.cleaned_data.get('fecha_hasta'):
            qs = qs.filter(fecha_despacho__lte=form.cleaned_data['fecha_hasta'])

    totales = qs.aggregate(total_ventas=Sum('valor_venta'), total_saldo=Sum('saldo'))
    return render(request, 'despachos/lista.html', {
        'despachos': qs,
        'form': form,
        'total_ventas': totales['total_ventas'] or 0,
        'total_saldo': totales['total_saldo'] or 0,
    })


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
    return render(request, 'despachos/form.html', {
        'form': form, 'titulo': 'Editar Despacho', 'despacho': despacho,
    })


@login_required
def eliminar_despacho(request, pk):
    despacho = get_object_or_404(Despacho, pk=pk)
    if request.method == 'POST':
        numero = despacho.numero
        despacho.delete()
        messages.success(request, f'Despacho {numero} eliminado.')
        return redirect('despachos:lista')
    return render(request, 'despachos/confirmar_eliminar.html', {'despacho': despacho})


@login_required
def importar_excel(request):
    if request.method == 'POST':
        form = ImportarExcelForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo']
            try:
                df = pd.read_excel(archivo)
                creados = 0
                omitidos = 0

                for _, row in df.iterrows():
                    contrato = str(row.get('Contrato', '')).strip()
                    if not contrato or contrato == 'nan':
                        omitidos += 1
                        continue

                    if Despacho.objects.filter(numero=contrato).exists():
                        omitidos += 1
                        continue

                    # Mensajero → Transportista
                    mensajero_nombre = str(row.get('Mensajero', '')).strip()
                    transportista = None
                    if mensajero_nombre and mensajero_nombre != 'nan':
                        transportista, _ = Transportista.objects.get_or_create(
                            nombre=mensajero_nombre,
                            defaults={'identificacion': mensajero_nombre[:50]},
                        )

                    estado_raw = str(row.get('Estado', 'PLANILLAS')).strip().upper()
                    tipo = 'reventas' if estado_raw == 'REVENTAS' else 'planillas'

                    fecha_venta = pd.to_datetime(row.get('Fecha de venta'), errors='coerce')
                    fecha_pago = pd.to_datetime(row.get('Fecha de pago'), errors='coerce')

                    saldo_val = row.get('Saldo', 0)
                    try:
                        saldo_val = Decimal(str(saldo_val)) if str(saldo_val) != 'nan' else Decimal('0')
                    except Exception:
                        saldo_val = Decimal('0')

                    total_val = row.get('Total', 0)
                    try:
                        total_val = Decimal(str(total_val)) if str(total_val) != 'nan' else Decimal('0')
                    except Exception:
                        total_val = Decimal('0')

                    Despacho.objects.create(
                        numero=contrato,
                        tipo=tipo,
                        destinatario=str(row.get('Cliente', '')).strip(),
                        celular=str(row.get('Celular', '')).replace('.0', '').strip() if str(row.get('Celular', '')) != 'nan' else '',
                        cedula=str(row.get('Cédula', '')).strip() if str(row.get('Cédula', '')) != 'nan' else '',
                        destino=str(row.get('Dirección', '')).strip(),
                        zona=str(row.get('Zona', '')).strip(),
                        origen='Bodega',
                        vendedor1=str(row.get('Vendedor1', '')).strip() if str(row.get('Vendedor1', '')) != 'nan' else '',
                        vendedor2=str(row.get('Vendedor2', '')).strip() if str(row.get('Vendedor2', '')) != 'nan' else '',
                        coordinador_nombre=str(row.get('Coordinador', '')).strip() if str(row.get('Coordinador', '')) != 'nan' else '',
                        productos_detalle=str(row.get('Productos', '')).strip() if str(row.get('Productos', '')) != 'nan' else '',
                        valor_venta=total_val,
                        saldo=saldo_val,
                        estado='pendiente',
                        transportista=transportista,
                        fecha_despacho=fecha_venta.date() if pd.notna(fecha_venta) else timezone.now().date(),
                        fecha_pago=fecha_pago.date() if pd.notna(fecha_pago) else None,
                        creado_por=request.user,
                    )
                    creados += 1

                messages.success(request, f'Importación exitosa: {creados} registros creados, {omitidos} omitidos.')
                return redirect('despachos:lista')
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {e}')
    else:
        form = ImportarExcelForm()
    return render(request, 'despachos/importar.html', {'form': form})


# --- Transportistas ---

@login_required
def lista_transportistas(request):
    transportistas = Transportista.objects.annotate(
        total_despachos=Count('despachos'),
        total_ventas=Sum('despachos__valor_venta'),
        total_saldo=Sum('despachos__saldo'),
    )
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
    return render(request, 'despachos/transportistas/form.html', {
        'form': form, 'titulo': 'Editar Transportista',
    })


# --- Vehículos ---

@login_required
def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.select_related('transportista').annotate(
        total_despachos=Count('despachos'),
    )
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
    return render(request, 'despachos/vehiculos/form.html', {
        'form': form, 'titulo': 'Editar Vehículo',
    })
