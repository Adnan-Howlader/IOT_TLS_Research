import paho.mqtt.client as mqtt
import time
import json

# Configuration for your local Docker MQTT broker
BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "home/smart_thermostat/temperature"

# Initialize the MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

# Track metrics for average calculation
publish_cpu_costs = []
max_iterations = 15

try:
    print(f"Connecting to MQTT broker at {BROKER_HOST}:{BROKER_PORT}...")
    
    # 1. MEASURE CONNECTION / SETUP CPU TIME
    cpu_start = time.process_time()
    
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()  # Start the background network thread
    
    cpu_end = time.process_time()
    connection_cpu_ms = (cpu_end - cpu_start) * 1000  # Convert to milliseconds
    
    print(f"[BENCHMARK] Session Connection CPU Time: {connection_cpu_ms:.2f} ms")
    print("IoT Sensor simulation started. Publishing telemetry...\n")

    iteration = 0
    while iteration < max_iterations:
        payload = {
            "device_id": "thermo_01",
            "temperature": 22.5,
            "status": "ACTIVE",
            "auth_token": "plaintext_secret_123"
        }
        
        # 2. MEASURE PURE STEADY-STATE PUBLISH CPU TIME (Isolated)
        pub_cpu_start = time.process_time()
        
        message = json.dumps(payload)
        client.publish(TOPIC, message)
        
        pub_cpu_end = time.process_time()
        publish_cpu_us = (pub_cpu_end - pub_cpu_start) * 1_000_000  # Convert to microseconds (µs)
        
        publish_cpu_costs.append(publish_cpu_us)
        
        print(f"Run {iteration+1:02d} | Publish CPU Cost: {publish_cpu_us:.2f} µs")
        
        iteration += 1
        # Keep the pacing sleep OUTSIDE the measurement timer
        time.sleep(3)

except KeyboardInterrupt:
    print("\nStopping sensor simulation...")
finally:
    client.loop_stop()
    client.disconnect()
    
    # 3. CALCULATE AND PRINT AVERAGES
    if publish_cpu_costs:
        avg_publish_cpu = sum(publish_cpu_costs) / len(publish_cpu_costs)
        print("\n" + "="*40)
        print(" PERFORMANCE BENCHMARK SUMMARY (AVERAGES)")
        print("="*40)
        print(f"Connection/Handshake CPU Time : {connection_cpu_ms:.2f} ms")
        print(f"Average Publish CPU Cost      : {avg_publish_cpu:.2f} µs")
        print("="*40)
    else:
        print("Session closed successfully.")