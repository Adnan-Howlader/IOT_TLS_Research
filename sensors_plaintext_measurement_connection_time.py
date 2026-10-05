import paho.mqtt.client as mqtt
import time
import json
import statistics

# Configuration for your local Docker MQTT broker (Plaintext Edge/Broker)
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "home/smart_thermostat/temperature"
NUM_RUNS = 15  # Target: 10-20 independent sessions

durations = []

print(f"Starting startup cost measurement (Plaintext) across {NUM_RUNS} sessions...")

for i in range(1, NUM_RUNS + 1):
    # Initialize a fresh client each run to capture true TCP connect & MQTT handshake cost
    client = mqtt.Client()
    
    payload = {
        "device_id": "thermo_01",
        "temperature": 22.5,
        "status": "ACTIVE",
        "auth_token": "plaintext_secret_123"
    }
    message = json.dumps(payload)
    
    # Start high-resolution timer right before connection attempt
    start_time = time.time()
    
    try:
        # 1. Connect (TCP handshake + MQTT CONNECT/CONNACK)
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        
        # 2. Publish one single message
        client.publish(TOPIC, message)
        
        # Process network traffic briefly to flush the message out over the socket
        client.loop(timeout=0.2)
        
        # 3. Cleanly disconnect
        client.disconnect()
        
        # Stop timer
        end_time = time.time()
        duration = end_time - start_time
        durations.append(duration)
        
        print(f"Run {i:02d}: {duration:.4f} seconds")
        
    except Exception as e:
        print(f"Run {i:02d} failed: {e}")
    
    # Brief cooldown delay between test iterations
    time.sleep(0.5)

# Calculate and display results
if durations:
    median_duration = statistics.median(durations)
    print("\n" + "="*35)
    print(" PLAINTEXT STARTUP COST RESULTS")
    print("="*35)
    print(f"Successful Runs : {len(durations)} / {NUM_RUNS}")
    print(f"Median Duration : **{median_duration:.4f} seconds**")
    print(f"All Measurements: {[round(d, 4) for d in durations]}")
    print("="*35)
else:
    print("No successful runs recorded. Check broker connectivity.")