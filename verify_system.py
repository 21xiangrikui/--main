import requests

BASE_URL = 'http://127.0.0.1:5000'

def test_system():
    print("Testing Homepage...")
    try:
        r = requests.get(BASE_URL)
        if r.status_code == 200:
            print("SUCCESS: Homepage loaded successfully.")
            print(f"Page content preview: {r.text[:200]}...")
        else:
            print(f"FAILED: Homepage status {r.status_code}")
            return
            
        print("Testing Login...")
        payload = {'username': 'admin', 'password': 'admin123'}
        r = requests.post(f"{BASE_URL}/login", data=payload, allow_redirects=True)
        if r.status_code == 200:
            print("SUCCESS: Login successful.")
            print("Testing Dashboard access...")
            r = requests.get(f"{BASE_URL}/dashboard", cookies=r.cookies)
            if r.status_code == 200:
                print("SUCCESS: Dashboard accessible.")
                print(f"Dashboard preview: {r.text[:200]}...")
            else:
                print(f"FAILED: Dashboard access failed. Status {r.status_code}")
        else:
            print(f"FAILED: Login failed. Status {r.status_code}")
            
        print("\nAll tests completed.")
    except Exception as e:
        print(f"ERROR: Could not connect to server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_system()
