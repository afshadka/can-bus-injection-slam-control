# can-bus-injection-slam-control
# 🛠️ CAN Bus Injection & SLAM Bot Control Handover

This project enables **manual motor control** of a robot via **CAN bus command injection**, with a safe and seamless **handover back to the SLAM or app control system**. Ideal for debugging, diagnostics, or intervention without disrupting odometry or SLAM.

---

## 🚀 Features

- ✅ Position mode motor control using CANopen SDOs  
- 🧭 Inject directional movement (forward/backward)
- ⛔ Emergency stop at any moment
- 🔁 Safe release of control to onboard SLAM/system
- 📡 SocketCAN (`can0`) based communication (Raspberry Pi, Jetson etc.)

---

## 🧠 Use Case

Useful for:
- Biped robots or mobile bots with CAN motor drivers
- Manual override testing in SLAM/ROS systems
- Scripted movement during demos or calibration
- Seamless return to automated control after injection

---

## 🧾 Requirements

- Linux-based board (e.g., Raspberry Pi, Jetson)
- Python 3.7+
- `python-can` library
- Motors that support CANopen SDO commands
- CAN interface active as `can0`

---

## ⚙️ Setup

```bash
sudo apt update
sudo apt install python3-pip
pip3 install python-can
