#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

uvicorn app.admin_panel_sqladmin:app --host 0.0.0.0 --port 8002 --reload