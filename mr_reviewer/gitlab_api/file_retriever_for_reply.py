import requests

GITLAB_API_URL = 'https://gitlab.com/api/v4'
GITLAB_PRIVATE_TOKEN = "glpat-ZekGy3vsLDzfsWTdFzKE"

def get_legacy_diff_note_details(private_token, project_id, commit_id):
    base_url = "https://gitlab.com/api/v4"
    url = f"{base_url}/projects/{project_id}/repository/commits/{commit_id}/comments"
    # url = f"{base_url}/projects/{project_id}/repository/commits/{commit_id}/discussions/64ad230938d59f1e9944c88cb9863ddf347dcd91"
    headers = {"PRIVATE-TOKEN": private_token}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # print(f"Response: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get legacy diff note details: {e}")
        return None

def get_file_content(project_id, file_path, commit_sha, private_token):
    headers = {"PRIVATE-TOKEN": private_token}
    base_url = "https://gitlab.com/api/v4"
    url = f"{base_url}/projects/{project_id}/repository/files/{file_path}/raw"
    params = {"ref": commit_sha}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to get file content: {e}")
        return None

def get_line_from_file(file_content, line_number):
    lines = file_content.splitlines()
    if line_number <= len(lines):
        return lines[line_number - 1] 
    else:
        print("Line number out of range.")
        return None

def get_discussions(project_id, commit_id):
    url = f"{GITLAB_API_URL}/projects/{project_id}/repository/commits/{commit_id}/discussions/5e574f3e1670285860be8bf2688713cba0f4ec2c/notes/2015867478"
    headers = {
        'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        discussions = response.json()
        # print(f"Discussions: {discussions}")
        latest_note = None

        for discussion in discussions:

            for note in discussion['notes']:
                if '@codehawk' in note['body']:
                    if latest_note is None or note['created_at'] > latest_note['created_at']:
                        latest_note = note

        if latest_note:
            print(f"Latest Note ID: {latest_note['id']}, Note Body: {latest_note['body']}")
            return latest_note['body']
        else:
            print("No notes mentioning @codehawk found in the discussions.")
    else:
        print(f"Failed to fetch discussions: {response.status_code} {response.text}")