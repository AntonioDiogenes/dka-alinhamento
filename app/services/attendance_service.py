"""
Serviço de Histórico de Atendimentos e Ordens de Serviço (services/attendance_service.py).
Conecta as Views de Atendimentos com o AttendanceRepository e a camada de banco criptografado SQLCipher.
"""
from typing import List, Dict, Any, Optional
from app.database.repositories.attendance_repository import AttendanceRepository

class AttendanceService:
    @staticmethod
    def get_all_attendances() -> List[Dict[str, Any]]:
        return AttendanceRepository.get_all()

    @staticmethod
    def get_attendance_by_id(attendance_id: int) -> Optional[Dict[str, Any]]:
        return AttendanceRepository.get_by_id(attendance_id)

    @staticmethod
    def filter_attendances(
        date_filter: str = "",
        model_filter: str = "",
        plate_filter: str = "",
        client_filter: str = ""
    ) -> List[Dict[str, Any]]:
        return AttendanceRepository.filter(
            date_filter=date_filter,
            model_filter=model_filter,
            plate_filter=plate_filter,
            client_filter=client_filter
        )

    @staticmethod
    def create_attendance(data: Dict[str, Any]) -> Dict[str, Any]:
        return AttendanceRepository.create(data)

    @staticmethod
    def delete_attendance(attendance_id: int) -> bool:
        return AttendanceRepository.delete(attendance_id)
