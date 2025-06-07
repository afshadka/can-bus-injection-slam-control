import can
import time
import struct
import math

# === Parameters ===
WHEEL_CIRCUM_MM = 550
ENC_COUNTS_PER_REV = 16384
can_interface = 'can0'
bus = can.interface.Bus(can_interface, interface='socketcan')

MOTOR1_ID = 0x601
MOTOR2_ID = 0x602

# === Utility Functions ===
def mm_to_counts(mm):
    return int((mm / WHEEL_CIRCUM_MM) * ENC_COUNTS_PER_REV)

def counts_to_bytes(counts):
    return list(struct.pack('<i', counts))

def send_sdo(can_id, data_bytes):
    msg = can.Message(arbitration_id=can_id, data=data_bytes, is_extended_id=False)
    try:
        bus.send(msg)
    except can.CanError as e:
        print(f"❌ CAN send error: {e}")

def enable_motor(node_id):
    base = 0x600 + (node_id & 0xFF)
    send_sdo(base, [0x2F, 0x60, 0x60, 0x00, 0x01, 0x00, 0x00, 0x00])  # Position mode
    time.sleep(0.02)
    send_sdo(base, [0x2B, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00])  # Shutdown
    time.sleep(0.02)
    send_sdo(base, [0x2B, 0x40, 0x60, 0x00, 0x0F, 0x00, 0x00, 0x00])  # Enable
    time.sleep(0.05)

def disable_motor(node_id):
    base = 0x600 + (node_id & 0xFF)
    send_sdo(base, [0x2B, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00])
    time.sleep(0.05)

def stop_motors():
    print("🛑 Stopping motors...")
    for node in [MOTOR1_ID, MOTOR2_ID]:
        send_sdo(node, [0x23, 0x7B, 0x60, 0x00] + [0x00] * 4)

def move_forward(distance_mm, speed_mmps):
    step_mm = 1
    delay = step_mm / speed_mmps
    total_counts = mm_to_counts(distance_mm)
    step_counts = mm_to_counts(step_mm)
    steps = math.ceil(abs(total_counts) / abs(step_counts))
    direction = 1 if total_counts >= 0 else -1

    print(f"➡ Moving {distance_mm}mm at {speed_mmps}mm/s in {steps} steps")
    for _ in range(steps):
        move_counts = direction * step_counts
        payload_m1 = [0x23, 0x7B, 0x60, 0x00] + counts_to_bytes(-move_counts)
        payload_m2 = [0x23, 0x7B, 0x60, 0x00] + counts_to_bytes(move_counts)
        send_sdo(MOTOR1_ID, payload_m1)
        send_sdo(MOTOR2_ID, payload_m2)
        time.sleep(delay)

def inject_control():
    print("⚙️ Injecting control...")
    enable_motor(1)
    enable_motor(2)

def release_control():
    print("🔄 Releasing control to SLAM system...")
    for node in [MOTOR1_ID, MOTOR2_ID]:
        base = 0x600 + (node & 0xFF)
        send_sdo(base, [0x2B, 0x40, 0x60, 0x00, 0x06, 0x00, 0x00, 0x00])  # Disable
        time.sleep(0.02)
        send_sdo(base, [0x2B, 0x7B, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00])  # Clear pos
        send_sdo(base, [0x2B, 0x60, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00])  # Reset mode
        send_sdo(base, [0x2B, 0x40, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00])  # Reset control
    print("✅ Control handed back.")

# === Main ===
if __name__ == "__main__":
    try:
        print("\n🟢 CAN Injection Control Ready")
        inject_control()
        while True:
            cmd = input("Enter 'move', 'stop', 'release', or 'exit': ").strip().lower()
            if cmd == 'move':
                dist = float(input("Distance (mm): "))
                speed = float(input("Speed (mm/s): "))
                move_forward(dist, speed)
            elif cmd == 'stop':
                stop_motors()
            elif cmd == 'release':
                stop_motors()
                release_control()
            elif cmd == 'exit':
                stop_motors()
                release_control()
                print("👋 Exiting.")
                break
            else:
                print("❓ Unknown command.")
    except KeyboardInterrupt:
        stop_motors()
        release_control()
        print("\n⛔ Interrupted. Motors stopped and control released.")
