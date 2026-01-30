#!/bin/bash
# Script to generate TypeScript types from FastAPI OpenAPI spec
# Usage: ./scripts/generate-api-types.sh [backend_url]

BACKEND_URL="${1:-http://localhost:8000}"
OUTPUT_DIR="src/lib/models/generated"
OUTPUT_FILE="$OUTPUT_DIR/api.ts"

echo "🔄 Generating TypeScript types from OpenAPI spec..."
echo "   Backend URL: $BACKEND_URL"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Fetch OpenAPI spec and generate types
npx openapi-typescript "$BACKEND_URL/openapi.json" -o "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Types generated successfully: $OUTPUT_FILE"
else
    echo "❌ Failed to generate types. Is the backend running?"
    exit 1
fi
