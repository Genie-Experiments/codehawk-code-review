import os
from llama_index.core.agent import ReActAgent
from llama_index.llms.groq import Groq
from llama_index.llms.openai import OpenAI
from llm_processing.llm_review import llm_review_processing, llm_review_tool
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(api_key=openai_api_key, model="gpt-4", temperature=0.1)

tools = [llm_review_tool]

agent = ReActAgent.from_tools(tools=tools, llm=llm, verbose=True, context="""Purpose: The role of this agent is to check if the review for
                            a code snippet is accurate and provide improved review if necessary. The agent will use the code snippet and the full file content for context. 
                            The agent will provide improved code reviews if necessary of the code snippet. Use the full file content only for context for code snippet.
                            If you think, the review needs improvement then provide the improved review. If you think the review is accurate, then simply return "Review is good".
                            """)

def generate_and_evaluate_review(line_content, full_file_content):

    initial_review = llm_review_processing(line_content, full_file_content)
    
    current_review = initial_review
    iteration = 0

    # while iteration < 5:
    agent_input = f"Evaluate the following code review: {current_review}. Use the code snippet: {line_content} and the full file content: {full_file_content} for context. Provide an improved review if necessary.Refine the review if necessary in a professional manner. If the review is accurate, return the original review as it is. This review will be used in a production code so keep it professional. and don't start with 'Here is the review' or 'Review comment'. Just give the refined review directly."
        
    refined_review = agent.query(agent_input)

    print(f"Line of code: {line_content}")
    print(f"Initial Review: {current_review}")
    print(f"Refined Review: {refined_review.response}")
    if current_review == refined_review:
        return current_review
    else:
        current_review = refined_review
        return current_review
        # iteration += 1

