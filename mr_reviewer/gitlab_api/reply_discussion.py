import requests

GITLAB_API_URL = 'https://gitlab.com/api/v4'
GITLAB_PRIVATE_TOKEN = "glpat-ZekGy3vsLDzfsWTdFzKE"

def reply_to_discussion(commit_id, project_id, discussion_id, reply_text, note_id):
    # For general comments in the thread
    url = f"{GITLAB_API_URL}/projects/{project_id}/repository/commits/{commit_id}/discussions/{discussion_id}/notes"

    #For focused replies        
    #url = f"{GITLAB_API_URL}/projects/{project_id}/repository/commits/{commit_id}/discussions/"
    headers = {
        'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN
    }
    data = {
        'body': reply_text
    }
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Successfully replied to the discussion.")
    else:
        print(f"Failed to reply: {response.status_code} {response.text}")