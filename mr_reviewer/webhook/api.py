from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


GITLAB_PRIVATE_TOKEN = ''
GITLAB_API_URL = 'https://gitlab.com/api/v4'
GITLAB_TRIGGER_TOKEN = ""

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'object_kind' in data and data['object_kind'] == 'note':
        note_content = data['object_attributes']['note']

        if "@codehawk" in note_content:
            note_id = data['object_attributes']['id']
            discussion_id = data['object_attributes']['discussion_id']
            commit_id = data['commit']['id']
            project_id = data['project']['id']
            print(f"Received new note mentioning @codehawk on commit {commit_id} in project {project_id}")
            print("Note ID:", note_id)
            print("Discussion ID:", discussion_id)

            branch = get_branch_from_commit(project_id, commit_id)
            if branch:
                print(f"Commit ID: {commit_id}, Branch: {branch}") 
                trigger_gitlab_pipeline(project_id, branch, commit_id, note_content, note_id, discussion_id)
                print("Pipeline triggered due to new note on commit.")
            else:
                print("Branch for commit not found.")
        else:
            print("Note does not mention @codehawk.")
    
    return jsonify({'status': 'received'}), 200


def trigger_gitlab_pipeline(project_id, branch, commit_id, note_content, note_id, discussion_id):
    url = f"{GITLAB_API_URL}/projects/{project_id}/trigger/pipeline"
    response = requests.post(url, data={
        'token': GITLAB_TRIGGER_TOKEN,
        'ref': branch,  
        'variables[COMMIT_ID]': commit_id,
        'variables[NOTE_CONTENT]': note_content,
        'variables[NOTE_ID]': note_id,
        'variables[DISCUSSION_ID]': discussion_id,
        'variables[Project_ID]': project_id,
    })

    print(response.text)
    print(f"Triggering pipeline at {url} with commit ID {commit_id} on branch {branch}")  
    if response.status_code == 201:
        print('Pipeline triggered successfully.')
    else:
        print(f'Failed to trigger pipeline: {response.status_code} {response.text}')

def get_branch_from_commit(project_id, commit_id):
    """
    Fetch the branch associated with the given commit ID in the specified project.
    """
    branches_url = f"{GITLAB_API_URL}/projects/{project_id}/repository/branches"

    headers = {
        'PRIVATE-TOKEN': GITLAB_PRIVATE_TOKEN
    }

    response = requests.get(branches_url, headers=headers)
    response.raise_for_status()
    branches = response.json()

    for branch in branches:
        branch_name = branch['name']
        commits_url = f"{GITLAB_API_URL}/projects/{project_id}/repository/branches/{branch_name}/commit"
        page = 1
        while True:
            commits_url_page = f"{GITLAB_API_URL}/projects/{project_id}/repository/commits?ref_name={branch_name}&page={page}&per_page=100"
            response = requests.get(commits_url_page, headers=headers)
            response.raise_for_status()
            commits = response.json()
            
            if not commits:
                break

            for commit in commits:
                if commit['id'] == commit_id:
                    return branch_name
            
            page += 1
    
    return None

if __name__ == '__main__':
    app.run(port=8080, debug=True)