from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, pagination, status
from rest_framework.decorators import action


from .models import Libro, Categoria
from .serializers import LibroSerializer

import datetime
import random
import requests
import json
from decouple import config


# Create your views here.
class LibroPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 1000


class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.order_by("nombre_libro")
    serializer_class = LibroSerializer
    pagination_class = LibroPagination
    
    @action(detail=False, methods=["get"])
    def get_libros_from_api(self, request):
        # Obtener la clave de la API de Google Books desde el archivo de entorno
        api_key = config("GOOGLE_BOOKS_API_KEY")
        
        # Establecer el número máximo de resultados por página
        max_results = 40

        # Obtener el número de página de la solicitud
        page_number = request.query_params.get("page", "1")
        page_number = int(page_number) # convierte el valor en un entero

        # Calcular el índice de inicio para la página actual
        start_index = (page_number - 1) * max_results + 1
        
        libros_creados = []
        count = 0
        while count < max_results:
            # Hacer una solicitud a la API de Google Books para obtener los libros más relevantes
            try:
                response = requests.get(
                    f"https://www.googleapis.com/books/v1/volumes?q=*&key={api_key}&startIndex={start_index}&maxResults={max_results}&orderBy=relevance&random={random.random()}&printType=books&projection=full"
                )
            except requests.exceptions.RequestException as e:
                print(f"Ocurrió un error al hacer la solicitud: {e}")
                return Response({"error": {e}},status=status.HTTP_404_NOT_FOUND)
                break;

            try:
                data = json.loads(response.content)
                response.close()
                if "items" not in data:
                    return Response({"error": "No se encontraron resultados"},status=status.HTTP_404_NOT_FOUND)
            except requests.exceptions.RequestException as e:
                print(f"Ocurrió un error al hacer la solicitud: {e}")
                return Response({"error": "Ocurrió un error al hacer la solicitud"},status=status.HTTP_404_NOT_FOUND)


            for item in data["items"]:
                # Obtener los valores de "volumeInfo" y "saleInfo" del diccionario del libro actual
                volume_info = item.get("volumeInfo", {})
                sale_info = item.get("saleInfo", {})

                if "categories" in volume_info:
                    # Verificar si el libro está en una categoría permitida
                    categorias = volume_info.get("categories")
                    if categorias:
                        categoria = categorias[0]
                    else:
                        categoria = "Otro"
                else:
                    categoria = "Otro"


                fecha_publicacion = volume_info.get("publishedDate")
                
                if not fecha_publicacion:
                    continue

                try:
                    datetime.datetime.strptime(fecha_publicacion, "%Y-%m-%d")
                except ValueError:
                    continue

                # Establecer los valores predeterminados para los campos del libro en un diccionario
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
                    "isbn": volume_info.get("industryIdentifiers",[])[0].get("identifier","s/e")
                }

                # # Saltar este libro si no tiene una descripción
                # if not default_values["descripcion"]:
                #     continue
                
                count += len(data["items"])
                start_index += max_results
                
                #Crear una instancia del modelo de libro y guardar cada libro en la base de datos
                libro = Libro.objects.create(**default_values)

                libro.save()
                
                # Obtener todos los libros guardados y serializarlos para enviarlos en la respuesta
            libros = Libro.objects.all()
            page = self.paginate_queryset(libros)
            if page is not None:
                serializer = LibroSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = LibroSerializer(libros, many=True)
            return Response(serializer.data)


    # def list(self, request, *args, **kwargs):
    #     # Llama a la función get()
    #     self.get(request)

    #     queryset = self.filter_queryset(self.get_queryset())

    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def crear_nuevo_libro(self, request):
        data = request.data
        
        # Verificar si el libro ya existe en la base de datos
        if not Libro.objects.filter(
            nombre_libro=data["nombre_libro"], autor=data["autor"]
        ).exists():
            # Crear una nueva instancia del modelo de libro con los valores del diccionario "default_values"
            libro = Libro(**data)
            libro.save()
            
            serializer = LibroSerializer(libro)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
        return Response(
            {"detail": "Este libro ya existe en la base de datos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
