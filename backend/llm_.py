from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from transformers import AutoTokenizer
import fitz
from io import BytesIO
import os
import faiss
from functools import  lru_cache
import json
import re
import logging
from try_task.questions import FAQS

load_dotenv()

api_key=os.getenv("GROQ_API_KEY")


text=""
for t_ in FAQS:
    text += f"{t_['question']},{t_['answer']} \n\n"
    print()

@lru_cache(maxsize=100)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")


@lru_cache(maxsize=100)
def rag_llm(input_questions):

    embeddings = get_embeddings()
    # embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    llm= ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama3-8b-8192")
    new_vector_store = FAISS.load_local(
    "faiss_index2", embeddings, allow_dangerous_deserialization=True
    )

    ret_=new_vector_store.as_retriever(search_kwargs={'k': 2})
    # new_vector_store.as_retriever(search_kwargs={'k': 2})
    # print("ret___:",ret_)
    template="""You are an educational assistant for Vedantu, an Indian online tutoring and educational platform.
    Your task is to provide helpful, accurate responses to student and parent questions. 

    Here are the FAQs you should use as a knowledge base:

    {context}

    Important guidelines:
    1. Answer questions based on the FAQs provided above.
    2. Maintain a friendly, helpful tone suitable for students and parents.
    3. Keep responses concise but informative.
    4. If you're not confident about an answer, say so and suggest escalating to a human agent.
    5. Always use accurate information - do not make up answers.
    6. For educational questions, focus on explaining concepts clearly.

    Along with your response, detect the intent of the user's message and provide a confidence score.
    Your detected intent should be one of: 
    - general_inquiry
    - course_information 
    - payment_issue
    - technical_problem
    - exam_question
    - scheduling
    - complaint
    - feedback
    - career_advice
    - other

    Return your response in JSON format with fields: response, intent, confidence.

    Question: {question}
    Answer:

    """
    rag_prompt_custom = PromptTemplate.from_template(template)



    rag_chain=({"context": ret_ , "question": RunnablePassthrough()}|rag_prompt_custom|llm|StrOutputParser())
    ans=rag_chain.invoke(input_questions)
    
    
    try:
        match = re.search(r'{.*}', ans, re.DOTALL)
        if match:
            json_str = match.group(0)
            parsed_response = json.loads(json_str)
            print(parsed_response)
        else:
            ("No JSON found.")
        bot_response = parsed_response.get("response", "I'm sorry, I couldn't process your request.")
        intent = parsed_response.get("intent", "other")
        confidence = float(parsed_response.get("confidence", 0.0))
    except json.JSONDecodeError:
        # Fallback if response is not valid JSON
        logging.error(f"Failed to parse JSON response: {ans}")
        bot_response = "I apologize, but I'm experiencing some technical difficulties. Could you please try again?"
        intent = "other"
        confidence = 0.0
    return bot_response, intent, confidence

    



def embed_fassis(text):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
    # print(embeddings)
    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(tokenizer,chunk_size=1000, chunk_overlap=150)
    all_splits = text_splitter.split_text(text)
    # print("all_splits:",all_splits)
    # docs = [Document(page_content=chunk) for chunk in all_splits]
    # print("docs:",docs)
    # index = faiss.IndexFlatL2(len(embeddings.embed_query(" ")))
    

    # vector_store = FAISS(
    #     embedding_function=embeddings,
    #     index=index,
    #     docstore=InMemoryDocstore(),
    #     index_to_docstore_id={},
    # )
    # vector_store.add_documents(documents=docs)
    # vector_store.save_local("faiss_index")
    # return "File uploaded"

    docs = [Document(page_content=chunk) for chunk in all_splits]
    # Define dimension
    dimension = len(embeddings.embed_query(" "))
    #dimension  = The number of features in each embedding
    # Create HNSW index
    index = faiss.IndexHNSWFlat(dimension, 32)  # 32  Max number of connections each node (vector) can have.

    index.hnsw.efSearch = 64  # Search parameter (higher = better recall, slower)  "exploration factor during search"

    #It controls how many nodes (i.e., vectors/embeddings) the algorithm visits during a search query

    # Set metric (optional: L2 is default)
    index.metric_type = faiss.METRIC_L2
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    vector_store.add_documents(documents=docs)
    # ret_=vector_store.as_retriever()
    vector_store.save_local("faiss_index2")

    