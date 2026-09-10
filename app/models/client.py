"""
Modelo ORM do Cliente (models/client.py).
"""
from sqlalchemy import Column, Integer, String, Text, Boolean
from app.models.base import Base

class ClientModel(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, default=1, nullable=True)
    name = Column(String(150), nullable=True)
    document = Column(String(25), nullable=True)
    nome = Column(String(150), nullable=True)
    cpf_cnpj = Column(String(25), nullable=True)
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
    is_active = Column(Boolean, default=True)
    date_service = Column(String(20), nullable=True)

    def to_dict(self):
        """Converte a entidade ORM em dicionário."""
        nome_val = self.nome or self.name or ""
        cpf_cnpj_val = self.cpf_cnpj or self.document or ""
        ativo_val = self.ativo if self.ativo is not None else (self.is_active if self.is_active is not None else True)
        return {
            "id": self.id,
            "nome": nome_val,
            "cpf_cnpj": cpf_cnpj_val,
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
            "ativo": ativo_val,
            "date_service": self.date_service or ""
        }
