from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
#from django.db import models
from django.core.validators import RegexValidator

class UsuarioManager(BaseUserManager):
    def create_user(self, numero, password=None, **extra_fields):
        if not numero:
            raise ValueError('El número es obligatorio')
        
        user = self.model(numero=numero, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, numero, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(numero, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    numero = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'numero'
    REQUIRED_FIELDS = ['nombre']
    
    def __str__(self):
        return self.numero
    
    def get_full_name(self):
        return self.nombre
    
    def get_short_name(self):
        return self.nombre
    


    
class TCP(models.Model):
    """
    Modelo para TCP (Trabajo Común de Prácticas)
    """
    numero = models.IntegerField(
        unique=True,
        verbose_name="Número de TCP",
        help_text="Número único del TCP (ej: 1, 2, 3, etc.)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "TCP"
        verbose_name_plural = "TCPs"
        ordering = ['numero']

    def __str__(self):
        return f"TCP {self.numero}"

class Semestre(models.Model):
    """Modelo para gestionar los semestres académicos"""
    
    numero = models.IntegerField(
        unique=True,  # Ahora es único pero no es llave primaria
        verbose_name="Semestre"
    )
    
    class Meta:
        ordering = ['numero']
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"
    
    def __str__(self):
        return f"{self.numero}° Semestre"
    
class Asignatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, help_text="Código de color en formato HEX (ej: #FF5733)", default="#000000")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Asignatura"
        verbose_name_plural = "Asignaturas"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# models.py - Actualizar el modelo Estudiante
class Estudiante(models.Model):
    numero_control = models.CharField(
        max_length=14, 
        unique=True, 
        verbose_name="Número de Control",
        validators=[RegexValidator(r'^\d{14}$', 'El número de control debe tener exactamente 14 dígitos.')]
    )
    curp = models.CharField(max_length=18, unique=True, verbose_name="CURP")
    nombre = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    semestre_actual = models.ForeignKey(
        Semestre, 
        on_delete=models.PROTECT, 
        related_name='estudiantes_actuales',
        verbose_name="Semestre actual",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ['apellidos', 'nombre']

    def __str__(self):
        return f"{self.numero_control} - {self.nombre} {self.apellidos}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del estudiante"""
        return f"{self.nombre} {self.apellidos}".strip()
    
    @property
    def curp_completo(self):
        """Retorna la CURP del estudiante"""
        return self.curp

# models.py
class Nota(models.Model):
    estudiante = models.ForeignKey(
        Estudiante, 
        on_delete=models.CASCADE, 
        related_name='notas'
    )
    asignatura = models.ForeignKey(
        Asignatura, 
        on_delete=models.CASCADE, 
        related_name='notas'
    )
    semestre_cursado = models.ForeignKey(
        Semestre,
        on_delete=models.PROTECT,
        related_name='notas',
        verbose_name="Semestre en que cursó",
        editable=False
    )
    tcp = models.ForeignKey(
        TCP,
        on_delete=models.PROTECT,
        related_name='notas',
        verbose_name="TCP asociado"
    )

    nota = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nota"
        verbose_name_plural = "Notas"
        # CAMBIADO: Unicidad por estudiante + tcp + semestre + asignatura
        unique_together = ['estudiante', 'tcp', 'semestre_cursado', 'asignatura']
        ordering = ['estudiante', 'asignatura']

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} - TCP: {self.tcp.numero} - {self.semestre_cursado}: {self.nota}"
    
    def save(self, *args, **kwargs):
        # Validar que tenga TCP
        if not self.tcp_id:
            raise ValueError("El TCP es obligatorio")
        
        # Si no tiene semestre cursado asignado, usar el semestre actual del estudiante
        if not self.semestre_cursado_id and self.estudiante:
            self.semestre_cursado = self.estudiante.semestre_actual
        
        # Verificar que ya tenga semestre cursado antes de guardar
        if not self.semestre_cursado_id:
            raise ValueError("No se pudo determinar el semestre cursado. El estudiante debe tener un semestre actual.")
        
        super().save(*args, **kwargs)