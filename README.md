# Flask GPIO Tester

A touchscreen-friendly Raspberry Pi Zero W application for automated GPIO testing and solenoid control.

## Features

- **Configurable Test Sequences**: Define ordered steps of GPIO activations and optional pauses with per-pin durations.
- **Save & Manage Profiles**: Create, edit, load, and delete JSON-based test configurations via a simple UI.
- **Visual Step Preview**: See all steps rendered as colored blocks (green for GPIO pulses, purple for pauses).
- **Live Status & Logs**: View real-time cycle counts and the latest 50 log entries, auto-refreshing every few seconds.
- **Touchscreen Optimized**: Large buttons and inputs designed for 320×240 to 800×480 touch displays.
- **GPIO Pinout Reference**: Built-in static pinout image to quickly identify header pins and their BCM numbers.

## Prerequisites

- Raspberry Pi Zero W running Raspberry Pi OS (Bookworm or later)
- Python 3 (including `python3-full`)
- `git` installed to clone the repository
- (Optional) A touchscreen attached to the Pi for best UX

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/flask-gpio-tester.git
cd flask-gpio-tester
```

### 2. Install system packages

```bash
sudo apt update
sudo apt install -y python3-venv python3-full git
```

### 3. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Python dependencies

> **CAUTION**: On Raspberry Pi Zero W, use `--no-cache-dir --use-pep517` to avoid memory issues

```bash
pip install --upgrade pip setuptools wheel
pip install flask RPi.GPIO --no-cache-dir --use-pep517
```

### 5. Set up application directories

```bash
mkdir configs
mkdir static
```

### 6. Add your GPIO pinout image

Place your `pinout.png` into the `static/` folder:

```bash
cp /path/to/pinout.png static/
```

## Running the App

### Development Mode

1. Ensure your virtual environment is active:

   ```bash
   source venv/bin/activate
   ```
2. Run the Flask application:

   ```bash
   python app.py
   ```
3. Open your browser to:

   ```
   http://<pi-ip-address>:5000
   ```

### Production Mode (systemd service)

1. Create the systemd service file:

   ```bash
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
   ```

2. Enable and start the service:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable tester.service
   sudo systemctl start tester.service
   ```

3. Monitor status and logs:

   ```bash
   sudo systemctl status tester.service
   sudo journalctl -u tester.service -f
   ```

4. Access the web UI at:

   ```
   http://<pi-ip-address>:5000
   ```

## Usage

1. **Manage Configs**: Navigate to **Manage Configs** to create, edit, delete, and add steps to profiles.
2. **Start a Test**: Select a configuration on the main page and click **Start Test**.
3. **Live Monitoring**: View cycle count and logs on the **Status & Logs** page.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
