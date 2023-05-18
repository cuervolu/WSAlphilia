from django.db import models
from autoslug import AutoSlugField

# Create your models here.
class Categoria(models.TextChoices):
    FICTION = "Fiction"
    GENERAL = "General"
    HISTORICAL = "Historical"
    SUSPENSE = "Suspense"
    THRILLERS = "Thrillers"
    COMPUTERS = "Computers"


class Libro(models.Model):
    id_libro = models.BigAutoField(
        primary_key=True, db_column="ID_LIBRO", verbose_name="ID Libro"
    )
    nombre_libro = models.CharField(max_length=100, null=False)
    descripcion = models.TextField(null=False)
    autor = models.CharField(max_length=100, null=False)
    editorial = models.CharField(max_length=100, null=False)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    cantidad_disponible = models.BigIntegerField(null=False)
    thumbnail = models.URLField()
    portada = models.URLField(max_length=300)
    fecha_publicacion = models.DateField(null=True)
    categoria = models.CharField(
        max_length=200,
        choices=Categoria.choices,
        default=Categoria.GENERAL,
    )
    isbn = models.CharField(max_length=20, null=True)
    slug = AutoSlugField(populate_from="nombre_libro")

    class Meta:
        db_table = "libro"

    def __str__(self):
        return self.nombre_libro
