import sys
import os
import json
import paho.mqtt.client as mqtt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from license.license_check import verify_license
verify_license()

MQTT_BROKER = "172.20.10.2"
MQTT_PORT = 1883
MQTT_TOPIC = "parking/control"


# 🔵 EXISTING FUNCTION — DO NOT CHANGE
def publish_booking(product, slot):
    payload = {
        "action": "BOOK",
        "product": product,
        "slot": slot
    }

    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_start()   # 🔥 IMPORTANT
    client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
    client.loop_stop()

    client.disconnect()



# 🟢 NEW FUNCTION — GATE OPEN SUCCESS
def publish_gate_open_success(token, slot):
    payload = {
        "action": "GATE_OPEN_SUCCESS",
        "token": token,
        "slot": slot
    }

    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_start()   # 🔥 IMPORTANT
    client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
    client.loop_stop()

    client.disconnect()
