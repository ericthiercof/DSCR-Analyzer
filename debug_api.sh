#!/bin/bash
echo "Testing API with curl to see validation errors"
curl -X POST http://127.0.0.1:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"city":"jackson", "state":"MI", "downPaymentPercent":20, "interestRate":7, "minPrice":150000, "maxPrice":1500000}' \
  -v
