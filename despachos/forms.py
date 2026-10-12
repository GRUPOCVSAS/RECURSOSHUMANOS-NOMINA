from django import forms
from .models import Despacho, Transportista, Vehiculo, SeguimientoDespacho


class DespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = [
            'numero', 'tipo', 'fecha_despacho', 'fecha_pago',
            'destinatario', 'celular', 'cedula',
            'destino', 'zona', 'origen',
            'vendedor1', 'vendedor2', 'coordinador_nombre',
            'productos_detalle', 'valor_venta', 'saldo',
            'peso_kg', 'estado', 'transportista', 'vehiculo', 'notas',
        ]
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'fecha_despacho': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_pago': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'destinatario': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'zona': forms.TextInput(attrs={'class': 'form-control'}),
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
            'vendedor1': forms.TextInput(attrs={'class': 'form-control'}),
            'vendedor2': forms.TextInput(attrs={'class': 'form-control'}),
            'coordinador_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'productos_detalle': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'transportista': forms.Select(attrs={'class': 'form-select'}),
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class TransportistaForm(forms.ModelForm):
    class Meta:
        model = Transportista
        fields = ['nombre', 'identificacion', 'telefono', 'email', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['placa', 'marca', 'modelo', 'capacidad_kg', 'transportista', 'activo']
        widgets = {
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'transportista': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SeguimientoForm(forms.ModelForm):
    class Meta:
        model = SeguimientoDespacho
        fields = ['estado', 'observacion']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observacion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class FiltroDespachoForm(forms.Form):
    estado = forms.ChoiceField(
        choices=[('', 'Todos los estados')] + Despacho.ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    tipo = forms.ChoiceField(
        choices=[('', 'Todos los tipos')] + Despacho.TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contrato, cliente, zona, vendedor...'}),
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    zona = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zona...'}),
    )
    mensajero = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mensajero...'}),
    )


class ImportarExcelForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo Excel de ventas',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'}),
    )
