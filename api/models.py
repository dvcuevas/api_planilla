from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Planilla(models.Model):
    """
    Modelo principal que representa una planilla de recaudación.
    Contiene la imagen subida por la app y el estado del procesamiento.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completada'),
        ('error', 'Error'),
    ]
    
    # Campos principales
    imagen = models.ImageField(
        upload_to='planillas/',
        help_text='Imagen de la planilla de recaudación'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Estado del procesamiento de la planilla'
    )
    
    # Datos extraídos por Azure Form Recognizer
    datos_extraidos = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos extraídos por Azure Form Recognizer'
    )
    error_procesamiento = models.TextField(
        null=True,
        blank=True,
        help_text='Mensaje de error si el procesamiento falla'
    )
    
    # Metadatos
    nombre_archivo = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='Nombre original del archivo'
    )
    tamaño_archivo = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Tamaño del archivo en bytes'
    )
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Planilla'
        verbose_name_plural = 'Planillas'
    
    def __str__(self):
        return f"Planilla {self.id} - {self.get_status_display()}"


class Tarifa(models.Model):
    """
    Modelo que representa las tarifas de la empresa.
    Se relaciona con una planilla específica.
    """
    
    planilla = models.ForeignKey(
        Planilla,
        on_delete=models.CASCADE,
        related_name='tarifas',
        help_text='Planilla a la que pertenece esta tarifa'
    )
    
    # Información de la tarifa
    concepto = models.CharField(
        max_length=200,
        help_text='Concepto de la tarifa (ej: Pasaje urbano, Pasaje interurbano)'
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Precio de la tarifa'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        help_text='Cantidad de boletos vendidos'
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Subtotal (precio × cantidad)'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['concepto']
        verbose_name = 'Tarifa'
        verbose_name_plural = 'Tarifas'
    
    def __str__(self):
        return f"{self.concepto} - ${self.precio}"


class Ingreso(models.Model):
    """
    Modelo que representa los ingresos de la planilla.
    """
    
    planilla = models.ForeignKey(
        Planilla,
        on_delete=models.CASCADE,
        related_name='ingresos',
        help_text='Planilla a la que pertenece este ingreso'
    )
    
    # Información del ingreso
    concepto = models.CharField(
        max_length=200,
        help_text='Concepto del ingreso'
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Monto del ingreso'
    )
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['concepto']
        verbose_name = 'Ingreso'
        verbose_name_plural = 'Ingresos'
    
    def __str__(self):
        return f"{self.concepto} - ${self.monto}"


class Egreso(models.Model):
    """
    Modelo que representa los egresos de la planilla.
    """
    
    planilla = models.ForeignKey(
        Planilla,
        on_delete=models.CASCADE,
        related_name='egresos',
        help_text='Planilla a la que pertenece este egreso'
    )
    
    # Información del egreso
    concepto = models.CharField(
        max_length=200,
        help_text='Concepto del egreso'
    )
    monto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Monto del egreso'
    )
    observaciones = models.TextField(
        blank=True,
        help_text='Observaciones adicionales'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['concepto']
        verbose_name = 'Egreso'
        verbose_name_plural = 'Egresos'
    
    def __str__(self):
        return f"{self.concepto} - ${self.monto}"


class ControlBoleto(models.Model):
    """
    Modelo que representa el control de boletos de la planilla.
    """
    
    planilla = models.ForeignKey(
        Planilla,
        on_delete=models.CASCADE,
        related_name='control_boletos',
        help_text='Planilla a la que pertenece este control'
    )
    
    # Información del control
    numero_inicial = models.PositiveIntegerField(
        help_text='Número inicial del talonario'
    )
    numero_final = models.PositiveIntegerField(
        help_text='Número final del talonario'
    )
    cantidad_vendidos = models.PositiveIntegerField(
        help_text='Cantidad de boletos vendidos'
    )
    cantidad_devueltos = models.PositiveIntegerField(
        default=0,
        help_text='Cantidad de boletos devueltos'
    )
    cantidad_anulados = models.PositiveIntegerField(
        default=0,
        help_text='Cantidad de boletos anulados'
    )
    
    # Cálculos
    total_boletos = models.PositiveIntegerField(
        help_text='Total de boletos en el talonario'
    )
    boletos_faltantes = models.PositiveIntegerField(
        default=0,
        help_text='Boletos faltantes (total - vendidos - devueltos - anulados)'
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['numero_inicial']
        verbose_name = 'Control de Boleto'
        verbose_name_plural = 'Controles de Boletos'
    
    def save(self, *args, **kwargs):
        # Calcular total de boletos
        self.total_boletos = self.numero_final - self.numero_inicial + 1
        
        # Calcular boletos faltantes
        self.boletos_faltantes = self.total_boletos - (
            self.cantidad_vendidos + self.cantidad_devueltos + self.cantidad_anulados
        )
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Talonario {self.numero_inicial}-{self.numero_final}"
