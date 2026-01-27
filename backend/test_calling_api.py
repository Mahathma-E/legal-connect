"""
Test Script for Paid Calling Feature API Endpoints
Tests all calling feature endpoints with various scenarios
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_calling_feature():
    print("\n" + "="*60)
    print("TESTING PAID CALLING FEATURE API ENDPOINTS")
    print("="*60)
    
    # Test user IDs (replace with actual user IDs from your database)
    caller_id = "user123"  # Public user
    receiver_id = "user456"  # Advocate user
    admin_id = "admin001"
    
    # 1. Test Get Call Settings (Admin)
    print("\n\n1. Testing: GET /api/admin/call-settings")
    response = requests.get(f"{BASE_URL}/api/admin/call-settings")
    print_response("Get Call Settings", response)
    
    # 2. Test Update Call Settings (Admin)
    print("\n\n2. Testing: PUT /api/admin/call-settings")
    update_data = {
        "admin_id": admin_id,
        "call_price": 25,
        "call_duration": 15,
        "feature_enabled": True
    }
    response = requests.put(
        f"{BASE_URL}/api/admin/call-settings",
        json=update_data
    )
    print_response("Update Call Settings", response)
    
    # 3. Test Check Eligibility - Without Mutual Follow
    print("\n\n3. Testing: POST /api/call/check-eligibility (No mutual follow)")
    eligibility_data = {
        "caller_id": caller_id,
        "receiver_id": receiver_id
    }
    response = requests.post(
        f"{BASE_URL}/api/call/check-eligibility",
        json=eligibility_data
    )
    print_response("Check Eligibility - No Mutual Follow", response)
    
    # 4. Test Check Eligibility - With Mutual Follow (after following each other)
    print("\n\n4. Testing: POST /api/call/check-eligibility (With mutual follow)")
    print("   NOTE: Make sure both users follow each other first!")
    response = requests.post(
        f"{BASE_URL}/api/call/check-eligibility",
        json=eligibility_data
    )
    print_response("Check Eligibility - With Mutual Follow", response)
    
    # 5. Test Initiate Call
    print("\n\n5. Testing: POST /api/call/initiate")
    initiate_data = {
        "caller_id": caller_id,
        "receiver_id": receiver_id
    }
    response = requests.post(
        f"{BASE_URL}/api/call/initiate",
        json=initiate_data
    )
    print_response("Initiate Call", response)
    
    # Get call session ID from response
    call_session_id = None
    if response.status_code == 200:
        call_session_id = response.json().get('call_session_id')
        print(f"\n✅ Call Session ID: {call_session_id}")
    
    # 6. Test Get Call History
    print("\n\n6. Testing: GET /api/call/history/<user_id>")
    response = requests.get(f"{BASE_URL}/api/call/history/{caller_id}?limit=10")
    print_response(f"Get Call History for {caller_id}", response)
    
    # 7. Test End Call
    if call_session_id:
        print("\n\n7. Testing: POST /api/call/end")
        end_data = {
            "call_session_id": call_session_id
        }
        response = requests.post(
            f"{BASE_URL}/api/call/end",
            json=end_data
        )
        print_response("End Call", response)
    else:
        print("\n\n7. Skipping End Call test (no active call session)")
    
    # 8. Test Admin Call History
    print("\n\n8. Testing: GET /api/admin/call-history")
    response = requests.get(f"{BASE_URL}/api/admin/call-history?limit=20")
    print_response("Admin Call History", response)
    
    # 9. Test Insufficient Balance Scenario
    print("\n\n9. Testing: Insufficient Balance Scenario")
    print("   (This will fail if user has sufficient balance)")
    response = requests.post(
        f"{BASE_URL}/api/call/initiate",
        json=initiate_data
    )
    print_response("Initiate Call - Insufficient Balance", response)
    
    # Summary
    print("\n\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("\n✅ All API endpoints tested!")
    print("\nEndpoints tested:")
    print("  1. GET  /api/admin/call-settings")
    print("  2. PUT  /api/admin/call-settings")
    print("  3. POST /api/call/check-eligibility")
    print("  4. POST /api/call/initiate")
    print("  5. POST /api/call/end")
    print("  6. GET  /api/call/history/<user_id>")
    print("  7. GET  /api/admin/call-history")
    print("\nNOTE: Some tests may fail if:")
    print("  - Users don't have mutual follow")
    print("  - User IDs don't exist in database")
    print("  - Insufficient wallet balance")
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        test_calling_feature()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to backend server")
        print("   Make sure the Flask server is running on http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
