# import pymysql
# pymysql.install_as_MySQLdb()

from license.license_check import verify_license
verify_license()

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# e8dde8b741df7fdae08e4d5c0db5a6a30c1c69227b30f7f8f802b48a0b6b4d4c
# 🔐 LICENSE CHECK
from license.license_check import verify_license
verify_license()

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soloRising.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        raise
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soloRising.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
