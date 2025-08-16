# DSCR Property Analyzer Project Map

## Project Structure Overview
- `/frontend` - React frontend application
- `/backend` - FastAPI backend service
- `/main.py` - Backend entry point
- `/docs` - Project documentation and agent interaction logs

## Key Frontend Components
- `App.jsx` - Main application component
- `SearchForm.jsx` - Property search form with interest rate controls
- `PropertyList.jsx` - Displays property results with DSCR calculations

## Key Backend Components
- `routes/property.py` - Property endpoints
- `mashvisor_search.py` - Mashvisor API integration
- `models/property.py` - Property data models

## Data Flow
1. User enters search criteria and interest rate in SearchForm
2. Backend searches for properties using Zillow/Mashvisor
3. PropertyList displays results and calculates DSCR using the interest rate

## Documentation
- `project-map.md` - This project structure overview
- `copilot-agent-log.md` - GitHub Copilot agent interaction history
