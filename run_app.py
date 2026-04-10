import os
import sys

# Set PYTHONPATH environment variable to include the deps directory before exec
os.environ['PYTHONPATH'] = '/app/deps:/app'

# Exec into Python module streamlit. Force global.developmentMode to false to avoid AssertionError.
os.execv(sys.executable, [
    'python3', '-m', 'streamlit', 'run', 'main.py',
    '--server.port', '8080',
    '--server.address', '0.0.0.0',
    '--server.enableCORS', 'false',
    '--server.enableXsrfProtection', 'false'
])


