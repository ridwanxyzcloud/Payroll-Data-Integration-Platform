import sys
import os

# PYTHONPATH for project directories
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from helpers.metrics_server import start_metrics_server, test_server


start_metrics_server(port=8001)