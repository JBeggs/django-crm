release: echo "=== RELEASE COMMAND STARTING ===" && mkdir -p media/locks staticfiles && echo "=== RUNNING MIGRATIONS ===" && python run_migrations.py && echo "=== COLLECTING STATIC FILES ===" && python manage.py collectstatic --noinput && echo "=== RELEASE COMMAND COMPLETED ==="
web: gunicorn webcrm.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 30 --graceful-timeout 10 --max-requests 1000 --max-requests-jitter 100

