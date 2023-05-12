"""
URL configuration for servicio_alphilia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from sistema_web_alphilia.views import LibroViewSet

router = DefaultRouter()
router.register(r'libros', LibroViewSet, basename='libro')

urlpatterns = [
    path('libros/get-libros-from-api/', LibroViewSet.as_view({'get': 'get_libros_from_api'}), name='get-libros-from-api'),
    path('libros/get-libros-by-categoria/', LibroViewSet.as_view({'get': 'get_libros_by_categoria'}), name='get-libros-by-categoria'),
    path('', include(router.urls)),
]


urlpatterns += router.urls

