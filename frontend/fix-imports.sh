#!/bin/bash

echo "=== Fixing Vite import resolution issues ==="
echo ""

# Step 1: Remove all caches and generated files
echo "Step 1: Removing node_modules, caches, and lock files..."
rm -rf node_modules
rm -rf .vite
rm -rf dist
rm -f package-lock.json
echo "✓ Cleanup complete"
echo ""

# Step 2: Clear npm cache
echo "Step 2: Clearing npm cache..."
npm cache clean --force
echo "✓ npm cache cleared"
echo ""

# Step 3: Reinstall dependencies
echo "Step 3: Reinstalling dependencies..."
npm install
echo "✓ Dependencies installed"
echo ""

# Step 4: Verify critical files exist
echo "Step 4: Verifying critical files..."
if [ -f "src/lib/utils.ts" ]; then
    echo "✓ src/lib/utils.ts exists"
else
    echo "✗ ERROR: src/lib/utils.ts is missing!"
    exit 1
fi

if [ -f "tsconfig.json" ]; then
    echo "✓ tsconfig.json exists"
else
    echo "✗ ERROR: tsconfig.json is missing!"
    exit 1
fi

if [ -f "vite.config.ts" ]; then
    echo "✓ vite.config.ts exists"
else
    echo "✗ ERROR: vite.config.ts is missing!"
    exit 1
fi
echo ""

echo "=== Setup complete! ==="
echo ""
echo "Now run: npm run dev"
echo ""
