"""
Repositório de Mecânicos / Técnicos (database/repositories/mechanic_repository.py).
Encapsula todas as operações de banco de dados para a entidade Mecânico.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.mechanic import MechanicModel
from app.database.connection import get_session

class MechanicRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        session = get_session()
        try:
            mechanics = session.query(MechanicModel).order_by(MechanicModel.id.asc()).all()
            return [m.to_dict() for m in mechanics]
        finally:
            session.close()

    @staticmethod
    def get_active() -> List[Dict[str, Any]]:
        session = get_session()
        try:
            mechanics = session.query(MechanicModel).filter(MechanicModel.ativo == True).order_by(MechanicModel.id.asc()).all()
            return [m.to_dict() for m in mechanics]
        finally:
            session.close()

    @staticmethod
    def get_by_id(mechanic_id: int) -> Optional[Dict[str, Any]]:
        session = get_session()
        try:
            mechanic = session.query(MechanicModel).filter(MechanicModel.id == mechanic_id).first()
            return mechanic.to_dict() if mechanic else None
        finally:
            session.close()

    @staticmethod
    def filter(
        nome_filter: str = "",
        especialidade_filter: str = "",
        status_filter: str = "Todos"
    ) -> List[Dict[str, Any]]:
        session = get_session()
        try:
            query = session.query(MechanicModel)

            if nome_filter:
                query = query.filter(MechanicModel.nome.ilike(f"%{nome_filter.strip()}%"))

            if especialidade_filter:
                query = query.filter(MechanicModel.especialidade.ilike(f"%{especialidade_filter.strip()}%"))

            if status_filter == "Ativos":
                query = query.filter(MechanicModel.ativo == True)
            elif status_filter == "Inativos":
                query = query.filter(MechanicModel.ativo == False)

            mechanics = query.order_by(MechanicModel.id.asc()).all()
            return [m.to_dict() for m in mechanics]
        finally:
            session.close()

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        session = get_session()
        try:
            date_val = data.get("date_created") or datetime.now().strftime("%d/%m/%Y")
            new_mechanic = MechanicModel(
                nome=data.get("nome", "").strip(),
                cpf=data.get("cpf", "").strip(),
                celular=data.get("celular", "").strip(),
                especialidade=data.get("especialidade", "Técnico Alinhador").strip(),
                ativo=data.get("ativo", True),
                date_created=date_val
            )
            session.add(new_mechanic)
            session.commit()
            session.refresh(new_mechanic)
            return new_mechanic.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def update(mechanic_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = get_session()
        try:
            mechanic = session.query(MechanicModel).filter(MechanicModel.id == mechanic_id).first()
            if not mechanic:
                return None

            for key in ["nome", "cpf", "celular", "especialidade", "ativo", "date_created"]:
                if key in data:
                    setattr(mechanic, key, data[key])

            session.commit()
            session.refresh(mechanic)
            return mechanic.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def delete(mechanic_id: int) -> bool:
        session = get_session()
        try:
            mechanic = session.query(MechanicModel).filter(MechanicModel.id == mechanic_id).first()
            if mechanic:
                session.delete(mechanic)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
