"""
Repositório de Caminhões (database/repositories/truck_repository.py).
Encapsula todas as operações de banco de dados para a entidade Caminhão/Truck.
"""
from typing import List, Dict, Any, Optional
from app.models.truck import TruckModel
from app.database.connection import get_session

class TruckRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        session = get_session()
        try:
            trucks = session.query(TruckModel).order_by(TruckModel.id.asc()).all()
            return [t.to_dict() for t in trucks]
        finally:
            session.close()

    @staticmethod
    def get_manufacturers() -> List[str]:
        session = get_session()
        try:
            brands = session.query(TruckModel.brand_name).distinct().order_by(TruckModel.brand_name.asc()).all()
            brand_list = [b[0] for b in brands if b[0]]
            return ["Todos os fabricantes"] + brand_list
        finally:
            session.close()

    @staticmethod
    def filter(
        search_text: str = "",
        manufacturer: str = "Todos os fabricantes",
        search_query: str = "",
        brand_filter: str = "Todos os fabricantes",
        **kwargs
    ) -> List[Dict[str, Any]]:
        s_query = search_text or search_query
        b_filter = manufacturer if manufacturer != "Todos os fabricantes" else brand_filter

        session = get_session()
        try:
            query = session.query(TruckModel)

            if b_filter and b_filter != "Todos os fabricantes":
                query = query.filter(TruckModel.brand_name == b_filter.strip())

            if s_query:
                sq = f"%{s_query.strip()}%"
                query = query.filter(
                    (TruckModel.model_name.ilike(sq)) |
                    (TruckModel.brand_name.ilike(sq)) |
                    (TruckModel.brand_code.ilike(sq))
                )

            trucks = query.order_by(TruckModel.id.asc()).all()
            return [t.to_dict() for t in trucks]
        finally:
            session.close()

    @staticmethod
    def get_brands_summary() -> List[Dict[str, Any]]:
        """Retorna marcas distintas com contagem de modelos associados."""
        session = get_session()
        try:
            trucks = session.query(TruckModel).all()
            brands_dict = {}
            for t in trucks:
                b_name = t.brand_name.strip() if t.brand_name else "Sem Marca"
                b_code = t.brand_code.strip() if t.brand_code else "---"
                if b_name not in brands_dict:
                    brands_dict[b_name] = {
                        "brand_name": b_name,
                        "brand_code": b_code,
                        "count": 0
                    }
                brands_dict[b_name]["count"] += 1
            
            result = list(brands_dict.values())
            result.sort(key=lambda x: x["brand_name"])
            return result
        finally:
            session.close()

    @staticmethod
    def update_brand(old_brand_name: str, new_brand_name: str, new_brand_code: str) -> bool:
        """Atualiza o nome e código da marca para todos os veículos associados."""
        session = get_session()
        try:
            trucks = session.query(TruckModel).filter(TruckModel.brand_name == old_brand_name).all()
            for t in trucks:
                t.brand_name = new_brand_name.strip()
                t.brand_code = new_brand_code.strip().upper()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"[TruckRepository] Erro ao atualizar marca: {e}")
            return False
        finally:
            session.close()

    @staticmethod
    def update_model(model_id: int, data: Dict[str, Any]) -> bool:
        """Atualiza os dados de um modelo específico por ID."""
        session = get_session()
        try:
            truck = session.query(TruckModel).filter(TruckModel.id == model_id).first()
            if not truck:
                return False
            
            if "model_name" in data:
                truck.model_name = data["model_name"].strip()
            if "brand_name" in data:
                truck.brand_name = data["brand_name"].strip()
            if "brand_code" in data:
                truck.brand_code = data["brand_code"].strip().upper()
            if "category" in data:
                truck.category = data["category"].strip()
            if "rim_size" in data:
                truck.rim_size = str(data["rim_size"]).strip()
            if "axles_count" in data:
                truck.axles_count = int(data["axles_count"])
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"[TruckRepository] Erro ao atualizar modelo: {e}")
            return False
        finally:
            session.close()
