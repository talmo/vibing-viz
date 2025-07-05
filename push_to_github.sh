#!/bin/bash
# Script to push to GitHub after repository is created

echo "Pushing Vibing-Viz to GitHub..."

# Push to main branch
git push -u origin main

# Create and push initial tag
git tag -a v0.1.0 -m "Initial release of Vibing-Viz

Features:
- Real-time 3D visualization with PyGFX
- Qt5 interface with dockable panels
- Multi-track pose rendering
- Camera system with animations
- Video overlay support
- Environment rendering
- Video/image export
"

git push origin v0.1.0

echo "✓ Code pushed to GitHub"
echo "✓ Tag v0.1.0 created"
echo ""
echo "Next steps:"
echo "1. Enable GitHub Pages for documentation (optional)"
echo "2. Set up GitHub Actions secrets for PyPI publishing (optional)"
echo "3. Create a release from the v0.1.0 tag"
echo "4. Update repository settings (description, topics, etc.)"