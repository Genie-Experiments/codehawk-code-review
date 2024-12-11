from langchain_groq import ChatGroq
from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import ChatPromptTemplate

llama3_70b = ChatGroq(temperature=0, groq_api_key="GROQ-KEY", model_name="llama3-70b-8192")

def get_llm_reply(full_file_content, line_of_code, note, tag_comment):
    template = """ You are being asked a question for which you left a code review on.

    This is the question that the developer left. Read their question and answer accordingly: {tag_comment}. 

    You need to provide a response to the question accordingly. The code snippet that you reviewed is this: {line_of_code}.

    This is the review that you left for the code snippet: {note}.


    Be professional in your response and provide a clear and concise answer to the question or clarification. Be sure to address the question or clarification directly and provide a clear explanation.

    The response should be straightforward, to the point. 

    This is the full file context for the code snippet. The file context is: {full_file_content}.

    Before responding, read the context and then using that give context-based feedback for {line_of_code}.

    The response should be professional because it is a production codebase and we want to maintain a professional environment.

    The response should not include phrases like "Here's the answer" or "The answer is". Instead, provide a direct answer to the question or clarification.

    The reply sent should be no more than 50 words. and to the point and relevant to the question.
    """
    
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_template(template)
    # llm = create_llm()

    chain = prompt | llama3_70b | output_parser
    output_llama3_70b = chain.invoke({"line_of_code": line_of_code, "full_file_content": full_file_content, "note": note, "tag_comment": tag_comment})
    print(output_llama3_70b)
    return output_llama3_70b