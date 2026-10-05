import paho.mqtt.client as mqtt
import time
import json

# Configuration for your local Docker MQTT broker
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "home/smart_thermostat/temperature"

# Initialize the MQTT client
client = mqtt.Client()

try:
    # Connect to the local Docker broker
    print(f"Connecting to MQTT broker at {BROKER_HOST}:{BROKER_PORT}...")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()  # Start the background network thread
    
    print("IoT Sensor simulation started. Publishing telemetry...")

    while True:
        # Simulate a telemetry payload containing cleartext data and credentials
        payload = {
            "device_id": "thermo_01",
            "temperature": 22.5,
            "status": "ACTIVE",
            "auth_token": "plaintext_secret_123"  # Simulating the cleartext vulnerability
        }
        
        message = json.dumps(payload)
        client.publish(TOPIC, message)
        print(f"Published to [{TOPIC}]: {message}")
        
        time.sleep(3) # Wait 3 seconds before sending the next reading

except KeyboardInterrupt:
    print("\nStopping sensor simulation...")
    client.loop_stop()
    client.disconnect()
except Exception as e:
    print(f"An error occurred: {e}")