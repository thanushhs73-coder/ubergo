#!/bin/bash
# Railway startup script
PORT=${PORT:-8000}
exec uvicorn admin_app.main:app --host 0.0.0.0 --port $PORT
