python manage.py makemigrations --no-input
python manage.py migrate --no-input
#python manage.py create_superuser -u
#python manage.py load_data
python manage.py collectstatic --no-input
cp -r /app/collected_static/. /static/static/

gunicorn vybeerai_backend.wsgi:application --bind 0.0.0.0:8000
 