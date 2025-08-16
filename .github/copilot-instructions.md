# DSCR Investment Property Analyzer

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Project Overview
DSCR Investment Property Analyzer is a real estate investment analysis platform with a FastAPI backend and React frontend. The application helps mortgage brokers and realtors analyze investment properties by calculating DSCR (Debt Service Coverage Ratio) and providing property search functionality.

## Working Effectively

### Initial Setup
Bootstrap, build, and test the repository:

1. **Check Python version** (Python 3.11+ required):
   ```bash
   python3 --version  # Should be 3.11+
   ```

2. **Create and activate Python virtual environment**:
   ```bash
   python3 -m venv .venv  # Takes ~3 seconds
   source .venv/bin/activate
   ```

3. **Install backend dependencies**:
   ```bash
   pip3 install -r backend/requirements.txt  # Takes ~60 seconds - NEVER CANCEL
   ```
   **NOTE**: If you encounter network timeouts from PyPI, retry with: `pip3 install --timeout 300 -r backend/requirements.txt`

4. **Create environment file** (required for backend to start):
   ```bash
   # Create .env in repository root with your API keys:
   cat > .env << EOF
   MASHVISOR_API_KEY=your_mashvisor_api_key_here
   ZILLOW_API_KEY=your_zillow_api_key_here
   ZILLOW_API_HOST=zillow-com1.p.rapidapi.com
   SERPAPI_KEY=your_serpapi_key_here
   SECRET_KEY=your_jwt_secret_key_here
   EOF
   ```
   **NOTE**: For testing without real API keys, use placeholder values like `test_key_placeholder`

5. **Check Node.js version** (Node.js 18+ recommended):
   ```bash
   node --version && npm --version
   ```

6. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install  # Takes ~3-4 minutes - NEVER CANCEL. Set timeout to 300+ seconds.
   cd ..
   ```

### Running the Application

**ALWAYS run the backend first, then the frontend.**

#### Start Backend API
```bash
source .venv/bin/activate
python main.py  # Starts on http://localhost:8000
```
- Takes ~5-10 seconds to start
- API docs available at: http://localhost:8000/docs
- Health check: http://localhost:8000

#### Start Frontend (in separate terminal)
```bash
cd frontend
npm start  # Starts on http://localhost:3000, takes ~15-20 seconds
```

### Building and Testing

#### Backend Testing
```bash
# Test API health check
python test_api.py

# Test API endpoints with curl
./debug_api.sh

# Manual API test with proper field names
curl -X POST http://127.0.0.1:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"city":"jackson", "state":"MI", "down_payment":20, "interest_rate":7, "min_price":150000, "max_price":1500000}'
```

#### Frontend Building and Testing
```bash
cd frontend

# Build for production
npm run build  # Takes ~8-10 seconds. NEVER CANCEL.

# Run linting (ESLint is integrated)
npx eslint src/  # Check for code style issues

# Note: npm test has configuration issues with axios imports
# Frontend tests are not currently functional due to Jest/axios ESM compatibility
```

## Validation Scenarios

**ALWAYS test these scenarios after making changes:**

1. **Backend Health Check**:
   - Start backend with `python main.py`
   - Verify API responds at http://localhost:8000
   - Check API docs load at http://localhost:8000/docs

2. **Frontend-Backend Integration**:
   - Start both backend and frontend
   - Access frontend at http://localhost:3000
   - Verify frontend loads without console errors
   - Test property search form submission (even with placeholder API keys)

3. **Build Validation**:
   - Run `npm run build` in frontend directory
   - Ensure build completes successfully without ESLint errors

## Critical Timing and Timeout Information

**NEVER CANCEL THESE OPERATIONS:**
- `pip3 install -r backend/requirements.txt` - Takes 60 seconds, set timeout to 120+ seconds
- `npm install` in frontend - Takes 3-4 minutes, set timeout to 300+ seconds  
- `npm run build` - Takes 8-10 seconds, set timeout to 60+ seconds

## API Keys Required

The application requires several API keys to function fully:

1. **Mashvisor API**: Sign up at https://www.mashvisor.com/
2. **Zillow API (RapidAPI)**: Subscribe at https://rapidapi.com/
3. **SerpAPI**: Get key from https://serpapi.com/
4. **Firebase** (optional): Download `firebase_key.json` to `/backend/`

**For development/testing**: Use placeholder values like `test_key_placeholder` in `.env`

## Common Issues and Solutions

1. **Backend fails to start with "Mashvisor API key not found"**:
   - Ensure `.env` file exists in repository root (not in `/backend/`)
   - Verify `MASHVISOR_API_KEY` is set in `.env`

2. **Frontend build fails with ESLint errors**:
   - ESLint treats warnings as errors in CI mode
   - Fix unused variable warnings by removing unused imports/variables

3. **Frontend tests fail with axios import errors**:
   - Known issue with Jest/axios ESM compatibility
   - Tests are currently non-functional but don't prevent development

4. **Firebase warnings**:
   - Expected when not using real Firebase credentials
   - Application works without Firebase for basic functionality

5. **Network timeouts during pip install**:
   - Common in cloud environments with restricted network access
   - Retry with longer timeout: `pip3 install --timeout 300 -r backend/requirements.txt`
   - If persistent, use cached packages or alternative package sources

## Project Structure

### Backend (`/backend/`)
- **Entry point**: `/main.py` (run from repository root)
- **API routes**: `/backend/routes/` - property search, user management
- **Services**: `/backend/services/` - external API integrations  
- **Models**: `/backend/models/` - data models for requests/responses
- **Key files**:
  - `mashvisor_search.py` - Mashvisor API integration
  - `routes/property.py` - Main property search endpoints

### Frontend (`/frontend/`)
- **React application** built with Create React App
- **Key components**:
  - `src/App.js` - Main application
  - `src/components/SearchForm.jsx` - Property search form
  - `src/components/PropertyList.jsx` - Display search results
  - `src/services/api.js` - Backend API communication

### Root Files
- `main.py` - Backend entry point
- `.env` - Environment variables (create manually)
- `debug_api.sh` - API testing script
- `test_api.py` - Backend health check script

## Development Workflow

1. **Always activate Python virtual environment first**: `source .venv/bin/activate`
2. **Start backend before frontend** for full functionality
3. **Use placeholder API keys** for development without external service costs
4. **Run ESLint** before committing frontend changes: `npx eslint src/`
5. **Test API endpoints** with provided scripts or curl commands
6. **Validate builds** with `npm run build` before deploying

## Troubleshooting Commands

```bash
# Check if services are running
curl http://localhost:8000/  # Backend health
curl http://localhost:3000/  # Frontend (should return HTML)

# Restart services
# Kill processes and restart with python main.py and npm start

# Check Python environment
source .venv/bin/activate && python --version && pip list | grep fastapi

# Check Node environment  
cd frontend && node --version && npm list --depth=0
```