import requests
import json

# Zoom API credentials
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'
MEETING_ID = 'your_meeting_id'
USER_ID = 'your_user_id'

def get_zoom_token(api_key, api_secret):
    url = "https://zoom.us/oauth/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': api_key,
        'client_secret': api_secret
    }
    response = requests.post(url, data=payload)
    return response.json()['access_token']

def send_ready_check(token, meeting_id):
    url = f"https://api.zoom.us/v2/meetings/{meeting_id}/chat"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    message = {
        'message': "Ready Check: Are you ready?",
        'to_contact': 'everyone'
    }
    response = requests.post(url, headers=headers, data=json.dumps(message))
    return response.status_code

def main():
    token = get_zoom_token(API_KEY, API_SECRET)
    status = send_ready_check(token, MEETING_ID)
    if status == 201:
        print("Ready check sent successfully.")
    else:
        print("Failed to send ready check.")

if __name__ == "__main__":
    main()
