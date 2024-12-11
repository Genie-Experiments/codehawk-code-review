import re
import requests

ignore_files_list = [
        ".gitlab-ci.yml",
        "generate_response.py",
        "files_retriever.py",
        "comment_posting.py",
        "llm_review.py",
        "reply_thread.py"
]

import urllib.parse

def get_changed_files_content(private_token, owner, repo_name, commit_sha):
    base_url = f"https://gitlab.com/api/v4"
    project_id = f"{owner}%2F{repo_name}" 
    headers = {"PRIVATE-TOKEN": private_token}

    commit_diff_url = f"{base_url}/projects/{project_id}/repository/commits/{commit_sha}/diff"

    try:
        diff_response = requests.get(commit_diff_url, headers=headers)
        diff_response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching commit diff: {e}")
        return {}, {}

    if diff_response.status_code != 200:
        print(f"Failed to fetch commit diff: {diff_response.status_code}")
        return {}, {}

    diff_data = diff_response.json()

    changed_files_content = {}
    full_file_content = {}

    for change in diff_data:
        file_name = change['new_path']
    
        if file_name in ignore_files_list:
            continue

        filename_encoded = urllib.parse.quote(file_name, safe='')
        file_url = f"{base_url}/projects/{project_id}/repository/files/{filename_encoded}/raw"
        file_params = {"ref": commit_sha}
        file_response = requests.get(file_url, headers=headers, params=file_params)

        if file_response.status_code == 200:
            file_content = file_response.text
            full_file_content[file_name] = file_content


            if 'diff' in change:
                diff_lines = change['diff'].split('\n')
                lines_changed = {}
                current_line_number = None
                for line in diff_lines:
                    match = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)', line)
                    if match:
                        current_line_number = int(match.group(1))
                    elif current_line_number is not None:
                        if line.startswith('+') and not re.match(r'^\+[\s\(\){}\[\]]*$', line[1:]): 
                            lines_changed[current_line_number] = line[1:]
                            current_line_number += 1
                        elif line.startswith('\\ No newline at end of file'):
                            continue
                        elif not line.startswith('-'):
                            current_line_number += 1

                changed_files_content[file_name] = lines_changed

            else:
                lines_added = {}
                file_lines = file_content.split('\n')
                for i, line in enumerate(file_lines, start=1):
                    if line.strip() and not re.match(r'^[\s\(\){}\[\]]*$', line): 
                        lines_added[i] = line
                changed_files_content[file_name] = lines_added

        else:
            print(f"Skipping file {file_name} due to error: {file_response.status_code}")

    return changed_files_content, full_file_content