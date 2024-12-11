import requests

def post_review_comment(private_token, project_id, filename, line_number, comment, commit_sha):

    base_url = "https://gitlab.com/api/v4"
    url = f"{base_url}/projects/{project_id}/repository/commits/{commit_sha}/comments"
    headers = {"PRIVATE-TOKEN": private_token}
    
    data = {
        "note": comment,
        "path": filename,
        "line": line_number,
        "line_type": "new" 
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() 
        print("Successfully posted commit comment")
    except requests.exceptions.RequestException as e:
        print(f"Failed to post commit comment: {e}")


