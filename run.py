import subprocess
import os
import time

# Function to run a Flask app in a separate process
def run_flask_app(script_name, port):
    env = os.environ.copy()
    env['FLASK_APP'] = script_name
    env['FLASK_ENV'] = 'development'  # Ensure we use development environment for auto-reload
    env['FLASK_RUN_PORT'] = str(port)
    return subprocess.Popen(['flask', 'run'], env=env)

app1_path = r"C:\Users\Pranav\Desktop\WP\app.py"
app2_path = r"C:\Users\Pranav\Desktop\WP\templates\app.py"

# Start both Flask apps
process1 = run_flask_app(app1_path, 5000) 
process2 = run_flask_app(app2_path, 5001)

print("Flask App is running")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Terminating Flask app...")
    process1.terminate()
    process2.terminate()
