"""
Modelo ORM do Atendimento (models/attendance.py).
"""
from sqlalchemy import Column, Integer, String
from app.models.base import Base

class AttendanceModel(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_formatted = Column(String(50), nullable=False)
    date_iso = Column(String(20), nullable=False)
    model = Column(String(150), nullable=False)
    plate = Column(String(20), nullable=False)
    client = Column(String(150), nullable=False)
    pdf_url = Column(String(255), nullable=True)

    def to_dict(self):
        """Converte a entidade ORM em dicionário."""
        return {
            "id": self.id,
            "date_formatted": self.date_formatted,
            "date_iso": self.date_iso,
            "model": self.model,
            "plate": self.plate,
            "client": self.client,
            "pdf_url": self.pdf_url or ""
        }
