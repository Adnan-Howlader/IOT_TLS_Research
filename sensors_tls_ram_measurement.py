import paho.mqtt.client as mqtt
import time
import json
import os
import psutil

# Broker configuration for End-to-End TLS
BROKER_ADDRESS = "localhost"
PORT = 8883
TOPIC = "home/smart_thermostat/temperature"

# Initialize psutil process handler for current script performance tracking
process = psutil.Process(os.getpid())

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to secure MQTT broker via TLS!")
    else:
        print(f"Failed to connect, return code {rc}")

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect

# Configure TLS using the server certificate for validation
client.tls_set(ca_certs="../server.crt")
client.tls_insecure_set(True)

print("Starting performance-tracked TLS sensor session...")

# 1. MEASURE STARTUP / CONNECTION COST
connect_start_time = time.perf_counter()

# Connect to the broker on the secure port (8883)
client.connect(BROKER_ADDRESS, PORT, 60)
client.loop_start()

connect_end_time = time.perf_counter()
startup_duration = connect_end_time - connect_start_time
print(f"[METRIC] Connection & TLS Handshake Duration: {startup_duration:.4f} seconds")

try:
    iteration = 0
    max_iterations = 15  # Run a sample batch of publishes for metric logging

    while iteration < max_iterations:
        payload = {
            "device_id": "thermo_01",
            "temperature": 22.5,
            "auth_token": "secure_secret_token_123"
        }
        
        message = json.dumps(payload)
        
        # 2. MEASURE WIRE-LEVEL PAYLOAD SIZE (Bytes)
        payload_bytes = len(message.encode('utf-8'))
        
        # Publish encrypted message
        client.publish(TOPIC, message)
        
        # 3. MEASURE SENSOR RESOURCE FOOTPRINT (CPU & Memory)
        current_cpu = process.cpu_percent(interval=None)
        current_mem = process.memory_info().rss / (1024 * 1024) # Resident Set Size in MB
        
        print(f"Run {iteration+1:02d} | Payload: {payload_bytes} bytes | CPU: {current_cpu}% | RAM: {current_mem:.2f} MB")
        
        iteration += 1
        time.sleep(3)
        
except KeyboardInterrupt:
    print("Stopping sensor script...")
finally:
    client.loop_stop()
    client.disconnect()
    
    # Final resource summary block
    final_mem = process.memory_info().rss / (1024 * 1024)
    print("\n" + "="*35)
    print(" TLS SENSOR PERFORMANCE METRICS SUMMARY")
    print("="*35)
    print(f"Startup / Handshake Time : {startup_duration:.4f} s")
    print(f"Payload Size (JSON)      : {payload_bytes} bytes")
    print(f"Final Memory Footprint   : {final_mem:.2f} MB RSS")
    print("="*35)