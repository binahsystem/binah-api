from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator
from typing import Literal

from app.compras import pedidos
from app.estoque import produtos



router = APIRouter(
    prefix="/recebimentos",
    tags=["Recebimentos"]
)


# ============================================================
# DADOS TEMPORÁRIOS
# ============================================================

recebimentos = []


# ============================================================
# MODELO DE RECEBIMENTO
# ============================================================

class Recebimento(BaseModel):
    codigo: int | None = None
    pedido_codigo: int = Field(..., gt=0)

    observacao: str | None = None

    status: Literal[
        "Conferência pendente",
        "Recebido",
        "Divergência"
    ] = "Conferência pendente"

    @model_validator(mode="after")
    def validar_recebimento(self):

        if self.observacao is not None:
            self.observacao = self.observacao.strip()

        return self


# ============================================================
# CRIAR RECEBIMENTO
# ============================================================

@router.post("/", status_code=201)
def criar_recebimento(recebimento: Recebimento):

    # Procurar o pedido de compra
    pedido = None

    for pedido_existente in pedidos:
        if pedido_existente.codigo == recebimento.pedido_codigo:
            pedido = pedido_existente
            break

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido de compra não encontrado!"
        )

    # Verificar se já existe recebimento para esse pedido
    for recebimento_existente in recebimentos:
        if recebimento_existente.pedido_codigo == recebimento.pedido_codigo:
            raise HTTPException(
                status_code=409,
                detail="Esse pedido já possui um recebimento cadastrado!"
            )

    # Gerar código
    recebimento.codigo = len(recebimentos) + 1

    recebimentos.append(recebimento)

    return {
        "mensagem": "Recebimento criado com sucesso!",
        "recebimento": recebimento,
        "pedido": pedido
    }


# ============================================================
# LISTAR RECEBIMENTOS
# ============================================================

@router.get("/")
def listar_recebimentos():

    return {
        "total": len(recebimentos),
        "recebimentos": recebimentos
    }


# ============================================================
# CONSULTAR RECEBIMENTO
# ============================================================

@router.get("/{codigo}")
def consultar_recebimento(codigo: int):

    for recebimento in recebimentos:
        if recebimento.codigo == codigo:
            return recebimento

    raise HTTPException(
        status_code=404,
        detail="Recebimento não encontrado!"
    )


# ============================================================
# CONFIRMAR RECEBIMENTO
# ============================================================

@router.post("/{codigo}/confirmar")
def confirmar_recebimento(codigo: int):

    # Procurar o recebimento
    recebimento = None

    for r in recebimentos:
        if r.codigo == codigo:
            recebimento = r
            break

    if recebimento is None:
        raise HTTPException(
            status_code=404,
            detail="Recebimento não encontrado!"
        )

    # Não permitir confirmar duas vezes
    if recebimento.status == "Recebido":
        raise HTTPException(
            status_code=409,
            detail="Este recebimento já foi confirmado!"
        )

    # Procurar o pedido relacionado
    pedido = None

    for p in pedidos:
        if p.codigo == recebimento.pedido_codigo:
            pedido = p
            break

    if pedido is None:
        raise HTTPException(
            status_code=404,
            detail="Pedido de compra não encontrado!"
        )

    # ========================================================
    # PRIMEIRO: verificar se TODOS os produtos existem
    # ========================================================

    produtos_encontrados = []

    for item in pedido.itens:

        produto_encontrado = None

        for produto in produtos:
            if produto.nome.lower() == item.produto.lower():
                produto_encontrado = produto
                break

        if produto_encontrado is None:
            raise HTTPException(
                status_code=404,
                detail=f"Produto '{item.produto}' não está cadastrado no estoque."
            )

        produtos_encontrados.append(
            (produto_encontrado, item.quantidade)
        )

    # ========================================================
    # SEGUNDO: atualizar o estoque
    # ========================================================

    for produto, quantidade in produtos_encontrados:
        produto.quantidade += quantidade

    # ========================================================
    # TERCEIRO: atualizar o recebimento
    # ========================================================

    recebimento.status = "Recebido"

    # ========================================================
    # QUARTO: atualizar o pedido
    # ========================================================

    pedido.status = "Recebido"

    return {
        "mensagem": "Recebimento confirmado e estoque atualizado com sucesso!",
        "recebimento": recebimento,
        "pedido": pedido
    }