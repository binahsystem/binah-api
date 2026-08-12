from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator


router = APIRouter(prefix="/fiscal", tags=["Fiscal"])


# Modelo de item da NF-e
class ItemNFe(BaseModel):
    produto: str = Field(..., min_length=1)
    quantidade: float = Field(..., gt=0)
    valor_unitario: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validar_item(self):
        self.produto = self.produto.strip()

        if not self.produto:
            raise ValueError("O produto não pode estar vazio.")

        return self


# Modelo da NF-e
class NFe(BaseModel):
    codigo: int | None = None
    numero: str = Field(..., min_length=1)
    serie: str = Field(default="1", min_length=1)
    chave_acesso: str = Field(..., min_length=1)
    fornecedor_codigo: int = Field(..., gt=0)
    itens: list[ItemNFe] = Field(..., min_length=1)
    status: str = "Pendente"

    @model_validator(mode="after")
    def validar_nfe(self):
        self.numero = self.numero.strip()
        self.serie = self.serie.strip()
        self.chave_acesso = self.chave_acesso.strip()

        if not self.numero:
            raise ValueError("O número da NF-e não pode estar vazio.")

        if not self.chave_acesso:
            raise ValueError("A chave de acesso não pode estar vazia.")

        return self


# Lista temporária de NF-es
notas_fiscais = []


# Cadastrar NF-e
@router.post("/", status_code=201)
def cadastrar_nfe(nfe: NFe):

    # Gerar código automaticamente
    nfe.codigo = len(notas_fiscais) + 1

    # Verificar se a chave já foi cadastrada
    for nota_existente in notas_fiscais:
        if nota_existente.chave_acesso == nfe.chave_acesso:
            raise HTTPException(
                status_code=409,
                detail="Esta NF-e já foi cadastrada!"
            )

    notas_fiscais.append(nfe)

    return {
        "mensagem": "NF-e cadastrada com sucesso!",
        "nfe": nfe
    }


# Listar NF-es
@router.get("/")
def listar_nfes():
    return {
        "total": len(notas_fiscais),
        "notas_fiscais": notas_fiscais
    }


# Consultar NF-e pelo código
@router.get("/{codigo}")
def consultar_nfe(codigo: int):

    for nfe in notas_fiscais:
        if nfe.codigo == codigo:
            return nfe

    raise HTTPException(
        status_code=404,
        detail="NF-e não encontrada!"
    )