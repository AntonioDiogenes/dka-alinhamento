"""
Modelo ORM do Caminhão/Truck (models/truck.py).
"""
from sqlalchemy import Column, Integer, String
from app.models.base import Base

class TruckModel(Base):
    __tablename__ = "trucks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    brand_code = Column(String(10), nullable=False)
    brand_name = Column(String(50), nullable=False)
    category = Column(String(30), default="TRUCK")
    model_name = Column(String(100), nullable=False)
    rim_size = Column(String(10), default="22")
    axles_count = Column(Integer, default=3)

    def to_dict(self):
        """Converte a entidade ORM em dicionário."""
        return {
            "id": self.id,
            "brand_code": self.brand_code,
            "brand_name": self.brand_name,
            "category": self.category,
            "model_name": self.model_name,
            "rim_size": self.rim_size,
            "axles_count": self.axles_count
        }
