import paho.mqtt.client as mqtt
import time
import json

# Broker configuration for End-to-End TLS
BROKER_ADDRESS = "localhost"
PORT = 8883
TOPIC = "home/smart_thermostat/temperature"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to secure MQTT broker via TLS!")
    else:
        print(f"Failed to connect, return code {rc}")

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect

# Configure TLS using the server certificate for validation
# Insecure set to True bypasses local self-signed certificate hostname matching for testing
client.tls_set(ca_certs="../server.crt")
client.tls_insecure_set(True)

# Connect to the broker on the secure port (8883)

client.connect(BROKER_ADDRESS, PORT, 60)
client.loop_start()

try:
    while True:
        payload = {
            "device_id": "thermo_01",
            "temperature": 22.5,
            "auth_token": "secure_secret_token_123"
        }
        
        # Publish encrypted message
        client.publish(TOPIC, json.dumps(payload))
        print(f"Published encrypted payload to {TOPIC}")
        
        time.sleep(3)
        
except KeyboardInterrupt:
    print("Stopping sensor script...")
    client.loop_stop()
    client.disconnect()