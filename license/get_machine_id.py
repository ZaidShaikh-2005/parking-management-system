import uuid
import hashlib

mac = uuid.getnode()
machine_id = hashlib.sha256(str(mac).encode()).hexdigest()
print(machine_id)
