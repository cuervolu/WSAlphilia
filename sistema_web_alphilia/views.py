import datetime
import logging


import random
import requests
import json

from rest_framework.response import Response
from rest_framework import viewsets, pagination, status
from rest_framework.decorators import action


from .models import Libro
from .serializers import LibroSerializer

from decouple import config


# Create your views here.
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configurar el formateador del registro
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configurar un controlador de archivo para registrar los mensajes de error
file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

# Configurar un controlador de registro para mostrar los mensajes en la consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Agregar los controladores al registro
logger.addHandler(file_handler)
logger.addHandler(console_handler)
class LibroPagination(pagination.PageNumberPagination):   
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class LibroViewSet(viewsets.ModelViewSet): 
    queryset = Libro.objects.order_by("nombre_libro")
    serializer_class = LibroSerializer
    pagination_class = LibroPagination
    
    def create_libro_from_data(self,data, _=None):
        volume_info = data.get("volumeInfo", {})
        sale_info = data.get("saleInfo", {})
        
        isbn = volume_info.get("industryIdentifiers", [])[0].get("identifier", "s/e")
        if Libro.objects.filter(isbn=isbn).exists():
            return None
        
        nombre_libro = volume_info.get("title", "")
        autor = volume_info.get("authors", ["a/d"])[0]

        if Libro.objects.filter(nombre_libro=nombre_libro, autor=autor).exists():
            return None


        if "categories" in volume_info:
            categorias = volume_info.get("categories")
            if categorias:
                categoria = categorias[0]
            else:
                categoria = "General"
        else:
            categoria = "General"

        fecha_publicacion = volume_info.get("publishedDate")

        if not fecha_publicacion:
            current_year = datetime.datetime.now().year
            fecha_publicacion = datetime.datetime(
                current_year,
                random.randint(1, 12),
                random.randint(1, 28),
            ).strftime("%Y-%m-%d")

        try:
            datetime.datetime.strptime(fecha_publicacion, "%Y-%m-%d")
        except ValueError:
            return None

        default_values = {
            "nombre_libro": volume_info.get("title", ""),
            "autor": volume_info.get("authors", ["a/d"])[0],
            "descripcion": volume_info.get("description", "Sin descripción"),
            "editorial": volume_info.get("publisher", "s/e"),
            "precio_unitario": sale_info.get("retailPrice", {}).get(
                "amount", random.randint(8000, 45000)
            ),
            "portada": volume_info.get("imageLinks", {}).get(
                "thumbnail",
                "https://islandpress.org/sites/default/files/default_book_cover_2015.jpg",
            ),
            "cantidad_disponible": random.randint(1, 150),
            "fecha_publicacion": fecha_publicacion,
            "categoria": categoria,
            "isbn": volume_info.get("industryIdentifiers", [])[0].get(
                "identifier", "s/e"
            ),
        }

        libro = Libro.objects.create(**default_values)
        return libro


    @action(detail=False, methods=["get"])
    def get_libros_from_api(self, request):
        # Obtener la clave de la API de Google Books desde el archivo de entorno
        api_key = config("GOOGLE_BOOKS_API_KEY")

        # Establecer el número máximo de resultados por página
        max_results = 40

        # Obtener el número de página de la solicitud
        page_number = request.query_params.get("page", "1")
        page_number = int(page_number)  # convierte el valor en un entero

        # Calcular el índice de inicio para la página actual
        start_index = (page_number - 1) * max_results + 1

        libros_creados = []
        count = 0
        while count < max_results:
            # Hacer una solicitud a la API de Google Books para obtener los libros más relevantes
            try:
                response = requests.get(
                    f"https://www.googleapis.com/books/v1/volumes?q=*&key={api_key}&startIndex={start_index}&maxResults={max_results}&orderBy=relevance&random={random.random()}&projection=full"
                )
            except requests.exceptions.RequestException as e:
                logger.error(f"Ocurrió un error al hacer la solicitud: {e}")
                raise
            try:
                data = json.loads(response.content)
                response.close()
                if "items" not in data:
                    data = json.loads(response.content)
                response.close()
                if "items" not in data:
                    return Response(
                        {"error": "No se encontraron resultados"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                for item in data.get("items", []):
                    libro = self.create_libro_from_data(item)
                    if libro:
                        libros_creados.append(libro)

                    count += 1
                    start_index += 1

                    if count >= max_results:
                        break

                # Guardar los libros creados en la base de datos
                Libro.objects.bulk_create(libros_creados)

                # Obtener todos los libros guardados y serializarlos para enviarlos en la respuesta
                libros = Libro.objects.all()
                page = self.paginate_queryset(libros)
                if page is not None:
                    serializer = LibroSerializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = LibroSerializer(libros, many=True)
                return Response(serializer.data)
            except Exception as e:
                logger.error(f"Ocurrió un error al procesar los datos de la API: {e}")
                return Response(
                {"error": "Ocurrió un error al procesar los datos de la API"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

    @action(detail=False, methods=["get"])
    def get_libros_by_categoria(self, request):
        categoria = request.query_params.get("categoria", None)
        if categoria:
            libros = Libro.objects.filter(categoria=categoria)
            if libros.exists():
                serializer = LibroSerializer(libros, many=True)
                return Response(serializer.data)
            else:
                # Obtener la clave de la API de Google Books desde el archivo de entorno
                api_key = config("GOOGLE_BOOKS_API_KEY")

                # Hacer una solicitud a la API de Google Books para obtener los libros de la categoría especificada
                try:
                    response = requests.get(
                        f"https://www.googleapis.com/books/v1/volumes?q=subject:{categoria}&key={api_key}"
                    )
                    response.raise_for_status()
                    data = response.json()
                    response.close()
                except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                    return Response(
                        {"error": f"Error al obtener los libros de la API: {e}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                libros_creados = []
                for item in data.get("items", []):
                    libro = self.create_libro_from_data(item)
                    if libro:
                        libros_creados.append(libro)

                serializer = LibroSerializer(libros_creados, many=True)
                return Response(serializer.data)
        else:
            return Response({"error": "La categoría no fue proporcionada."}, status=status.HTTP_400_BAD_REQUEST)

        
    