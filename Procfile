web: gunicorn project.wsgi
release: python manage.py migrate && python manage.py collectstatic --noinput
