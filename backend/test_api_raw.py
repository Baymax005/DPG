"""
Raw API test to see the actual response
"""
import requests
import json

WALLET = "0x03AC9b88fac2E6e065e3aF4b23fb06F972F66765"
API_KEY = "XEUGFHET25SI6JJ3GQ1C3VYZ41VH1AE7EY"

# Test V2 API endpoint
url = "https://api.etherscan.io/v2/api"
params = {
    "chainid": "11155111",  # Sepolia chain ID
    "module": "account",
    "action": "txlist",
    "address": WALLET,
    "startblock": 0,
    "endblock": 99999999,
    "page": 1,
    "offset": 100,
    "sort": "desc",
    "apikey": API_KEY
}

print(f"🔍 Testing URL: {url}")
print(f"📋 Parameters: {json.dumps(params, indent=2)}")
print("\n" + "="*70 + "\n")

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"📡 Status Code: {response.status_code}")
    print(f"📄 Response Headers: {dict(response.headers)}")
    print("\n" + "="*70 + "\n")
    
    data = response.json()
    print(f"📦 Full Response JSON:")
    print(json.dumps(data, indent=2))
    
    if data.get("status") == "1":
        print(f"\n✅ SUCCESS! Found {len(data.get('result', []))} transactions")
    else:
        print(f"\n❌ API Error!")
        print(f"   Status: {data.get('status')}")
        print(f"   Message: {data.get('message')}")
        print(f"   Result: {data.get('result')}")
        
except Exception as e:
    print(f"💥 Exception: {type(e).__name__}: {e}")
