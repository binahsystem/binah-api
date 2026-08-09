from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/estoque", tags=["Estoque"])


# Modelo de produto
class Produto(BaseModel):
    nome: str = Field(..., min_length=1)
    quantidade: float = Field(..., ge=0)
    unidade: str = Field(..., min_length=1)
    estoque_minimo: float = Field(..., ge=0)


# Modelo para registrar saída
class SaidaEstoque(BaseModel):
    nome: str = Field(..., min_length=1)
    quantidade: float = Field(..., gt=0)

# Modelo para registrar entrada
class EntradaEstoque(BaseModel):
    nome: str = Field(..., min_length=1)
    quantidade: float = Field(..., gt=0)


# Banco temporário em memória
produtos = []


# Listar estoque
@router.get("/")
def listar_estoque():
    return {
        "total": len(produtos),
        "produtos": produtos
    }


# Cadastrar produto
@router.post("/")
def cadastrar_produto(produto: Produto):
    produtos.append(produto)

    return {
        "mensagem": "Produto cadastrado com sucesso!",
        "produto": produto
    }

# Registrar entrada no estoque
@router.post("/entrada")
def registrar_entrada(entrada: EntradaEstoque):
    for produto in produtos:
        if produto.nome == entrada.nome:
            produto.quantidade += entrada.quantidade

            return {
                "mensagem": "Entrada registrada com sucesso!",
                "produto": produto
            }

    return {
        "mensagem": "Produto não encontrado!"
    }


# Registrar saída de produto
@router.post("/saida")
def registrar_saida(saida: SaidaEstoque):

    # Procurar o produto pelo nome
    for produto in produtos:

        if produto.nome.lower() == saida.nome.lower():

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