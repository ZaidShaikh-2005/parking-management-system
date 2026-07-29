import sys
import os

# Add project root to Python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from license.license_check import verify_license

try:
    verify_license()
except SystemExit:
    sys.exit(1)

sys.exit(0)
