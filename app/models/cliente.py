"""
Modelo Entidade Cliente (models/cliente.py).
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Cliente:
    id: Optional[int] = None
    nome: str = ""
    cpf_cnpj: str = ""
    email: str = ""
    celular: str = ""
    telefone_fixo: str = ""
    cep: str = ""
    logradouro: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    uf: str = "SP"
    observacoes: str = ""
    ativo: bool = True
