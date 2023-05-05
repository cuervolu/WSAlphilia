#!/bin/bash

# Carga las variables de entorno desde el archivo .env
dos2unix .env
# Espera a que Oracle esté disponible
while ! nc -z $DB_HOST $DB_PORT; do   
    sleep 1 # Espera 1 segundo antes de volver a intentar
done

# Ejecuta las migraciones
python manage.py makemigrations
python manage.py makemigrations sistema_web_alphilia
python manage.py migrate

# Inicia el servidor
python manage.py runserver 0.0.0.0:8080
