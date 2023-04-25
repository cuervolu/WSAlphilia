from django.db import models


# Create your models here.
class Categoria(models.TextChoices):
    FICTION = "Fiction"
    GENERAL = "General"
    HISTORICAL = "Historical"
    SUSPENSE = "Suspense"
    THRILLERS = "Thrillers"
    COMPUTERS = "Computers"
    CATEGORIAS_CHOICES = [
        (FICTION, "Fiction"),
        (GENERAL, "General"),
        (HISTORICAL, "Historical"),
        (SUSPENSE, "Suspense"),
        (THRILLERS, "Thrillers"),
        (COMPUTERS, "Computers"),
    ]
    nombre = models.CharField(
        max_length=200,
        choices=CATEGORIAS_CHOICES,
        default=GENERAL,
    )

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    id_libro = models.BigAutoField(
        primary_key=True, db_column="ID_LIBRO", verbose_name="ID Libro"
    )
    nombre_libro = models.CharField(max_length=100, null=False)
    descripcion = models.TextField(null=False)
    autor = models.CharField(max_length=100, null=False)
    editorial = models.CharField(max_length=100, null=False)
    precio_unitario = models.BigIntegerField(null=False)
    cantidad_disponible = models.BigIntegerField(null=False)
    portada = models.CharField(max_length=255, null=False)
    fecha_publicacion = models.DateField(null=True)
    categoria = models.CharField(
        max_length=200, choices=Categoria.choices, default=Categoria.GENERAL
    )

    class Meta:
        db_table = "libro"

    def __str__(self):
        return self.nombre_libro
