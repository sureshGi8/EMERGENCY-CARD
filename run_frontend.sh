#!/bin/bash
echo "================================="
echo "Starting Emergency Card Frontend"
echo "================================="
echo ""
echo "Open your browser: http://localhost:3000"
echo ""
cd frontend
python3 -m http.server 3000
