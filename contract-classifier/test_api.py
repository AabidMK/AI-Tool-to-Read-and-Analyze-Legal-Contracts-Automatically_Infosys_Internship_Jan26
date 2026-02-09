import requests
import time

BASE_URL = "http://localhost:8000"

# Upload a contract
with open("sample_contracts/NondisclosureAgreement.pdf", "rb") as f:
    response = requests.post(f"{BASE_URL}/analyze", files={"file": f})
    print("Upload Response:", response.json())
    task_id = response.json()["task_id"]

# Poll for results
while True:
    response = requests.get(f"{BASE_URL}/result/{task_id}")
    result = response.json()
    print(f"Status: {result['status']}")
    
    if result["status"] == "completed":
        print("\nContract Analysis Report:")
        print(f"Type: {result['report']['contract_summary']['type']}")
        print(f"Industry: {result['report']['contract_summary']['industry']}")
        print(f"Risk: {result['report']['contract_summary']['overall_risk_rating']}")
        break
    elif result["status"] == "failed":
        print(f"Error: {result.get('error')}")
        break
    
    time.sleep(2)
