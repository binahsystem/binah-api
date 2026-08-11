from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator


router = APIRouter(prefix="/estoque", tags=["Estoque"])


# Modelo de produto
class Produto(BaseModel):
    codigo: int | None = None
    nome: str = Field(..., min_length=1)
    quantidade: float = Field(..., ge=0)
    unidade: str = Field(..., min_length=1)
    estoque_minimo: float = Field(..., ge=0)

    @model_validator(mode="after")
    def validar_produto(self):
        self.nome = self.nome.strip()
        self.unidade = self.unidade.strip()

        if not self.nome:
            raise ValueError("O nome do produto não pode estar vazio.")

        if not self.unidade:
            raise ValueError("A unidade do produto não pode estar vazia.")

        return self


# Modelo para registrar saída
class SaidaEstoque(BaseModel):
    codigo: int | None = Field(default=None, gt=0)
    nome: str | None = Field(default=None, min_length=1)
    quantidade: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validar_produto(self):
        if self.codigo is None and not self.nome:
            raise ValueError("Informe o código ou o nome do produto.")

        if self.nome is not None:
            self.nome = self.nome.strip()

            if not self.nome:
                raise ValueError("O nome do produto não pode estar vazio.")

        return self


# Modelo para registrar entrada
class EntradaEstoque(BaseModel):
    codigo: int | None = Field(default=None, gt=0)
    nome: str | None = Field(default=None, min_length=1)
    quantidade: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validar_produto(self):
        if self.codigo is None and not self.nome:
            raise ValueError("Informe o código ou o nome do produto.")

        if self.nome is not None:
            self.nome = self.nome.strip()

            if not self.nome:
                raise ValueError("O nome do produto não pode estar vazio.")

        return self


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
@router.post("/", status_code=201)
def cadastrar_produto(produto: Produto):

    # Verificar se o produto já está cadastrado
    for p in produtos:
        if p.nome.lower() == produto.nome.lower():
            raise HTTPException(
                status_code=409,
                detail="Produto já cadastrado!"
            )

    produto.codigo = len(produtos) + 1
    produtos.append(produto)

    return {
        "mensagem": "Produto cadastrado com sucesso!",
        "produto": produto
    }

# Consultar produto pelo código

@router.get("/{codigo}")
def consultar_produto(codigo: int):
    for produto in produtos:
        if produto.codigo == codigo:
            return produto

    raise HTTPException(
        status_code=404,
        detail="Produto não encontrado!"
    )

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

    raise HTTPException(
        status_code=404,
        detail="Produto não encontrado!"
            )


# Registrar saída de produto
@router.post("/saida")
def registrar_saida(saida: SaidaEstoque):

     # Procurar o produto pelo código ou pelo nome
    produto_encontrado = None

    for produto in produtos:

        if saida.codigo is not None and produto.codigo == saida.codigo:
            produto_encontrado = produto
            break

        if saida.nome is not None and produto.nome.lower() == saida.nome.lower():
            produto_encontrado = produto
            break

    if produto_encontrado is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado!"
        )

    # Verificar se existe quantidade suficiente
    if saida.quantidade > produto_encontrado.quantidade:
        raise HTTPException(
            status_code=400,
            detail="Quantidade insuficiente em estoque!"
        )


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