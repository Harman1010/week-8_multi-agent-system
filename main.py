#def main():

    #while True:

        #print("Welcome to Multi-Agent System")

        #print("Enter `exit` to quit")

        #query = input("Enter your query")

        #if(query.lower() == 'exit'):

            #break

#if __name__ == "__main__":

    #main()



#from langchain_google_genai import ChatGoogleGenerativeAI

#from utils.config import settings

#llm = ChatGoogleGenerativeAI(
 #   model=settings.model_name,
  #  gemini_api_key=settings.gemini_api_key,
   # temperature=0.2
#)

#response = llm.invoke("What is the weather like in Delhi?")

#print(response.content)

from graph import create_graph


graph = create_graph()

initial_state = {
    "query": "tell me recent stuff about ai agents and also give python code example",
    "transformed_query": "",
    "plan": [],
    "results": {},
    "observations": [],
    "status": ""
}

result = graph.invoke(initial_state)

print("Original query")
print(result["query"])

print("Transformed query")
print(result["transformed_query"])