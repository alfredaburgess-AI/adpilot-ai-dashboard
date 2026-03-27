#!/bin/sh
export PYTHONPATH=/app/vendor:/app:${PYTHONPATH:-}
export PATH=/app/vendor/bin:${PATH:-/usr/local/bin:/usr/bin:/bin}
exec python3 -m streamlit run /app/main.py \
  --server.port 8080 \
  --server.address 0.0.0.0 \
  --server.headless true \
  --server.enableCORS false
