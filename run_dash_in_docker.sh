#!/bin/bash
# Run the Dash app inside the Docker container on port 8050

echo "🚀 Starting Dash Interactive Reports in Docker..."
echo "📊 The app will be available at: http://localhost:8050"
echo ""

# Run the standalone Dash app inside the backend container
docker exec -it mintly_backend python /app/run_dash_standalone.py

