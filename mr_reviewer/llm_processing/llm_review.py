import os
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from llama_index.core.tools import FunctionTool
from fuzzywuzzy import fuzz
from dotenv import load_dotenv
import time

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

llama3_70b = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="llama3-70b-8192")

review_history = []

def normalize_review(review):
    return review.strip().lower()

def is_similar_review(new_review, history, threshold=50):
    print("Checking for similar review")
    normalized_new_review = normalize_review(new_review)
    for review in history:
        if fuzz.ratio(normalize_review(review), normalized_new_review) > threshold:
            print("Similar review found")
            return True
    print("No similar review found")
    return False

def llm_review_processing(code_snippet, full_file_content):
    
    print("In processing")


    template = """ You are a senior software engineer tasked with reviewing a production codebase. You are reviewing a code snippet that has been changed in a merge request. 
    You need to provide feedback on the code snippet if it requires any. The code snippet will be this: {code_snippet}.

    Do not nitpick. Focus on the most important issues that will improve the code quality like performance, security, efficency, code conventions and maintainability.
    
    Review the code snippet only if it requires changes because it is a production codebase and we don't want to bombard the developers with unnecessary feedback. 
    If you feel it is good as it is, you can return "No review comment needed".

    If you encounter comments or docstrings in the code snippet, ignore them and focus on the actual code.

    For better review, use the file context for the code snippet. The file context is: {file_content}. 

    Before reviewing any code snippet, read the context and then using that give context-based feedback for {code_snippet}.

    The review should be straightforward, to the point and no more than 50 words. 

    The review should be professional because it is a production codebase and we want to maintain a professional environment.

    If you encounter just a function name or a variable name as {code_snippet}, you can return "No review comment needed".
    
    Please refrain from using incomplete or lacks context comments. Use the file context to provide a better review.

    Please keep in mind that it is a production codebase, so the review should be only if necessary. If the code snippet is good as it is, return "No review comment needed".

    You can use the following as examples. This should be the tone of the review. To the point and professional. The format should be followed strictly. Don't include phrases like "Heres the review" or "Review comment". Directly give the review. Examples are:
    "Why are you using a for loop here? Can you use a list comprehension instead?" or "You can use the 'requests' library to make the API call instead of using 'urllib'."
    


    """
    
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llama3_70b | output_parser
    output_llama3_70b = chain.invoke({"code_snippet": code_snippet, "file_content": full_file_content})
    print("Going to sleep")
    time.sleep(20)
    if is_similar_review(output_llama3_70b, review_history):
        return "No review comment needed"
    
    review_history.append(output_llama3_70b)
    
    print("Review history", review_history)

    return output_llama3_70b


llm_review_tool = FunctionTool.from_defaults(
    fn=llm_review_processing,
    name = "llm_review_processing",
    description = "Review a code snippet and provide feedback on the code snippet if it requires any.",
)