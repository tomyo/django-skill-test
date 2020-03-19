#!/bin/bash
set -euo pipefail

if [ -v DEV_MODE ]; then
    python manage.py migrate
fi

exec python server.py