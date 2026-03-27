import sys
import os

# Add vendor dependencies to path
sys.path.insert(0, '/app/deps')
sys.path.insert(0, '/app')
os.environ['PYTHONPATH'] = '/app/deps:/app'

# Launch streamlit
sys.argv = [
    'streamlit', 'run', '/app/main.py',
    '--server.port', '8080',
    '--server.address', '0.0.0.0',
    '--server.headless', 'true',
    '--server.enableCORS', 'false',
]

from streamlit.web.cli import main
main()
