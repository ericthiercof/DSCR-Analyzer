from math import isclose

def estimate_mortgage_payment(price, down_payment_pct=0.20, interest_rate=7.0, term_years=30, tax_rate=0.0125, hoa_fee=0):
    """Estimate monthly mortgage payment including taxes, insurance, HOA."""
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