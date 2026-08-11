from fastapi import FastAPI
from app.estoque import router as estoque_router
from app.compras import router as compras_router
from app.recebimentos import router as recebimentos_router
app = FastAPI(title="BINAH API")


@app.get("/")
def inicio():
    return {
        "mensagem": "API BINAH funcionando!",
        "status": "online"
    }


app.include_router(estoque_router)
app.include_router(compras_router)
app.include_router(recebimentos_router)