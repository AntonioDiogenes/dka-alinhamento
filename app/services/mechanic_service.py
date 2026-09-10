"""
Serviço de Gestão de Mecânicos / Técnicos (services/mechanic_service.py).
Conecta as Views de Mecânicos com o MechanicRepository.
"""
from typing import List, Dict, Any, Optional
from app.database.repositories.mechanic_repository import MechanicRepository

class MechanicService:
    @staticmethod
    def get_all_mechanics() -> List[Dict[str, Any]]:
        """Retorna a lista de todos os mecânicos cadastrados."""
        try:
            return MechanicRepository.get_all()
        except Exception:
            return []

    @staticmethod
    def get_active_mechanics() -> List[Dict[str, Any]]:
        """Retorna apenas mecânicos ativos."""
        try:
            return MechanicRepository.get_active()
        except Exception:
            return []

    @staticmethod
    def get_mechanic_by_id(mechanic_id: int) -> Optional[Dict[str, Any]]:
        """Busca um mecânico por ID."""
        return MechanicRepository.get_by_id(mechanic_id)

    @staticmethod
    def filter_mechanics(
        nome_filter: str = "",
        especialidade_filter: str = "",
        status_filter: str = "Todos"
    ) -> List[Dict[str, Any]]:
        """Filtra a lista de mecânicos."""
        return MechanicRepository.filter(
            nome_filter=nome_filter,
            especialidade_filter=especialidade_filter,
            status_filter=status_filter
        )

    @staticmethod
    def save_mechanic(mechanic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria ou atualiza um mecânico no banco de dados."""
        m_id = mechanic_data.get("id")
        if m_id:
            updated = MechanicRepository.update(int(m_id), mechanic_data)
            return updated or mechanic_data
        else:
            return MechanicRepository.create(mechanic_data)

    @staticmethod
    def delete_mechanic(mechanic_id: int) -> bool:
        """Remove um mecânico do banco de dados."""
        return MechanicRepository.delete(mechanic_id)
