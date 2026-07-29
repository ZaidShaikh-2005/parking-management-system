import zipfile
import os
import sys
from datetime import datetime
import hashlib
import uuid

ZIP_PASSWORD = b"ZAID@123"

def get_machine_id():
    mac = uuid.getnode()
    return hashlib.sha256(str(mac).encode()).hexdigest()

def verify_license():
    base_dir = os.path.dirname(__file__)
    zip_path = os.path.join(base_dir, "license.zip")

    if not os.path.exists(zip_path):
        print("❌ LICENSE FILE MISSING")
        sys.exit(1)

    try:
        with zipfile.ZipFile(zip_path) as z:
            data = z.read("license.key", pwd=ZIP_PASSWORD).decode()
    except:
        print("❌ LICENSE PASSWORD INVALID OR FILE TAMPERED")
        sys.exit(1)

    parts = data.strip().split("|")
    if len(parts) != 3:
        print("❌ LICENSE FORMAT INVALID")
        sys.exit(1)

    key, machine_id, expiry = parts

    if machine_id != get_machine_id():
        print("❌ LICENSE NOT FOR THIS MACHINE")
        sys.exit(1)

    # 🔥 sanitize expiry (pendrive / space proof)
    expiry = expiry.strip().upper()

    if expiry != "LIFETIME":
        try:
            exp_date = datetime.strptime(expiry, "%Y-%m-%d")
        except ValueError:
            print("❌ INVALID EXPIRY FORMAT")
            sys.exit(1)

        if datetime.now() > exp_date:
            print("❌ LICENSE EXPIRED")
            sys.exit(1)

    print("✅ LICENSE VERIFIED")
