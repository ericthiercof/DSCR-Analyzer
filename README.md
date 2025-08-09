# 🏘️ DSCR Investment Property Analyzer

A professional real estate investment analysis platform for mortgage brokers and realtors.

## 🚀 Features

- **Property Search** - Find investment properties using Zillow API
- **DSCR Analysis** - Calculate Debt Service Coverage Ratio for each property
- **Mortgage Calculations** - Accurate payment estimates including taxes, insurance, PMI
- **Rent Estimation** - Zillow Zestimate + SerpAPI fallback for market data
- **Investment Scoring** - Grade properties from A+ to D based on cash flow potential

## 🏗️ Architecture

### Backend (FastAPI)
- **Location**: `/backend/`
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000`

### Frontend (Coming Soon)
- React-based user interface
- Professional property search forms
- Interactive dashboards and charts

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- Node.js (for future frontend)
- Firebase account
- Zillow API key (RapidAPI)
- SerpAPI key

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd blank-app
```

2. **Setup Python environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install backend dependencies**
```bash
cd backend
pip3 install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create backend/.env with your API keys:
ZILLOW_API_KEY=your_zillow_api_key_here
ZILLOW_API_HOST=zillow-com1.p.rapidapi.com
SERPAPI_KEY=your_serpapi_key_here
SECRET_KEY=your_jwt_secret_key_here
```

5. **Start the API**
```bash
python3 main.py
```

## 🔑 API Keys Required

### Zillow API (RapidAPI)
1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to Zillow API
3. Add your key to `backend/.env`

### SerpAPI
1. Sign up at [SerpAPI](https://serpapi.com/)
2. Get your API key
3. Add to `backend/.env`

### Firebase (Optional)
1. Create Firebase project
2. Download `firebase_key.json`
3. Place in `/backend/` directory

## 📊 API Endpoints

### Property Search
```bash
POST /api/search
```
Search for investment properties with DSCR analysis

**Example Request:**
```json
{
  "city": "Los Angeles",
  "state": "CA",
  "down_payment": 20,
  "interest_rate": 7.0,
  "min_price": 300000,
  "max_price": 800000,
  "username": "test_user"
}
```

### Save Search
```bash
POST /api/save-search
```
Save search criteria for future use

### Saved Searches
```bash
GET /api/saved-searches/{username}
```
Retrieve user's saved searches

### Firebase Test
```bash
POST /api/test-firebase
```
Test Firebase connection

## 🧮 DSCR Calculation

The Debt Service Coverage Ratio is calculated as:
```
DSCR = Monthly Rental Income / Monthly Debt Payment
```

Where Monthly Debt Payment includes:
- Principal & Interest
- Property Taxes
- Insurance
- HOA Fees
- PMI (if down payment < 20%)

## 📈 Investment Grading

- **A+ (DSCR ≥ 1.50)**: Excellent cash flow 🔥
- **A (DSCR ≥ 1.30)**: Very good investment 📈
- **B+ (DSCR ≥ 1.20)**: Good investment ✅
- **B (DSCR ≥ 1.10)**: Fair investment ⚠️
- **C (DSCR ≥ 1.00)**: Break even 📊
- **D (DSCR < 1.00)**: Cash flow negative ❌

## 🚀 Development

### Running in Development
```bash
# Backend with auto-reload
cd backend
python3 main.py
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

### Testing the API
1. Go to `http://localhost:8000/docs`
2. Click on "POST /api/search"
3. Click "Try it out"
4. Enter search parameters
5. Click "Execute"

## 📝 Project Status

✅ **Backend API** - Complete and tested  
⏳ **React Frontend** - Coming next  
⏳ **Deployment** - Cloud deployment planned  
⏳ **Authentication** - Enhanced security features  

## 🤝 Contributing

This is a private project for mortgage broker use.

## 📄 License

Private project.
