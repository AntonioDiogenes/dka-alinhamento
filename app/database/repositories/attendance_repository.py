"""
Repositório de Atendimentos (database/repositories/attendance_repository.py).
Encapsula todas as operações de banco de dados para a entidade Atendimento/OS.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.attendance import AttendanceModel
from app.database.connection import get_session

class AttendanceRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        session = get_session()
        try:
            attendances = session.query(AttendanceModel).order_by(AttendanceModel.id.desc()).all()
            return [a.to_dict() for a in attendances]
        finally:
            session.close()

    @staticmethod
    def get_by_id(attendance_id: int) -> Optional[Dict[str, Any]]:
        session = get_session()
        try:
            att = session.query(AttendanceModel).filter(AttendanceModel.id == attendance_id).first()
            return att.to_dict() if att else None
        finally:
            session.close()

    @staticmethod
    def filter(
        date_filter: str = "",
        model_filter: str = "",
        plate_filter: str = "",
        client_filter: str = ""
    ) -> List[Dict[str, Any]]:
        session = get_session()
        try:
            query = session.query(AttendanceModel)

            if date_filter:
                query = query.filter(AttendanceModel.date_formatted.ilike(f"%{date_filter.strip()}%"))

            if model_filter:
                query = query.filter(AttendanceModel.model.ilike(f"%{model_filter.strip()}%"))

            if plate_filter:
                query = query.filter(AttendanceModel.plate.ilike(f"%{plate_filter.strip()}%"))

            if client_filter:
                query = query.filter(AttendanceModel.client.ilike(f"%{client_filter.strip()}%"))

            attendances = query.order_by(AttendanceModel.id.desc()).all()
            return [a.to_dict() for a in attendances]
        finally:
            session.close()

    @staticmethod
    def get_by_client_name_or_id(name_or_id: Any) -> List[Dict[str, Any]]:
        session = get_session()
        try:
            query = session.query(AttendanceModel)
            search_str = str(name_or_id).strip()
            query = query.filter(AttendanceModel.client.ilike(f"%{search_str}%"))
            attendances = query.order_by(AttendanceModel.id.desc()).all()
            return [a.to_dict() for a in attendances]
        finally:
            session.close()

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        session = get_session()
        try:
            now = datetime.now()
            new_att = AttendanceModel(
                date_formatted=data.get("date_formatted") or now.strftime("%d/%m/%Y %H:%M"),
                date_iso=data.get("date_iso") or now.strftime("%Y-%m-%d"),
                model=data.get("model", "Volvo FH 540"),
                plate=data.get("plate", "ABC-1D23"),
                client=data.get("client", "Cliente"),
                pdf_url=data.get("pdf_url", "")
            )
            session.add(new_att)
            session.commit()
            session.refresh(new_att)
            return new_att.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def delete(attendance_id: int) -> bool:
        session = get_session()
        try:
            att = session.query(AttendanceModel).filter(AttendanceModel.id == attendance_id).first()
            if att:
                session.delete(att)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
