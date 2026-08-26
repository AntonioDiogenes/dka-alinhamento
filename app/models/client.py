"""
Modelo ORM do Cliente (models/client.py).
"""
from sqlalchemy import Column, Integer, String, Text, Boolean
from app.models.base import Base

class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    cpf_cnpj = Column(String(25), nullable=False)
    email = Column(String(120), nullable=True)
    celular = Column(String(30), nullable=True)
    telefone_fixo = Column(String(30), nullable=True)
    cep = Column(String(15), nullable=True)
    logradouro = Column(String(150), nullable=True)
    numero = Column(String(30), nullable=True)
    complemento = Column(String(100), nullable=True)
    bairro = Column(String(100), nullable=True)
    cidade = Column(String(100), nullable=True)
    uf = Column(String(5), nullable=True)
    observacoes = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)
    date_service = Column(String(20), nullable=True)

    def to_dict(self):
        """Converte a entidade ORM em dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf_cnpj": self.cpf_cnpj,
            "email": self.email or "",
            "celular": self.celular or "",
            "telefone_fixo": self.telefone_fixo or "",
            "cep": self.cep or "",
            "logradouro": self.logradouro or "",
            "numero": self.numero or "",
            "complemento": self.complemento or "",
            "bairro": self.bairro or "",
            "cidade": self.cidade or "",
            "uf": self.uf or "SP",
            "observacoes": self.observacoes or "",
            "ativo": self.ativo,
            "date_service": self.date_service or ""
        }
