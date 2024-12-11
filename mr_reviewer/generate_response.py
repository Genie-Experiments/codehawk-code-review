import argparse
import os
import re
import requests

from gitlab_api.comment_posting import post_review_comment
from gitlab_api.files_retriever import get_changed_files_content
from llm_processing.llm_review import llm_review_processing
from llm_processing.agent import generate_and_evaluate_review

  
def main():

    parser = argparse.ArgumentParser(description="Process MR details and environment variables.")
    parser.add_argument('--owner', type=str, required=True, help='Repository owner')
    parser.add_argument('--repo-name', type=str, required=True, help='Repository name')
    parser.add_argument('--commit-sha', type=str, required=True, help='Commit SHA')
    parser.add_argument('--mr-number', type=str, required=True, help='Merge request number')
    parser.add_argument('--event-name', type=str, required=True, help='Event name')
    parser.add_argument('--action', type=str, required=True, help='Action name')
    parser.add_argument('--private-token', type=str, required=True, help='GitLab private token')

    args = parser.parse_args()

    print(f"Owner: {args.owner}")
    print(f"Repository Name: {args.repo_name}")
    print(f"Commit SHA: {args.commit_sha}")
    print(f"Merge Request Number: {args.mr_number}")
    print(f"Event Name: {args.event_name}")
    print(f"Action : {args.action}")

    owner = args.owner
    repo_name = args.repo_name
    commit_sha = args.commit_sha
    project_id = f"{owner}%2F{repo_name}"
    merge_request_iid = args.mr_number
    private_token = args.private_token
    comment_history = []
    try:
        changed_files_content, full_file_content = get_changed_files_content(private_token, owner, repo_name, commit_sha)
        print("\nChanged Files and Their Changed Lines:")

        
        for filename, lines_changed in changed_files_content.items():
            for line_number, line_content in lines_changed.items():
                if line_content.strip():  
                    # print(f"Line {line_number}: {line_content}")            
                    
                    review = llm_review_processing(line_content, full_file_content[filename])

                    # print("lINE CONTENT", line_content)
                    # llama_index_review = generate_and_evaluate_review(line_content, full_file_content[filename])
                    # review = llama_index_review.response
                    
                    if "No review comment needed" in review:
                        print(f"No review comment needed for line {line_number} in file {filename}")
                    else:
                        # print(f"Posting review comment for line {line_number} in file {filename}")
                        comment_history.append(review)
                        post_review_comment(private_token, project_id, filename, line_number, review, commit_sha)

    except Exception as e:
        print(f"Failed to process reviews: {e}")
    

    print("\nComment History:", comment_history)

if __name__ == "__main__":
    main()

