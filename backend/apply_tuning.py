import requests
import json

API_URL = "http://localhost:8000/update-config"

def apply_tuning():
    print("--- Apply Tuning Configuration ---")
    print("Enter new values (leave blank to keep current):")
    
    config = {}
    
    val = input("USER_WINNING_MARGIN (Current: 200): ")
    if val: config["USER_WINNING_MARGIN"] = int(val)
    
    val = input("USER_LOSING_MARGIN (Current: -200): ")
    if val: config["USER_LOSING_MARGIN"] = int(val)
    
    val = input("FAST_PLAY_LIMIT (Current: 3.0): ")
    if val: config["FAST_PLAY_LIMIT"] = float(val)
    
    val = input("MISTAKE_SEVERE_MIN (Current: 300): ")
    if val: config["MISTAKE_SEVERE_MIN"] = int(val)
    
    if not config:
        print("No changes made.")
        return

    try:
        response = requests.post(API_URL, json=config)
        if response.status_code == 200:
            print("\nSuccess! Configuration updated.")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\nFailed to connect to backend: {e}")

if __name__ == "__main__":
    apply_tuning()
