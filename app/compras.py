from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator
from typing import Literal


router = APIRouter(prefix="/compras", tags=["Compras"])


# ============================================================
# DADOS TEMPORÁRIOS
# ============================================================

fornecedores = []
pedidos = []


# ============================================================
# FORNECEDOR
# ============================================================

class Fornecedor(BaseModel):
    codigo: int | None = None
    nome: str = Field(..., min_length=1)
    cnpj: str = Field(..., min_length=11)
    ativo: bool = True

    @model_validator(mode="after")
    def validar_fornecedor(self):
        self.nome = self.nome.strip()
        self.cnpj = self.cnpj.strip()

        if not self.nome:
            raise ValueError("O nome do fornecedor não pode estar vazio.")

        if not self.cnpj:
            raise ValueError("O CNPJ do fornecedor não pode estar vazio.")

        return self


# ============================================================
# ITEM DO PEDIDO
# ============================================================

class ItemPedido(BaseModel):
    produto: str = Field(..., min_length=1)
    quantidade: float = Field(..., gt=0)
    preco_unitario: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validar_item(self):
        self.produto = self.produto.strip()

        if not self.produto:
            raise ValueError("O produto não pode estar vazio.")

        return self


# ============================================================
# PEDIDO DE COMPRA
# ============================================================

class PedidoCompra(BaseModel):
    codigo: int | None = None
    fornecedor: str = Field(..., min_length=1)
    itens: list[ItemPedido] = Field(..., min_length=1)

    status: Literal[
        "Pendente",
        "Enviado",
        "Parcialmente recebido",
        "Recebido",
        "Concluído"
    ] = "Pendente"

    observacao: str | None = None

    @model_validator(mode="after")
    def validar_pedido(self):
        self.fornecedor = self.fornecedor.strip()

        if not self.fornecedor:
            raise ValueError("O fornecedor não pode estar vazio.")

        return self


# ============================================================
# CADASTRAR FORNECEDOR
# ============================================================

@router.post("/fornecedores", status_code=201)
def cadastrar_fornecedor(fornecedor: Fornecedor):

    fornecedor.codigo = len(fornecedores) + 1

    for fornecedor_existente in fornecedores:
        if fornecedor_existente.cnpj == fornecedor.cnpj:
            raise HTTPException(
                status_code=409,
                detail="Fornecedor já cadastrado!"
            )

    fornecedores.append(fornecedor)

    return {
        "mensagem": "Fornecedor cadastrado com sucesso!",
        "fornecedor": fornecedor
    }


# ============================================================
# LISTAR FORNECEDORES
# ============================================================

@router.get("/fornecedores")
def listar_fornecedores():

    return {
        "total": len(fornecedores),
        "fornecedores": fornecedores
    }


# ============================================================
# CONSULTAR FORNECEDOR
# ============================================================

@router.get("/fornecedores/{codigo}")
def consultar_fornecedor(codigo: int):

    for fornecedor in fornecedores:
        if fornecedor.codigo == codigo:
            return fornecedor

    raise HTTPException(
        status_code=404,
        detail="Fornecedor não encontrado!"
    )


# ============================================================
# CADASTRAR PEDIDO DE COMPRA
# ============================================================

@router.post("/pedidos", status_code=201)
def cadastrar_pedido(pedido: PedidoCompra):

    pedido.codigo = len(pedidos) + 1

    pedidos.append(pedido)

    return {
        "mensagem": "Pedido de compra cadastrado com sucesso!",
        "pedido": pedido
    }


# ============================================================
# LISTAR PEDIDOS
# ============================================================

@router.get("/pedidos")
def listar_pedidos():

    return {
        "total": len(pedidos),
        "pedidos": pedidos
    }


# ============================================================
# CONSULTAR PEDIDO
# ============================================================

@router.get("/pedidos/{codigo}")
def consultar_pedido(codigo: int):

    for pedido in pedidos:
        if pedido.codigo == codigo:
            return pedido

    raise HTTPException(
        status_code=404,
        detail="Pedido de compra não encontrado!"
    )