#!/bin/bash

# Create necessary directories
mkdir -p .github/copilot
mkdir -p .github/copilot/sessions

echo "📊 Generating Copilot project context..."

# 1. Generate a complete file listing (excluding common directories to ignore)
echo "## Project File Structure" > .github/copilot/project_structure.md
echo "\`\`\`" >> .github/copilot/project_structure.md
find . -type f -not -path "*/node_modules/*" -not -path "*/\.*" \
  -not -path "*/venv/*" -not -path "*/__pycache__/*" \
  -not -path "*/build/*" -not -path "*/dist/*" | sort >> .github/copilot/project_structure.md
echo "\`\`\`" >> .github/copilot/project_structure.md

# 2. Capture key file contents
echo "## Key Files Content" > .github/copilot/key_files.md

# Backend files
echo "### Backend Entry Point (main.py)" >> .github/copilot/key_files.md
echo "\`\`\`python" >> .github/copilot/key_files.md
cat main.py >> .github/copilot/key_files.md
echo "\`\`\`" >> .github/copilot/key_files.md

# Only include files that exist
if [ -f backend/routes/property.py ]; then
  echo "### Property Routes" >> .github/copilot/key_files.md
  echo "\`\`\`python" >> .github/copilot/key_files.md
  cat backend/routes/property.py >> .github/copilot/key_files.md
  echo "\`\`\`" >> .github/copilot/key_files.md
fi

if [ -f backend/mashvisor_search.py ]; then
  echo "### Mashvisor Integration" >> .github/copilot/key_files.md
  echo "\`\`\`python" >> .github/copilot/key_files.md
  cat backend/mashvisor_search.py >> .github/copilot/key_files.md
  echo "\`\`\`" >> .github/copilot/key_files.md
fi

# Frontend files (main components)
if [ -f frontend/src/App.jsx ]; then
  echo "### Main App Component" >> .github/copilot/key_files.md
  echo "\`\`\`jsx" >> .github/copilot/key_files.md
  cat frontend/src/App.jsx >> .github/copilot/key_files.md
  echo "\`\`\`" >> .github/copilot/key_files.md
fi

# 3. Create a session log entry
DATE=$(date +"%Y-%m-%d")
echo "# Session: $DATE" > .github/copilot/sessions/session_$DATE.md
echo "## Tasks Completed" >> .github/copilot/sessions/session_$DATE.md
echo "- Updated Copilot context" >> .github/copilot/sessions/session_$DATE.md
echo "" >> .github/copilot/sessions/session_$DATE.md
echo "## Notes" >> .github/copilot/sessions/session_$DATE.md
echo "Add session notes here" >> .github/copilot/sessions/session_$DATE.md

# 4. Copy the project map for easy reference
mkdir -p .github/copilot/docs
if [ -f docs/project-map.md ]; then
  cp docs/project-map.md .github/copilot/docs/
fi

echo "✅ Copilot context updated successfully!"
echo "Run this script at the start of each session to refresh Copilot's understanding of your project."
