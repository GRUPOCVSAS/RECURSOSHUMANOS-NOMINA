from django import forms
from .models import Despacho, Transportista, Vehiculo, SeguimientoDespacho


class DespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = [
            'numero', 'fecha_despacho', 'origen', 'destino',
            'destinatario', 'descripcion', 'peso_kg',
            'estado', 'transportista', 'vehiculo', 'notas',
        ]
        widgets = {
            'fecha_despacho': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'origen': forms.TextInput(attrs={'class': 'form-control'}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'destinatario': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
    buscar = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Buscar por número, destino o destinatario...'}),
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
