import paho.mqtt.client as mqtt
import time
import json

# Broker configuration for End-to-End TLS
BROKER_ADDRESS = "localhost"
PORT = 8883
TOPIC = "home/smart_thermostat/temperature"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected successfully to secure MQTT broker via TLS!")
    else:
        print(f"Failed to connect, return code {rc}")

# Initialize MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect

# Configure TLS using the server certificate for validation
# Insecure set to True bypasses local self-signed certificate hostname matching for testing
client.tls_set(ca_certs="../server.crt")
client.tls_insecure_set(True)

# Track metrics for average calculation
publish_cpu_costs = []
max_iterations = 15

try:
    print(f"Connecting to secure MQTT broker at {BROKER_ADDRESS}:{PORT}...")
    
    # 1. MEASURE CONNECTION / TLS HANDSHAKE CPU TIME
    # time.process_time() captures active CPU cycles spent on socket and TLS negotiation
    cpu_start = time.process_time()
    
    client.connect(BROKER_ADDRESS, PORT, 60)
    client.loop_start()  # Start the background network thread
    
    cpu_end = time.process_time()
    connection_cpu_ms = (cpu_end - cpu_start) * 1000  # Convert to milliseconds
    
    print(f"[BENCHMARK] TLS Connection/Handshake CPU Time: {connection_cpu_ms:.2f} ms\n")
    print("TLS Sensor simulation started. Publishing telemetry...")

    iteration = 0
    while iteration < max_iterations:
        payload = {
            "device_id": "thermo_01",
            "temperature": 22.5,
            "auth_token": "secure_secret_token_123"
        }
        
        message = json.dumps(payload)
        
        # 2. MEASURE STEADY-STATE PUBLISH CPU TIME (Per Message)
        pub_cpu_start = time.process_time()
        
        client.publish(TOPIC, message)
        time.sleep(0.001)  # Brief yield to allow network thread processing
        
        pub_cpu_end = time.process_time()
        publish_cpu_us = (pub_cpu_end - pub_cpu_start) * 1_000_000  # Convert to microseconds (µs)
        
        publish_cpu_costs.append(publish_cpu_us)
        
        print(f"Run {iteration+1:02d} | Publish CPU Cost: {publish_cpu_us:.2f} µs | Payload: {message}")
        
        iteration += 1
        time.sleep(3)
        
except KeyboardInterrupt:
    print("\nStopping sensor script...")
finally:
    client.loop_stop()
    client.disconnect()
    
    # 3. CALCULATE AND PRINT AVERAGES
    if publish_cpu_costs:
        avg_publish_cpu = sum(publish_cpu_costs) / len(publish_cpu_costs)
        print("\n" + "="*45)
        print(" TLS PERFORMANCE BENCHMARK SUMMARY (AVERAGES)")
        print("="*45)
        print(f"TLS Connection/Handshake CPU Time : {connection_cpu_ms:.2f} ms")
        print(f"Average Steady-State Publish Cost : {avg_publish_cpu:.2f} µs")
        print("="*45)
    else:
        print("Session closed successfully.")