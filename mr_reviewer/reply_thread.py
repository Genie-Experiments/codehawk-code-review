import argparse
import requests
import urllib.parse

from gitlab_api.file_retriever_for_reply import get_discussions, get_file_content, get_legacy_diff_note_details, get_line_from_file
from gitlab_api.reply_discussion import reply_to_discussion
from llm_processing.llm_reply import get_llm_reply

GITLAB_API_URL = 'https://gitlab.com/api/v4'
GITLAB_PRIVATE_TOKEN = ""

def main():
    parser = argparse.ArgumentParser(description='Interactive clarification job script.')
    
    parser.add_argument('--commit-id', type=str, required=True, help='Commit')
    parser.add_argument('--note-content', type=str, required=True, help='NoteContent')
    parser.add_argument('--note-id', type=str, required=True, help='NoteId')
    parser.add_argument('--discussion-id', type=str, required=True, help='DiscussionId')
    parser.add_argument('--mr-number', type=str, required=True, help='Merge request number')
    parser.add_argument('--project-id', type=str, required=True, help='Project ID')


    args = parser.parse_args()
    
    print(f"Commit ID: {args.commit_id}")
    print(f"Note Content: {args.note_content}")
    print(f"Note ID: {args.note_id}")
    print(f"Discussion ID: {args.discussion_id}")
    print(f"Merge Request Number: {args.mr_number}")
    print(f"Project ID: {args.project_id}")

    project_id = args.project_id
    commit_id = args.commit_id
    discussion_id = args.discussion_id
    note_id = args.note_id
    user_tag_comment = args.note_content
    
    note_details = get_legacy_diff_note_details(private_token="glpat-ZekGy3vsLDzfsWTdFzKE", project_id=project_id, commit_id=commit_id)
    
    # print(note_details)

    user = note_details[0]['author']['username']
    previous_review = note_details[0]['note']
    file_path = note_details[0]['path']
    line_number = note_details[0]['line']
    
    print(f"User: {user}")
    print(f"Previous Review: {previous_review}")
    print(f"File Path: {file_path}")


    filename_encoded = urllib.parse.quote(file_path, safe='')
    filename_encoded = filename_encoded.replace('.', '%2E')
    full_file_content = get_file_content(project_id, filename_encoded, commit_id, private_token="glpat-ZekGy3vsLDzfsWTdFzKE")
    
    if full_file_content:
        line_of_code = get_line_from_file(full_file_content, line_number)
        print(f"Line {line_number}: {line_of_code}")
    

    # tag_comment = "@codehawk what do you mean? I used the print function"
    
    llm_response = get_llm_reply(full_file_content, line_of_code, previous_review, user_tag_comment)
    specific_user_reply = f"@{user} {llm_response}"
    
    reply_to_discussion(commit_id, project_id, discussion_id, specific_user_reply, note_id)

if __name__ == "__main__":
    main()
    

