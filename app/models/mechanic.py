"""
Modelo ORM do Mecânico / Técnico (models/mechanic.py).
"""
from sqlalchemy import Column, Integer, String, Boolean
from app.models.base import Base

class MechanicModel(Base):
    __tablename__ = "mechanics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(150), nullable=False)
    cpf = Column(String(25), nullable=True)
    celular = Column(String(30), nullable=True)
    especialidade = Column(String(100), nullable=True)
    ativo = Column(Boolean, default=True)
    date_created = Column(String(20), nullable=True)

    def to_dict(self):
        """Converte a entidade ORM em dicionário."""
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf or "",
            "celular": self.celular or "",
            "especialidade": self.especialidade or "Técnico Alinhador",
            "ativo": self.ativo,
            "date_created": self.date_created or ""
        }
