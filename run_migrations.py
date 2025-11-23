#!/usr/bin/env python
"""Run migrations, ignoring 'already exists' errors but failing on connection errors."""
import sys
import subprocess
import time

# Print to stdout so Railway logs capture it
print("=" * 80)
print("RUNNING MIGRATIONS")
print("=" * 80)
sys.stdout.flush()

# Add timeout to prevent hanging forever
max_attempts = 3
for attempt in range(max_attempts):
    print(f"\nMigration attempt {attempt + 1}/{max_attempts}")
    sys.stdout.flush()
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', '--noinput'],
        capture_output=True,
        text=True,
        timeout=120  # 2 minute timeout per attempt
    )
    
    # Check if error is just "already exists" - that's okay
    if result.returncode != 0:
        error_lower = result.stderr.lower()
        if 'already exists' in error_lower:
            # "Already exists" is fine - table exists, which is what we want
            print("Some tables already exist (this is okay)")
            sys.exit(0)
        elif 'connection' in error_lower or 'timeout' in error_lower or 'operationalerror' in error_lower:
            # Database connection error - retry
            if attempt < max_attempts - 1:
                wait_time = (attempt + 1) * 5
                print(f"Database connection error (attempt {attempt + 1}/{max_attempts}). Retrying in {wait_time} seconds...", file=sys.stderr)
                print(result.stderr, file=sys.stderr)
                time.sleep(wait_time)
                continue
            else:
                # Final attempt failed - exit with error
                print("FATAL: Database connection failed after multiple attempts", file=sys.stderr)
                print(result.stderr, file=sys.stderr)
                sys.exit(result.returncode)
        else:
            # Other error - exit with failure
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)
    else:
        # Success
        print("\n" + "=" * 80)
        print("MIGRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(result.stdout)
        sys.stdout.flush()
        sys.exit(0)

# Should never reach here, but just in case
print("FATAL: Migrations failed after all retry attempts", file=sys.stderr)
sys.exit(1)

