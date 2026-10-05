import paho.mqtt.client as mqtt
import time
import json
import os
import psutil

# Configuration for your local Docker MQTT broker
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "home/smart_thermostat/temperature"

# Initialize psutil process handler for the current running script
process = psutil.Process(os.getpid())

# Initialize the MQTT client
client = mqtt.Client()

try:
    print(f"Connecting to MQTT broker at {BROKER_HOST}:{BROKER_PORT}...")
    
    # Measure CPU and memory before connection
    cpu_before = process.cpu_percent(interval=None)
    mem_before = process.memory_info().rss / (1024 * 1024) # in MB
    
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()  # Start the background network thread
    
    print("IoT Sensor simulation started. Publishing telemetry...")

    # Track resources over a short run or specific iterations for your paper
    iteration = 0
    max_iterations = 10  # Sample across 10 publish cycles

    while iteration < max_iterations:
        payload = {
            "device_id": "thermo_01",
            "temperature": 22.5,
            "status": "ACTIVE",
            "auth_token": "plaintext_secret_123"
        }
        
        message = json.dumps(payload)
        client.publish(TOPIC, message)
        
        # Measure current resource footprint of the script
        current_cpu = process.cpu_percent(interval=None)
        current_mem = process.memory_info().rss / (1024 * 1024) # RSS in MB
        
        print(f"Run {iteration+1:02d} | Published | CPU Usage: {current_cpu}% | Memory (RSS): {current_mem:.2f} MB")
        
        iteration += 1
        time.sleep(3)

except KeyboardInterrupt:
    print("\nStopping sensor simulation...")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    client.loop_stop()
    client.disconnect()
    
    # Final resource summary
    final_mem = process.memory_info().rss / (1024 * 1024)
    print("\n" + "="*30)
    print(" SENSOR RESOURCE FOOTPRINT SUMMARY")
    print("="*30)
    print(f"Final Memory (RSS) : {final_mem:.2f} MB")
    print("="*30)