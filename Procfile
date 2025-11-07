web: gunicorn contabiliadad.wsgi:application --config gunicorn_config.py
release: python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py ensure_superuser
