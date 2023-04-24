from django.db import models

# Create your models here.


class Libro(models.Model):
    id_libro = models.BigAutoField(
        primary_key=True, db_column='ID_LIBRO', verbose_name='ID Libro')
    nombre_libro = models.CharField(max_length=100, null=False)
    descripcion = models.TextField(null=False)
    autor = models.CharField(max_length=100, null=False)
    editorial = models.CharField(max_length=100, null=False)
    precio_unitario = models.BigIntegerField( null=False)
    cantidad_disponible = models.BigIntegerField( null=False)
    portada = models.CharField(max_length=255, null=False)

    class Meta:
        managed = True
        db_table = 'libro'
