from fastapi import FastAPI
from app.estoque import router as estoque_router

app = FastAPI(title="BINAH API")


@app.get("/")
def inicio():
    return {
        "mensagem": "API BINAH funcionando!",
        "status": "online"
    }


app.include_router(estoque_router)