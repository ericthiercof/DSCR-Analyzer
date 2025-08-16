# DSCR Property Analyzer Project Map

## Project Structure Overview
- `/frontend` - React frontend application
- `/backend` - FastAPI backend service
- `/main.py` - Backend entry point
- `/docs` - Project documentation
- `/.github/copilot` - Copilot context information

## Key Frontend Components
- `App.jsx` - Main application component
- `SearchForm.jsx` - Property search form with interest rate controls
- `PropertyList.jsx` - Displays property results with DSCR calculations
- `PropertyDetails.jsx` - Detailed view of a selected property
- `RentalComps.jsx` - Displays rental comps for a property

## Key Backend Components
- `routes/property.py` - Property endpoints for search and comps
- `mashvisor_search.py` - Mashvisor API integration for rental comps
- `models/property.py` - Property data models and validation
- `services/zillow.py` - Zillow API integration for property search
- `services/finance.py` - Financial calculations for mortgage payments and DSCR

## API Endpoints
- `POST /api/search` - Search for properties
- `POST /api/property-comps` - Get rental comps for a property
- `POST /api/search-with-cache` - Search with neighborhood caching

## Data Flow
1. User enters search criteria and interest rate in SearchForm
2. Backend searches for properties using Zillow API
3. PropertyList displays results and calculates DSCR using the interest rate
4. User can click "Long term rental comps" on a property
5. Backend fetches neighborhood data and rental comps from Mashvisor
6. RentalComps component displays comparable properties

## Future Enhancements
- Property analysis with machine learning predictions
- User authentication and saved property lists
- Neighborhood data caching and analysis

## 3. Update the Script to Include To-Do List

```bash
# Update the context script to include the to-do list
sed -i '/echo "✅ Copilot context updated successfully!"/i \
# 5. Copy the to-do list for easy reference\
if [ -f .github/copilot/tasks/todo.md ]; then\
  cp .github/copilot/tasks/todo.md .github/copilot/\
fi\
' update-copilot-context.sh
```
