#!/bin/bash
# Quick test script for Stremio addon

echo "🎬 Testing Stremio Addon Endpoints..."
echo ""

# Test 1: Root endpoint
echo "1. Testing root endpoint..."
curl -s http://localhost:7000/ | python3 -m json.tool
echo ""

# Test 2: Manifest
echo "2. Testing manifest..."
curl -s http://localhost:7000/manifest.json | python3 -m json.tool
echo ""

# Test 3: Stream (Naruto Example)
echo "3. Testing stream endpoint (Naruto S01E01)..."
curl -s http://localhost:7000/stream/series/tt0409591:1:1.json | python3 -m json.tool | head -30
echo ""

echo "✅ Test complete!"
echo "If all tests pass, add this to Stremio:"
echo "http://localhost:7000/manifest.json"
