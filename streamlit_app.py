

import streamlit as st
from login import login_screen

# Run the login logic first
login_screen()

# Then check if the user is logged in
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.stop()

# --- Sidebar Navigation ---
page = st.sidebar.radio("Go to", ["Search", "Saved Searches"])

import streamlit as st
import requests
from math import isclose
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()



# --- Config from Secrets ---
ZILLOW_API_KEY = st.secrets["zillow"]["api_key"]
ZILLOW_API_HOST = st.secrets["zillow"]["api_host"]
SERPAPI_KEY = st.secrets["serpapi"]["api_key"]



# --- Mortgage Calculation ---
def estimate_mortgage_payment(price, down_payment_pct=0.20, interest_rate=7.0, term_years=30, tax_rate=0.0125, hoa_fee=0):
    loan_amount = price * (1 - down_payment_pct)
    monthly_rate = interest_rate / 100 / 12
    n_payments = term_years * 12

    if isclose(monthly_rate, 0.0):
        base_payment = loan_amount / n_payments
    else:
        base_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n_payments) / ((1 + monthly_rate)**n_payments - 1)

    property_tax = price * tax_rate / 12
    insurance = price * 0.0035 / 12  # Estimated insurance cost
    pmi = 0
    if down_payment_pct < 0.20:
        pmi = price * 0.005 / 12

    total_payment = base_payment + property_tax + hoa_fee + insurance + pmi
    return round(total_payment, 2)

# --- Google Search Fallback Rent via SerpAPI ---
def fetch_average_rent_serpapi(zipcode, bedrooms):
    if not SERPAPI_KEY:
        return None
    query = f"average rent for {bedrooms} bedroom home in {zipcode}"
    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "hl": "en",
        "gl": "us"
    }
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        for res in data.get("answer_box", {}).get("snippet_highlighted_words", []):
            digits = ''.join(c for c in res if c.isdigit())
            if digits:
                return int(digits)
    except Exception as e:
        st.error(f"Error fetching rent from SerpAPI: {e}")
    return None

# --- Fetch Listings ---
def fetch_properties(city, state, max_results=50):
    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
    headers = {
        "X-RapidAPI-Key": ZILLOW_API_KEY,
        "X-RapidAPI-Host": ZILLOW_API_HOST
    }
    params = {
        "location": f"{city}, {state}",
        "status_type": "ForSale",
        "home_type": "Houses",
        "limit": str(max_results)
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        st.error(f"Zillow API error: {resp.status_code} - {resp.text}")
        return []
    data = resp.json()
    return data.get("props", [])


# --- Main Page Logic ---

if page == "Search":
    st.title("🏘️ DSCR Investment Property Analyzer")

    # Use session state for defaults
    city = st.text_input("City", st.session_state.get("city", "Los Angeles"))
    state = st.text_input("State (2-letter)", st.session_state.get("state", "CA"))
    down_payment = st.slider("Down Payment (%)", 0, 100, st.session_state.get("down_payment", 20))
    interest_rate = st.number_input("Interest Rate (%)", value=st.session_state.get("interest_rate", 7.0))
    min_price = st.number_input("Minimum Price ($)", value=st.session_state.get("min_price", 0))
    max_price = st.number_input("Maximum Price ($)", value=st.session_state.get("max_price", 2_000_000))

    # Auto-search if coming from saved search
    if (
        st.session_state.get("city") is not None and
        st.session_state.get("state") is not None and
        st.session_state.get("down_payment") is not None and
        st.session_state.get("interest_rate") is not None and
        st.session_state.get("min_price") is not None and
        st.session_state.get("max_price") is not None and
        st.session_state.get("trigger_search", False)
    ):
        st.session_state.properties = fetch_properties(city, state)
        st.session_state.fallback_rent = {}
        st.session_state["trigger_search"] = False

    if st.button("Search Properties"):
        st.session_state.properties = fetch_properties(city, state)
        st.session_state.fallback_rent = {}

    # Save Search Button
    if st.button("Save This Search"):
        user = st.session_state.get("username", "unknown")
        search_data = {
            "city": city,
            "state": state,
            "down_payment": down_payment,
            "interest_rate": interest_rate,
            "min_price": min_price,
            "max_price": max_price,
        }
        db.collection("users").document(user).collection("saved_searches").add(search_data)
        st.success("Search saved!")

    if st.button("🚀 Test Firebase"):
        db.collection("test").add({"message": "Hello from Streamlit!"})
        st.success("Successfully wrote to Firebase!")

    results = []

    if "properties" in st.session_state:
        for prop in st.session_state.properties:
            price = prop.get("price")
            address = prop.get("address")
            rent_zestimate = prop.get("rentZestimate")
            bedrooms = prop.get("bedrooms")
            zpid = prop.get("zpid")
            zipcode = address.split()[-1] if address else None
            hoa_fee = prop.get("hoaFee") or prop.get("priceComponent", {}).get("hoa") or 0
            tax_rate = prop.get("propertyTaxRate") or 0.0125

            if not (price and address and bedrooms and zipcode and zpid):
                continue
            if int(price) < int(min_price) or int(price) > int(max_price):
                continue

            monthly_payment = estimate_mortgage_payment(price, down_payment / 100, interest_rate, tax_rate=tax_rate, hoa_fee=hoa_fee)

            rent = rent_zestimate or st.session_state.fallback_rent.get(f"{zipcode}-{bedrooms}")
            rent_type = "Zestimate" if rent_zestimate else "Unknown"

            if rent:
                dscr = round(rent / monthly_payment, 2)
                results.append({
                    "address": address,
                    "price": price,
                    "monthly_payment": monthly_payment,
                    "rent": rent,
                    "rent_type": rent_type,
                    "dscr": dscr,
                    "hoa_fee": hoa_fee,
                    "tax_rate": tax_rate,
                    "zpid": zpid
                })

        # Sort by DSCR descending
        sorted_results = sorted(results, key=lambda x: x["dscr"], reverse=True)

        for r in sorted_results:
            st.markdown(f"🏠 [{r['address']}](https://www.zillow.com/homedetails/{r['zpid']}_zpid/")
            st.write(f"💵 Price: ${r['price']:,.0f}")
            st.write(f"📈 DSCR: {r['dscr']} {'🔥' if r['dscr'] > 1.25 else ''}")
            with st.expander("More details"):
                st.write(f"🏦 Monthly Payment: ${r['monthly_payment']:,.2f}")
                st.write(f"📊 Rent Estimate ({r['rent_type']}): ${r['rent']:,.0f}")
                st.write(f"🏘️ HOA Fee: ${r['hoa_fee']:,.2f}")
                st.write(f"📉 Tax Rate: {r['tax_rate']*100:.2f}%")
                st.write(f"🛡️ Estimated Insurance: ${r['price'] * 0.0035 / 12:,.2f}")
    else:
        st.info("🔎 Enter your search parameters and click 'Search Properties' to begin.")

# --- Saved Searches Page ---
elif page == "Saved Searches":
    st.title("💾 Saved Searches")
    user = st.session_state.get("username", "unknown")
    saved_searches_ref = db.collection("users").document(user).collection("saved_searches")
    saved_searches = list(saved_searches_ref.stream())
    if not saved_searches:
        st.info("No saved searches yet.")
    else:
        for s in saved_searches:
            data = s.to_dict()
            st.write(f"**City:** {data.get('city')} | **State:** {data.get('state')} | **Down Payment:** {data.get('down_payment')}% | **Interest:** {data.get('interest_rate')}% | **Price:** ${data.get('min_price')} - ${data.get('max_price')}")
            if st.button(f"Run Search", key=s.id):
                # Set session state and rerun search
                st.session_state["city"] = data.get("city", "")
                st.session_state["state"] = data.get("state", "")
                st.session_state["down_payment"] = data.get("down_payment", 20)
                st.session_state["interest_rate"] = data.get("interest_rate", 7.0)
                st.session_state["min_price"] = data.get("min_price", 0)
                st.session_state["max_price"] = data.get("max_price", 2000000)
                st.session_state["trigger_search"] = True
                st.rerun()
