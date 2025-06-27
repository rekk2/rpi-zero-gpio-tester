Flask GPIO Tester

A touchscreen-friendly Raspberry Pi Zero W application for automated GPIO testing and solenoid control.

Features

Configurable Test Sequences: Define ordered steps of GPIO activations and optional pauses with per-pin durations.

Save & Manage Profiles: Create, edit, load, and delete JSON-based test configurations via a simple UI.

Visual Step Preview: See all steps rendered as colored blocks (green for GPIO pulses, purple for pauses).

Live Status & Logs: View real-time cycle counts and the latest 50 log entries, auto-refreshing every few seconds.

Touchscreen Optimized: Large buttons and inputs designed for 320×240 to 800×480 touch displays.

GPIO Pinout Reference: Built-in static pinout image to quickly identify header pins and their BCM numbers.

Prerequisites

Raspberry Pi Zero W running Raspberry Pi OS (Bookworm or later).

Python 3 installed (with python3-full).

A display or touchscreen attached to the Pi (optional but recommended).

Installation

Clone the repository

git clone https://github.com/your-username/flask-gpio-tester.git
cd flask-gpio-tester

Install system packages

sudo apt update
sudo apt install -y python3-venv python3-full

Create a Python virtual environment

python3 -m venv venv

Activate the virtual environment

source venv/bin/activate

Install Python dependencies

Note: On Raspberry Pi Zero W with limited memory, append --no-cache-dir --use-pep517 to your pip install commands to avoid out-of-memory or build errors.

pip install --upgrade pip setuptools wheel
pip install flask RPi.GPIO --no-cache-dir --use-pep517

Set up application folders

mkdir configs
mkdir static

Add GPIO pinout image

Place your pinout.png in the static/ directory:

cp path/to/pinout.png static/

Running the App

Development Mode

Ensure the virtual environment is activated:

source venv/bin/activate

Start the Flask app:

python app.py

Open a browser to http://<pi-ip>:5000 to access the UI.

Production Mode (systemd Service)

Create a systemd service file:

sudo tee /etc/systemd/system/tester.service > /dev/null << 'EOF'
[Unit]
Description=Flask GPIO Tester
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/flask-gpio-tester
ExecStart=/home/pi/flask-gpio-tester/venv/bin/python /home/pi/flask-gpio-tester/app.py
Environment="PATH=/home/pi/flask-gpio-tester/venv/bin"
Restart=always

[Install]
WantedBy=multi-user.target
EOF

Enable and start the service:

sudo systemctl daemon-reload
sudo systemctl enable tester.service
sudo systemctl start tester.service

Check status and logs:

sudo systemctl status tester.service
sudo journalctl -u tester.service -f

Access the web UI at http://<pi-ip>:5000.

Usage

Manage Configs: Navigate to Manage Configs to create, edit, or delete test profiles.

Start a Test: Select a configuration on the main page and click Start Test.

Real-Time Monitoring: View cycle count and logs on the Status & Logs page.

Touch Controls: Optimized buttons and inputs for touchscreen use.

License

This project is released under the MIT License. Feel free to adapt and extend it for your needs.

