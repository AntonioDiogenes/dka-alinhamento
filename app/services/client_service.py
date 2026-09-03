"""
Serviço de Gestão de Clientes (services/client_service.py).
Conecta as Views de Clientes com o ClientRepository e a camada de banco de dados criptografado SQLCipher.
"""
from typing import List, Dict, Any, Optional
from app.database.repositories.client_repository import ClientRepository
from app.database.repositories.attendance_repository import AttendanceRepository

class ClientService:
    @staticmethod
    def get_all_clients() -> List[Dict[str, Any]]:
        return ClientRepository.get_all()

    @staticmethod
    def get_client_by_id(client_id: int) -> Optional[Dict[str, Any]]:
        return ClientRepository.get_by_id(client_id)

    @staticmethod
    def filter_clients(
        nome_filter: str = "",
        cpf_cnpj_filter: str = "",
        cidade_filter: str = "",
        placa_filter: str = "",
        status_filter: str = "Todos",
        **kwargs
    ) -> List[Dict[str, Any]]:
        return ClientRepository.filter(
            nome_filter=nome_filter,
            doc_filter=cpf_cnpj_filter,
            cidade_filter=cidade_filter,
            placa_filter=placa_filter,
            status_filter=status_filter,
            **kwargs
        )

    @staticmethod
    def save_client(client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cria ou atualiza um cliente no banco de dados criptografado."""
        c_id = client_data.get("id")
        if c_id:
            updated = ClientRepository.update(int(c_id), client_data)
            return updated or client_data
        else:
            return ClientRepository.create(client_data)

    @staticmethod
    def delete_client(client_id: int) -> bool:
        return ClientRepository.delete(client_id)

    @staticmethod
    def get_client_attendances(client_id: int) -> List[Dict[str, Any]]:
        client = ClientRepository.get_by_id(client_id)
        if not client:
            return []
        
        attendances = AttendanceRepository.get_by_client_name_or_id(client["nome"])
        res = []
        for att in attendances:
            res.append({
                "id": att["id"],
                "title": f"Alinhamento OS #{att['id']}",
                "status": "Finalizado",
                "status_color": "#10b981",
                "date": att["date_formatted"],
                "vehicle": f"{att['model']} ({att['plate']})",
                "pdf_url": att.get("pdf_url", "")
            })
        return res
