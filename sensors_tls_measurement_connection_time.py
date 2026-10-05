import paho.mqtt.client as mqtt
import time
import json
import statistics

# Broker configuration for End-to-End TLS
BROKER_ADDRESS = "localhost"
PORT = 8883
TOPIC = "home/smart_thermostat/temperature"
NUM_RUNS = 15  # Number of test iterations (fits your 10-20 requirement)

durations = []

print(f"Starting startup cost measurement ({NUM_RUNS} independent sessions)...")

for i in range(1, NUM_RUNS + 1):
    # Initialize a fresh client each time to capture true connection + TLS handshake cost
    client = mqtt.Client()
    
    # Configure TLS security settings
    client.tls_set(ca_certs="../server.crt")
    client.tls_insecure_set(True)
    
    payload = {
        "device_id": "thermo_01",
        "temperature": 22.5,
        "auth_token": "secure_secret_token_123"
    }
    
    # Start the high-resolution timer right before connection attempt
    start_time = time.time()
    
    try:
        # 1. Connect (includes TCP handshake + TLS negotiation + MQTT CONNACK)
        client.connect(BROKER_ADDRESS, PORT, 60)
        
        # 2. Publish one single message
        client.publish(TOPIC, json.dumps(payload))
        
        # Process network traffic loop briefly to ensure packet is sent out over TLS socket
        client.loop(timeout=0.2)
        
        # 3. Disconnect cleanly
        client.disconnect()
        
        # Stop timer
        end_time = time.time()
        duration = end_time - start_time
        durations.append(duration)
        
        print(f"Run {i:02d}: {duration:.4f} seconds")
        
    except Exception as e:
        print(f"Run {i:02d} failed: {e}")
    
    # Brief cooldown delay between connection attempts
    time.sleep(0.5)

# Calculate and display results
if durations:
    median_duration = statistics.median(durations)
    print("\n" + "="*30)
    print(" EXPERIMENT RESULTS (STARTUP COST)")
    print("="*30)
    print(f"Successful Runs : {len(durations)} / {NUM_RUNS}")
    print(f"Median Duration : **{median_duration:.4f} seconds**")
    print(f"All Measurements: {[round(d, 4) for d in durations]}")
    print("="*30)
else:
    print("No successful runs recorded. Check broker connectivity.")