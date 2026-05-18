#!/bin/sh
set -eu

api_url=${VITE_API_URL:-http://localhost:8000/api/v1}
escaped_api_url=$(printf '%s' "$api_url" | sed 's/\\/\\\\/g; s/"/\\"/g')

cat > /usr/share/nginx/html/runtime-env.js <<EOF
window.__ENV__ = {
  VITE_API_URL: "${escaped_api_url}"
};
EOF
