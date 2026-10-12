from django.db import models
from django.contrib.auth.models import User


class Transportista(models.Model):
    nombre = models.CharField(max_length=200)
    identificacion = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'transportistas'

    def __str__(self):
        return self.nombre


class Vehiculo(models.Model):
    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    capacidad_kg = models.DecimalField(max_digits=10, decimal_places=2)
    transportista = models.ForeignKey(
        Transportista, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='vehiculos'
    )
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['placa']

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"


class Despacho(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('en_transito', 'En Tránsito'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    TIPO_CHOICES = [
        ('planillas', 'Planillas'),
        ('reventas', 'Reventas'),
    ]

    # Identificación
    numero = models.CharField(max_length=50, unique=True, verbose_name='Contrato')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='planillas')

    # Cliente
    destinatario = models.CharField(max_length=200, verbose_name='Cliente')
    celular = models.CharField(max_length=20, blank=True)
    cedula = models.CharField(max_length=30, blank=True)

    # Dirección y zona
    origen = models.CharField(max_length=200, blank=True, default='Bodega')
    destino = models.CharField(max_length=200, verbose_name='Dirección')
    zona = models.CharField(max_length=200, blank=True)

    # Comercial
    vendedor1 = models.CharField(max_length=200, blank=True)
    vendedor2 = models.CharField(max_length=200, blank=True)
    coordinador_nombre = models.CharField(max_length=200, blank=True, verbose_name='Coordinador')

    # Producto y logística
    productos_detalle = models.TextField(blank=True, verbose_name='Productos')
    descripcion = models.TextField(blank=True)
    peso_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Finanzas
    valor_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Total')
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Saldo pendiente')

    # Logística
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    transportista = models.ForeignKey(
        Transportista, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despachos', verbose_name='Mensajero'
    )
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despachos'
    )

    # Fechas
    fecha_despacho = models.DateField(verbose_name='Fecha de venta')
    fecha_pago = models.DateField(null=True, blank=True, verbose_name='Fecha de pago')

    # Auditoría
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='despachos_creados'
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha_despacho', '-creado_en']

    def __str__(self):
        return f"{self.numero} - {self.destinatario}"

    @property
    def cobrado(self):
        return self.valor_venta - self.saldo

    @property
    def estado_color(self):
        colores = {
            'pendiente': 'warning',
            'en_proceso': 'info',
            'en_transito': 'primary',
            'entregado': 'success',
            'cancelado': 'danger',
        }
        return colores.get(self.estado, 'secondary')


class SeguimientoDespacho(models.Model):
    despacho = models.ForeignKey(Despacho, on_delete=models.CASCADE, related_name='seguimientos')
    estado = models.CharField(max_length=20, choices=Despacho.ESTADO_CHOICES)
    observacion = models.TextField(blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.despacho.numero} - {self.get_estado_display()}"
