#!/bin/bash
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port ${API_PORT}