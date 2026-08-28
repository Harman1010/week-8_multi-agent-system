from state import AgentState

from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.prompts import ChatPromptTemplate

from utils.config import settings

from utils.prompts import QUERY_TRANSFORMATION_PROMPT

llm = ChatGoogleGenerativeAI(
    model = settings.model_name,
    gemini_api_key = settings.gemini_api_key,
    temperature=0
)

def transform_query(state:AgentState) -> str:

    prompt = ChatPromptTemplate.from_template(
        QUERY_TRANSFORMATION_PROMPT
    )

    chain = prompt | llm

    response = chain.invoke({
        "query" : state["query"]
    })

    transformed_query = response.content.strip()

    return {
        "transformed_query" : transformed_query,
        "status" : "query transformed"
    }

