from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/estoque", tags=["Estoque"])


# Modelo de produto
class Produto(BaseModel):
    codigo: int | None = None
    nome: str = Field(..., min_length=1)
    quantidade: float = Field(..., ge=0)
    unidade: str = Field(..., min_length=1)
    estoque_minimo: float = Field(..., ge=0)


# Modelo para registrar saída
class SaidaEstoque(BaseModel):
    codigo: int | None = None
    nome: str | None = None
    quantidade: float = Field(..., gt=0)

# Modelo para registrar entrada
class EntradaEstoque(BaseModel):
    codigo: int | None = None
    nome: str | None = None
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
    produto.codigo = len(produtos) + 1
    produtos.append(produto)

    return {
        "mensagem": "Produto cadastrado com sucesso!",
        "produto": produto
    }

# Registrar entrada no estoque
@router.post("/entrada")
def registrar_entrada(entrada: EntradaEstoque):
    for produto in produtos:

        # Procurar pelo código
        if entrada.codigo is not None and produto.codigo == entrada.codigo:
            produto.quantidade += entrada.quantidade

            return {
                "mensagem": "Entrada registrada com sucesso!",
                "produto": produto
            }

        # Procurar pelo nome
        if entrada.nome is not None and produto.nome.lower() == entrada.nome.lower():
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

    # Procurar o produto pelo código ou pelo nome
    for produto in produtos:

        # Procurar pelo código
        if saida.codigo is not None and produto.codigo == saida.codigo:
            produto_encontrado = produto
            break

        # Procurar pelo nome
        if saida.nome is not None and produto.nome.lower() == saida.nome.lower():
            produto_encontrado = produto
            break

    else:
        return {
            "mensagem": "Produto não encontrado!",
            "estoque_baixo": False
        }

    # Verificar se existe quantidade suficiente
    if saida.quantidade > produto_encontrado.quantidade:
        return {
            "mensagem": "Quantidade insuficiente em estoque!",
            "produto": produto_encontrado,
            "estoque_baixo": False
        }

    # Retirar a quantidade
    produto_encontrado.quantidade -= saida.quantidade

    # Verificar se ficou abaixo do estoque mínimo
    estoque_baixo = (
        produto_encontrado.quantidade < produto_encontrado.estoque_minimo
    )

    # Mensagem normal
    mensagem = "Saída registrada com sucesso!"

    # Mensagem de alerta
    if estoque_baixo:
        mensagem = (
            f"⚠️ Estoque baixo! "
            f"O produto {produto_encontrado.nome} está com apenas "
            f"{produto_encontrado.quantidade} unidades."
        )

    return {
        "mensagem": mensagem,
        "produto": produto_encontrado,
        "estoque_baixo": estoque_baixo
    }