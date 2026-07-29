import zipfile

ZIP_PASSWORD = b"IQRAKHATIB@123"

LICENSE_DATA = (
    "ZAID-PARKING-001|"
    "e8dde8b741df7fdae08e4d5c0db5a6a30c1c69227b30f7f8f802b48a0b6b4d4c|"
    "LIFETIME"
)

with zipfile.ZipFile("license.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("license.key", LICENSE_DATA)

print("✅ license.zip created")
