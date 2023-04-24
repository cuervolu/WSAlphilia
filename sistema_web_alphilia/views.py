from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Libro
from .serializers import LibroSerializer

import random
import requests
import json
from decouple import config

# Create your views here.


class LibroView(APIView):
    def get(self, request):
        # Obtener la clave de la API de Google Books desde el archivo de entorno
        api_key = config("GOOGLE_BOOKS_API_KEY")
        
        # Hacer una solicitud a la API de Google Books para obtener los libros más relevantes
        response = requests.get(
            f"https://www.googleapis.com/books/v1/volumes?q=*&key={api_key}&maxResults=40&orderBy=relevance"
        )
        
        # Convertir la respuesta de la API a un objeto de Python
        data = json.loads(response.content)
        
        for item in data["items"]:
            # Obtener los valores de "volumeInfo" y "saleInfo" del diccionario del libro actual
            volume_info = item.get("volumeInfo", {})
            sale_info = item.get("saleInfo", {})
            
            # Establecer los valores predeterminados para los campos del libro en un diccionario
            default_values = {
                "nombre_libro": volume_info.get("title", ""),
                "autor": volume_info.get("authors", ["a/d"])[0],
                "descripcion": volume_info.get("description", ""),
                "editorial": volume_info.get("publisher", "s/e"),
                "precio_unitario": sale_info.get("retailPrice", {}).get("amount", random.randint(8000, 45000)),
                "portada": volume_info.get("imageLinks", {}).get("thumbnail", "https://islandpress.org/sites/default/files/default_book_cover_2015.jpg"),
                "cantidad_disponible": random.randint(1, 150)
            }
            
            # Saltar este libro si no tiene una descripción
            if not default_values["descripcion"]:
                continue
        
            # Crear un nuevo libro con los valores predeterminados y guardar en la base de datos
            self.crear_nuevo_libro(default_values)

        # Obtener todos los libros guardados y serializarlos para enviarlos en la respuesta
        libros = Libro.objects.all()
        serializer = LibroSerializer(libros, many=True)
        return Response(serializer.data)
    
    # Método para crear un nuevo libro en la base de datos
    def crear_nuevo_libro(self, data):
        # Verificar si el libro ya existe en la base de datos
        if not Libro.objects.filter(nombre_libro=data["nombre_libro"], autor=data["autor"]).exists():
            # Crear una nueva instancia del modelo de libro con los valores del diccionario "default_values"
            libro = Libro.objects.create(**data)
            # Guardar el libro en la base de datos
            libro.save()
