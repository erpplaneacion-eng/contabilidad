web: gunicorn contabiliadad.wsgi:application --log-file -
release: python manage.py migrate --noinput && python manage.py ensure_superuser
