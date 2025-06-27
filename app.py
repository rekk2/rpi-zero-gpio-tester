import os, json, time, threading, logging
from flask import Flask, render_template, request, redirect, url_for, flash
import RPi.GPIO as GPIO

# --- App Setup ---
app = Flask(__name__)
app.secret_key = 'secret'  # required for flashing messages

# Directory to store config files
CONFIG_FOLDER = './configs'
os.makedirs(CONFIG_FOLDER, exist_ok=True)

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)

# --- Logger Setup ---
logger = logging.getLogger('tester')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('tester.log')
fh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(fh)

# --- Global State ---
test_thread = None
test_params = {
    'running': False,
    'completed': False,
    'count': 0,
    'cycle': 0,
    'pins': {},
    'name': ''
}

def load_config(filename):
    with open(os.path.join(CONFIG_FOLDER, filename), 'r') as f:
        return json.load(f)

def save_config(filename, data):
    with open(os.path.join(CONFIG_FOLDER, filename), 'w') as f:
        json.dump(data, f, indent=2)

def delete_config(filename):
    os.remove(os.path.join(CONFIG_FOLDER, filename))

# --- Test Loop Function ---
def run_test():
    pins = test_params['pins']
    total = test_params['count']
    test_params['cycle'] = 0
    test_params['running'] = True
    test_params['completed'] = False

    # Initialize pins
    for p in pins:
        if p != 'pause':
            GPIO.setup(int(p), GPIO.OUT)
            GPIO.output(int(p), GPIO.LOW)

    while test_params['cycle'] < total and test_params['running']:
        for pin, delay in pins.items():
            if not test_params['running']:
                break
            if pin == 'pause':
                logger.info(f"Cycle {test_params['cycle']+1}/{total} - PAUSE for {delay}s")
                time.sleep(delay)
            else:
                GPIO.output(int(pin), GPIO.HIGH)
                logger.info(f"Cycle {test_params['cycle']+1}/{total} - GPIO {pin} ON for {delay}s")
                time.sleep(delay)
                GPIO.output(int(pin), GPIO.LOW)
            test_params['cycle'] += 1
            if test_params['cycle'] >= total:
                break

    # Cleanup pins
    for p in pins:
        if p != 'pause':
            GPIO.output(int(p), GPIO.LOW)

    test_params['running'] = False
    test_params['completed'] = True
    logger.info("Test finished")

# --- Flask Routes ---
@app.route('/', methods=['GET', 'POST'])
def index():
    configs = sorted(os.listdir(CONFIG_FOLDER))
    if request.method == 'POST':
        selected = request.form.get('config_file')
        if selected:
            cfg = load_config(selected)
            test_params['count'] = cfg.get('count', 0)
            test_params['pins'] = cfg.get('pins', {})
            test_params['name'] = cfg.get('name', '')
            global test_thread
            if not (test_thread and test_thread.is_alive()):
                test_thread = threading.Thread(target=run_test)
                test_thread.start()
            return redirect(url_for('status'))
    return render_template('index.html', params=test_params, configs=configs)

@app.route('/status')
def status():
    try:
        with open('tester.log') as f:
            lines = f.readlines()
        logs = lines[-50:]
    except FileNotFoundError:
        logs = []
    return render_template('status.html', params=test_params, logs=logs)

@app.route('/stop')
def stop():
    test_params['running'] = False
    return redirect(url_for('status'))

@app.route('/configs')
def config_list():
    configs = sorted(os.listdir(CONFIG_FOLDER))
    return render_template('configs.html', configs=configs)

@app.route('/configs/edit/<filename>', methods=['GET', 'POST'])
def config_edit(filename):
    if request.method == 'POST':
        name = request.form['name']
        count = int(request.form['count'])
        pins = {}
        # Existing pins
        for key in request.form:
            if key.startswith('pin_') and request.form[key].strip():
                parts = key.split('_')
                if len(parts) >= 2:
                    pin_num = parts[1]
                    try:
                        pins[pin_num] = float(request.form[key])
                    except ValueError:
                        flash(f'Invalid delay for pin {pin_num}')
        # New pin
        new_pin = request.form.get('new_pin')
        new_delay = request.form.get('new_delay')
        if new_pin and new_delay:
            try:
                pins[str(int(new_pin))] = float(new_delay)
            except ValueError:
                flash('Invalid new pin or delay')
        # Optional pause step
        pause_dur = request.form.get('pause_duration')
        if pause_dur:
            try:
                pins['pause'] = float(pause_dur)
            except ValueError:
                flash('Invalid pause duration')
        data = {'name': name, 'count': count, 'pins': pins}
        save_config(filename, data)
        flash(f'Saved {filename}')
        return redirect(url_for('config_list'))
    config = load_config(filename)
    return render_template('edit_config.html', config=config, filename=filename)

@app.route('/configs/delete/<filename>')
def config_delete(filename):
    delete_config(filename)
    flash(f'Deleted {filename}')
    return redirect(url_for('config_list'))

@app.route('/configs/create', methods=['GET', 'POST'])
def config_create():
    if request.method == 'POST':
        name = request.form['name']
        count = int(request.form['count'])
        pins = {}
        # Existing pins
        for key in request.form:
            if key.startswith('pin_') and request.form[key].strip():
                parts = key.split('_')
                if len(parts) >= 2:
                    pin_num = parts[1]
                    try:
                        pins[pin_num] = float(request.form[key])
                    except ValueError:
                        flash(f'Invalid delay for pin {pin_num}')
        # New pin
        new_pin = request.form.get('new_pin')
        new_delay = request.form.get('new_delay')
        if new_pin and new_delay:
            try:
                pins[str(int(new_pin))] = float(new_delay)
            except ValueError:
                flash('Invalid new pin or delay')
        # Optional pause step
        pause_dur = request.form.get('pause_duration')
        if pause_dur:
            try:
                pins['pause'] = float(pause_dur)
            except ValueError:
                flash('Invalid pause duration')
        data = {'name': name, 'count': count, 'pins': pins}
        filename = name.replace(' ', '_').lower() + '.json'
        save_config(filename, data)
        flash(f'Created {filename}')
        return redirect(url_for('config_list'))
    return render_template('edit_config.html', config=None, filename=None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
