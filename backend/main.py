from fastapi import FastAPI, HTTPException

from fastapi.staticfiles import StaticFiles

from fastapi.responses import FileResponse

from fastapi.middleware.cors import CORSMiddleware

from backend.schema import AgentRequest, AgentResponse

from graph import create_graph

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="frontend"),
    name="static"
)

app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=False,
    allow_origins=["*"]
)

graph = create_graph()

@app.get("/")
def get_home():

    return FileResponse("frontend/index.html")

@app.post("/chat",response_model=AgentResponse)
def get_answer(request:AgentRequest):

    try:
        result = graph.invoke({
            "query" : request.query
        })

        response = AgentResponse(
            answer=result["answer"]
        )

        return response

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Sorry,Unable to process your request due to Internal Server Error."
        )