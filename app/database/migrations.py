"""
Gerenciador de Migrações e Inicialização de Dados (database/migrations.py).
Executa na primeira inicialização do sistema:
1. Aplica a chave de criptografia SQLCipher.
2. Cria as tabelas do sistema via SQLAlchemy Base.metadata.
3. Popula os dados iniciais caso o banco esteja vazio.
"""
from typing import List, Dict, Any
from app.models.base import Base
from app.models.client import ClientModel
from app.models.attendance import AttendanceModel
from app.models.truck import TruckModel
from app.database.connection import get_engine, get_session, validate_connection

# Dados iniciais para seeding na primeira execução
SEED_CLIENTS = [
    {
        "nome": "Logística TransBrasil Ltda",
        "cpf_cnpj": "12.345.678/0001-90",
        "email": "contato@transbrasil.com.br",
        "celular": "(11) 98765-4321",
        "telefone_fixo": "(11) 3344-5566",
        "cep": "01310-100",
        "logradouro": "Av. Paulista",
        "numero": "1000",
        "complemento": "Conj 501",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "uf": "SP",
        "observacoes": "Cliente preferencial de frota pesada (Volvo e Scania).",
        "ativo": True,
        "date_service": "17/08/2026"
    },
    {
        "nome": "Transportes Rodoviários Santos",
        "cpf_cnpj": "98.765.432/0001-10",
        "email": "financeiro@tprsantos.com.br",
        "celular": "(13) 99123-4567",
        "telefone_fixo": "(13) 3211-9988",
        "cep": "11010-010",
        "logradouro": "Rua XV de Novembro",
        "numero": "45",
        "complemento": "",
        "bairro": "Centro",
        "cidade": "Santos",
        "uf": "SP",
        "observacoes": "Atendimento agendado quinzenalmente.",
        "ativo": True,
        "date_service": "17/08/2026"
    },
    {
        "nome": "Expresso Anhanguera Cargas",
        "cpf_cnpj": "45.112.890/0001-44",
        "email": "operacoes@anhangueracargas.com",
        "celular": "(19) 97400-1122",
        "telefone_fixo": "(19) 3871-2200",
        "cep": "13010-000",
        "logradouro": "Av. Francisco Glicério",
        "numero": "890",
        "complemento": "Galpão B",
        "bairro": "Centro",
        "cidade": "Campinas",
        "uf": "SP",
        "observacoes": "Manutenção corretiva e alinhamento de 3 eixos.",
        "ativo": True,
        "date_service": "16/08/2026"
    },
    {
        "nome": "Frota Agrícola Centro-Oeste",
        "cpf_cnpj": "33.998.112/0001-88",
        "email": "suporte@agricolaco.com.br",
        "celular": "(62) 98111-3344",
        "telefone_fixo": "(62) 3512-4400",
        "cep": "74000-000",
        "logradouro": "Rodovia BR-153",
        "numero": "KM 12",
        "complemento": "",
        "bairro": "Zona Rural",
        "cidade": "Goiânia",
        "uf": "GO",
        "observacoes": "Faturamento faturado 30 dias.",
        "ativo": True,
        "date_service": "16/08/2026"
    },
    {
        "nome": "Comércio e Distribuidora Vale",
        "cpf_cnpj": "77.654.321/0001-55",
        "email": "gerencia@distribuidoravale.com",
        "celular": "(31) 99887-6655",
        "telefone_fixo": "(31) 3290-1122",
        "cep": "30130-000",
        "logradouro": "Av. Afonso Pena",
        "numero": "1500",
        "complemento": "Loja 2",
        "bairro": "Funcionários",
        "cidade": "Belo Horizonte",
        "uf": "MG",
        "observacoes": "Requer relatório impresso ao entregar veículo.",
        "ativo": True,
        "date_service": "15/08/2026"
    }
]

SEED_ATTENDANCES = [
    {
        "date_formatted": "17/08/2026 14:30",
        "date_iso": "2026-08-17",
        "model": "Volvo FH 540 Globetrotter 6x4",
        "plate": "ABC-1D23",
        "client": "Logística TransBrasil Ltda",
        "pdf_url": "https://oficina.example.com/os/1042.pdf"
    },
    {
        "date_formatted": "17/08/2026 11:15",
        "date_iso": "2026-08-17",
        "model": "Scania R450 Streamline 6x2",
        "plate": "BRA-2E19",
        "client": "Transportes Rodoviários Santos",
        "pdf_url": "https://oficina.example.com/os/1041.pdf"
    },
    {
        "date_formatted": "16/08/2026 16:45",
        "date_iso": "2026-08-16",
        "model": "Mercedes-Benz Actros 2651",
        "plate": "XYZ-9876",
        "client": "Expresso Anhanguera Cargas",
        "pdf_url": "https://oficina.example.com/os/1040.pdf"
    },
    {
        "date_formatted": "16/08/2026 09:20",
        "date_iso": "2026-08-16",
        "model": "DAF XF 530 Super Space Cab",
        "plate": "KTM-4410",
        "client": "Frota Agrícola Centro-Oeste",
        "pdf_url": "https://oficina.example.com/os/1039.pdf"
    },
    {
        "date_formatted": "15/08/2026 15:10",
        "date_iso": "2026-08-15",
        "model": "MAN TGX 28.440 6x2",
        "plate": "OFN-7733",
        "client": "Comércio e Distribuidora Vale",
        "pdf_url": "https://oficina.example.com/os/1038.pdf"
    }
]

SEED_TRUCKS = [
    {"brand_code": "VOL", "brand_name": "Volvo", "category": "TRUCK", "model_name": "FH 540 Globetrotter", "rim_size": "22", "axles_count": 3},
    {"brand_code": "SCA", "brand_name": "Scania", "category": "TRUCK", "model_name": "R 450 Streamline", "rim_size": "22.5", "axles_count": 3},
    {"brand_code": "MER", "brand_name": "Mercedes-Benz", "category": "TRUCK", "model_name": "Actros 2651 6x4", "rim_size": "22", "axles_count": 3},
    {"brand_code": "DAF", "brand_name": "DAF", "category": "TRUCK", "model_name": "XF 530 Super Space", "rim_size": "22.5", "axles_count": 3},
    {"brand_code": "MAN", "brand_name": "MAN", "category": "TRUCK", "model_name": "TGX 28.440 6x2", "rim_size": "22", "axles_count": 3},
    {"brand_code": "IVE", "brand_name": "Iveco", "category": "TRUCK", "model_name": "Stralis Hi-Way 600", "rim_size": "22.5", "axles_count": 3},
    {"brand_code": "VW", "brand_name": "Volkswagen", "category": "TRUCK", "model_name": "Constellation 24.280", "rim_size": "22", "axles_count": 3},
    {"brand_code": "VOL", "brand_name": "Volvo", "category": "TRUCK", "model_name": "VM 330 6x2", "rim_size": "22.5", "axles_count": 2},
    {"brand_code": "SCA", "brand_name": "Scania", "category": "TRUCK", "model_name": "S 500 V8 Highline", "rim_size": "22.5", "axles_count": 3}
]

def run_migrations():
    """Inicializa as tabelas no banco de dados criptografado e roda o seeder caso necessário."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    validate_connection()

    session = get_session()
    try:
        # Seeder de Clientes
        if session.query(ClientModel).count() == 0:
            for c_data in SEED_CLIENTS:
                session.add(ClientModel(**c_data))

        # Seeder de Atendimentos
        if session.query(AttendanceModel).count() == 0:
            for a_data in SEED_ATTENDANCES:
                session.add(AttendanceModel(**a_data))

        # Seeder de Caminhões
        if session.query(TruckModel).count() == 0:
            for t_data in SEED_TRUCKS:
                session.add(TruckModel(**t_data))

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
