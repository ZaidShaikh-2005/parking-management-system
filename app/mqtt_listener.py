import sys
import os

# --------------------------------------------------
# PROJECT PATH + LICENSE
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from license.license_check import verify_license
verify_license()

# --------------------------------------------------
# DJANGO SETUP
# --------------------------------------------------
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soloRising.settings")
django.setup()

# --------------------------------------------------
# IMPORTS
# --------------------------------------------------
import json
import paho.mqtt.client as mqtt
from app.models import ParkingSlot

# --------------------------------------------------
# MQTT CALLBACK
# --------------------------------------------------
def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors="ignore").strip()
    print("📩 Message received:", payload)

    # 🔒 Only JSON allowed
    if not payload.startswith("{"):
        print("ℹ Non-JSON message ignored")
        return

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print("⚠ Invalid JSON ignored")
        return

    action = data.get("action")
    product = data.get("product")
    slot_no = data.get("slot")

    if not all([action, product, slot_no]):
        print("⚠ Missing booking fields")
        return

    # 🔥 CRITICAL FIX — slot_number MUST be int
    slot = ParkingSlot.objects.filter(
        product__title__iexact=product,
        slot_number=slot_no
    ).first()

    if not slot:
        print("❌ Slot not found")
        return

    action = action.upper()

    # ---------------- BOOK SLOT ----------------
    if action == "BOOK":
        if slot.is_occupied:
            print("⚠ Slot already occupied")
            return

        slot.is_occupied = True
        slot.booking_source = "MQTT"
        slot.save(update_fields=["is_occupied", "booking_source"])
        print(f"✅ Slot {slot_no} BOOKED via MQTT")

    # ---------------- FREE SLOT (FINAL FIX) ----------------
    elif action == "FREE":
        # 🔥 FORCE FREE — NO IGNORE, NO RETURN
        slot.is_occupied = False
        slot.booking_source = None
        slot.save(update_fields=["is_occupied", "booking_source"])
        print(f"♻ Slot {slot_no} FREED via MQTT")

    else:
        print("⚠ Unknown action ignored")

# --------------------------------------------------
# MQTT CONNECTION
# --------------------------------------------------
client = mqtt.Client()
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.subscribe("parking/booking")

print("✅ Connected to LOCAL MQTT Broker")
client.loop_forever()
