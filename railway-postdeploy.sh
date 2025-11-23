#!/bin/bash
# Railway post-deploy script to ensure migrations run
# This can be called manually or set as a post-deploy hook

set -e  # Exit on error

echo "=========================================="
echo "POST-DEPLOY: Running Migrations"
echo "=========================================="

# Create directories
mkdir -p media/locks staticfiles

# Run migrations with retry logic
python run_migrations.py

# Collect static files
echo "=========================================="
echo "POST-DEPLOY: Collecting Static Files"
echo "=========================================="
python manage.py collectstatic --noinput

echo "=========================================="
echo "POST-DEPLOY: Complete"
echo "=========================================="

