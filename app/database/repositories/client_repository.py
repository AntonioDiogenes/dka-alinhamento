"""
Repositório de Clientes (database/repositories/client_repository.py).
Encapsula todas as operações de banco de dados para a entidade Cliente.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models.client import ClientModel
from app.models.attendance import AttendanceModel
from app.database.connection import get_session

class ClientRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        session = get_session()
        try:
            clients = session.query(ClientModel).order_by(ClientModel.id.desc()).all()
            return [c.to_dict() for c in clients]
        finally:
            session.close()

    @staticmethod
    def get_by_id(client_id: int) -> Optional[Dict[str, Any]]:
        session = get_session()
        try:
            client = session.query(ClientModel).filter(ClientModel.id == client_id).first()
            return client.to_dict() if client else None
        finally:
            session.close()

    @staticmethod
    def filter(
        nome_filter: str = "",
        doc_filter: str = "",
        cidade_filter: str = "",
        placa_filter: str = "",
        status_filter: str = "Todos",
        **kwargs
    ) -> List[Dict[str, Any]]:
        session = get_session()
        try:
            query = session.query(ClientModel)

            if nome_filter:
                n_str = nome_filter.strip()
                query = query.filter((ClientModel.nome.ilike(f"%{n_str}%")) | (ClientModel.name.ilike(f"%{n_str}%")))

            doc = doc_filter or kwargs.get("cpf_cnpj_filter", "")
            if doc:
                d_str = doc.strip()
                query = query.filter((ClientModel.cpf_cnpj.ilike(f"%{d_str}%")) | (ClientModel.document.ilike(f"%{d_str}%")))

            if cidade_filter:
                query = query.filter(ClientModel.cidade.ilike(f"%{cidade_filter.strip()}%"))

            placa = placa_filter or kwargs.get("placa", "")
            if placa:
                matching_atts = session.query(AttendanceModel.client).filter(
                    AttendanceModel.plate.ilike(f"%{placa.strip()}%")
                ).all()
                matching_names = [a[0] for a in matching_atts if a[0]]
                query = query.filter((ClientModel.nome.in_(matching_names)) | (ClientModel.name.in_(matching_names)))

            if status_filter == "Ativos":
                query = query.filter((ClientModel.ativo == True) | (ClientModel.is_active == True))
            elif status_filter == "Inativos":
                query = query.filter((ClientModel.ativo == False) | (ClientModel.is_active == False))

            clients = query.order_by(ClientModel.id.desc()).all()
            return [c.to_dict() for c in clients]
        finally:
            session.close()

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        session = get_session()
        try:
            date_val = data.get("date_service") or datetime.now().strftime("%d/%m/%Y")
            nome_val = data.get("nome", "").strip()
            doc_val = data.get("cpf_cnpj", "").strip()
            ativo_val = data.get("ativo", True)

            new_client = ClientModel(
                company_id=1,
                name=nome_val,
                document=doc_val,
                nome=nome_val,
                cpf_cnpj=doc_val,
                email=data.get("email", "").strip(),
                celular=data.get("celular", "").strip(),
                telefone_fixo=data.get("telefone_fixo", "").strip(),
                cep=data.get("cep", "").strip(),
                logradouro=data.get("logradouro", "").strip(),
                numero=data.get("numero", "").strip(),
                complemento=data.get("complemento", "").strip(),
                bairro=data.get("bairro", "").strip(),
                cidade=data.get("cidade", "").strip(),
                uf=data.get("uf", "SP").strip(),
                observacoes=data.get("observacoes", "").strip(),
                ativo=ativo_val,
                is_active=ativo_val,
                date_service=date_val
            )
            session.add(new_client)
            session.commit()
            session.refresh(new_client)
            return new_client.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def update(client_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        session = get_session()
        try:
            client = session.query(ClientModel).filter(ClientModel.id == client_id).first()
            if not client:
                return None

            for key in ["nome", "cpf_cnpj", "email", "celular", "telefone_fixo", "cep",
                        "logradouro", "numero", "complemento", "bairro", "cidade",
                        "uf", "observacoes", "ativo", "date_service"]:
                if key in data:
                    val = data[key]
                    setattr(client, key, val)
                    if key == "nome":
                        setattr(client, "name", val)
                    elif key == "cpf_cnpj":
                        setattr(client, "document", val)
                    elif key == "ativo":
                        setattr(client, "is_active", val)

            session.commit()
            session.refresh(client)
            return client.to_dict()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @staticmethod
    def delete(client_id: int) -> bool:
        session = get_session()
        try:
            client = session.query(ClientModel).filter(ClientModel.id == client_id).first()
            if client:
                session.delete(client)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
