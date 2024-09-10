import sys
import os

# PYTHONPATH for project directories
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)


from scripts.dbt_run import dbt_trigger

dbt_trigger()