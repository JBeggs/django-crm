#!/usr/bin/env python
"""
Quick script to check Railway PostgreSQL database state.
Run this via Railway web shell or Railway CLI once you have access.

Usage:
    python check_database_state.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webcrm.settings')
django.setup()

from django.db import connection

print("=" * 60)
print("DATABASE STATE CHECK")
print("=" * 60)

# 1. Test connection
print("\n1. Testing database connection...")
try:
    connection.ensure_connection()
    print("   ✅ Database connection successful!")
    
    with connection.cursor() as cursor:
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"   PostgreSQL version: {version[:80]}...")
except Exception as e:
    print(f"   ❌ Connection failed: {type(e).__name__}: {e}")
    exit(1)

# 2. Check if migrations table exists
print("\n2. Checking migrations table...")
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'django_migrations'
        """)
        exists = cursor.fetchone()
        if exists:
            cursor.execute('SELECT COUNT(*) FROM django_migrations')
            count = cursor.fetchone()[0]
            print(f"   ✅ Migrations table exists ({count} migrations recorded)")
        else:
            print("   ❌ Migrations table does NOT exist - migrations haven't run!")
except Exception as e:
    print(f"   ❌ Error checking migrations: {e}")

# 3. List all tables
print("\n3. Listing all tables in database...")
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        if tables:
            print(f"   Found {len(tables)} tables:")
            for table in tables[:20]:  # Show first 20
                print(f"     - {table[0]}")
            if len(tables) > 20:
                print(f"     ... and {len(tables) - 20} more")
        else:
            print("   ❌ No tables found - migrations haven't run!")
except Exception as e:
    print(f"   ❌ Error listing tables: {e}")

# 4. Check critical tables
print("\n4. Checking critical tables...")
critical_tables = [
    'settings_massmailsettings',
    'settings_reminders',
    'django_migrations',
    'auth_user',
    'django_content_type',
    'django_session',
]

for table_name in critical_tables:
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = '{table_name}'
            """)
            exists = cursor.fetchone()
            status = "✅ EXISTS" if exists else "❌ MISSING"
            print(f"   {table_name}: {status}")
    except Exception as e:
        print(f"   {table_name}: ❌ ERROR - {e}")

# 5. Check migration status via Django
print("\n5. Checking Django migration status...")
try:
    from django.core.management import call_command
    from io import StringIO
    
    output = StringIO()
    call_command('showmigrations', '--list', stdout=output)
    migrations_output = output.getvalue()
    
    # Count applied migrations
    applied = migrations_output.count('[X]')
    unapplied = migrations_output.count('[ ]')
    
    print(f"   Applied migrations: {applied}")
    print(f"   Unapplied migrations: {unapplied}")
    
    if unapplied > 0:
        print("   ⚠️  Some migrations haven't been applied!")
        print("\n   First few unapplied migrations:")
        for line in migrations_output.split('\n')[:15]:
            if '[ ]' in line:
                print(f"     {line.strip()}")
except Exception as e:
    print(f"   ❌ Error checking migration status: {e}")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("\nIf you see:")
print("  - ❌ No tables found → Run: python manage.py migrate")
print("  - ❌ Migrations table missing → Run: python manage.py migrate")
print("  - ✅ Tables exist → Database is set up correctly")
print("\n" + "=" * 60)

