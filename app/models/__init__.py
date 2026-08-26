"""
Pacote de Modelos ORM do SQLAlchemy (models/__init__.py).
"""
from app.models.base import Base
from app.models.client import ClientModel
from app.models.attendance import AttendanceModel
from app.models.truck import TruckModel

__all__ = ["Base", "ClientModel", "AttendanceModel", "TruckModel"]
