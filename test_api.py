import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"
API_KEY = "sk-artfish-test-key"

def test_health():
    print("Checking health...")
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"Health: {resp.json()}")

def test_execution():
    print("\nSubmitting intent...")
    payload = {
        "goals": ["cyberpunk_city", "night_rain"],
        "constraints": {"style": "photorealistic"},
        "user_id": "test_user",
        "priority": 1
    }
    headers = {"X-API-Key": API_KEY}
    
    resp = requests.post(f"{BASE_URL}/v1/execute", json=payload, headers=headers, timeout=10)
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
        return
        
    data = resp.json()
    run_id = data["run_id"]
    print(f"Task submitted. Run ID: {run_id}")
    
    # 轮询状态
    for _ in range(10):
        time.sleep(1)
        status_resp = requests.get(f"{BASE_URL}/v1/execution/{run_id}", headers=headers, timeout=10)
        status_data = status_resp.json()
        print(f"Current Status: {status_data['status']} | Cost: {status_data['total_cost']}")
        
        if status_data["status"] in ["SUCCESS", "FAIL"]:
            break
            
    if status_data["status"] == "SUCCESS":
        print("\nDownloading report...")
        report_resp = requests.get(f"{BASE_URL}/v1/execution/{run_id}/report", headers=headers, timeout=10)
        with open(f"test_report_{run_id}.pdf", "wb") as f:
            f.write(report_resp.content)
        print(f"Report saved as test_report_{run_id}.pdf")

if __name__ == "__main__":
    # 注意：运行此测试前需要先启动 api/main.py
    try:
        test_health()
        test_execution()
    except Exception as e:
        print(f"Test failed: {e}")
        print("Make sure the API server is running (python -m api.main)")
