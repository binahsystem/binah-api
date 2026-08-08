from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/estoque",
    tags=["Estoque"]
)


class Produto(BaseModel):
    nome: str
    quantidade: float
    unidade: str
    estoque_minimo: float


class SaidaEstoque(BaseModel):
    nome: str
    quantidade: float


# Banco temporário em memória
produtos = []


@router.get("/")
def listar_estoque():
    return {
        "total": len(produtos),
        "produtos": produtos
    }


@router.post("/")
def cadastrar_produto(produto: Produto):
    produtos.append(produto)

    return {
        "mensagem": "Produto cadastrado com sucesso!",
        "produto": produto
    }


@router.post("/saida")
def registrar_saida(saida: SaidaEstoque):

    # Procurar o produto pelo nome
    for produto in produtos:

        if produto.nome == saida.nome:

            # Verificar se existe quantidade suficiente
            if saida.quantidade > produto.quantidade:
                return {
                    "mensagem": "Quantidade insuficiente em estoque!",
                    "produto": produto,
                    "estoque_baixo": False
                }

            # Retirar a quantidade
            produto.quantidade -= saida.quantidade

            # Verificar se ficou abaixo do estoque mínimo
            estoque_baixo = produto.quantidade < produto.estoque_minimo

            # Mensagem normal
            mensagem = "Saída registrada com sucesso!"

            # Mensagem de alerta
            if estoque_baixo:
                mensagem = (
                    f"⚠️ Estoque baixo! "
                    f"O produto {produto.nome} está com apenas "
                    f"{produto.quantidade} unidades."
                )

            return {
                "mensagem": mensagem,
                "produto": produto,
                "estoque_baixo": estoque_baixo
            }

    # Produto não encontrado
    return {
        "mensagem": "Produto não encontrado!",
        "estoque_baixo": False
    }