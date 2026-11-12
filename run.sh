#!/usr/bin/env bash
# Startup script for Zamp Flow AP Reconciliation Engine
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "  🚀 Starting Zamp Flow: Autonomous AP Engine"
echo "  📍 Local URL: http://localhost:8000"
echo "  🛠️  Problem Statement: PS-1 (Finance / AP - Invoice to Decision)"
echo "=========================================================="

python3 -m uvicorn server:app --host 0.0.0.0 --port 8000
