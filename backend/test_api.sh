#!/bin/bash
echo "Testing API endpoints..."

echo "\\n 1. Health Check:"
curl http://localhost:3000/api/health

echo "\\n 2. Create Participant:"
curl -X POST http://localhost:3000/api/participants/ \
  -H "Content-Type: application/json" \
  -d '{"participant_code":"TEST001","native_language":"English"}'

echo "\\n 3. List Participants:"
curl http://localhost:3000/api/participants/

echo "\\n 4. List Videos:"
curl http://localhost:3000/api/videos/