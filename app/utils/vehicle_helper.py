"""
Utilitário de Classificação Inteligente de Veículos (utils/vehicle_helper.py).
Classifica veículos (Passeio/Leve vs Caminhão Rígido vs Cavalo Mecânico) com base na marca e modelo,
mesmo quando a tabela legada no banco de dados atribui 'category' = 'TRUCK' para todos.
"""

HEAVY_BRANDS = {
    'SCANIA', 'VOLVO', 'DAF', 'MAN', 'IVECO', 'SINOTRUK', 'INTERNATIONAL',
    'MARCOPOLO', 'VOLARE', 'CARRETA', 'AGRALE', 'SHACMAN', 'FOTON'
}

HEAVY_MODELS_KEYWORDS = [
    'ACTROS', 'ATEGO', 'AXOR', 'ACCELO', '1620', '1938', '1113', '1318', '710', '915', 'AROCS', 'ZETROS',
    'CONSTELLATION', 'DELIVERY', 'METEOR', 'WORKER', 'TITAN', 'COMPOSIÇÃO', 'CAVALO', 'SEMIRREBOQUE',
    'CARGO', 'F-350', 'F-4000', 'F-12000', 'F-14000', 'F-25000', 'SHACMAN', 'AUMARK'
]

LIGHT_BRANDS = {
    'FIAT', 'CHEVROLET GM', 'TOYOTA', 'HONDA', 'HYUNDAI', 'RENAULT', 'NISSAN', 'PEUGEOT',
    'CITROEN', 'JEEP', 'BMW', 'AUDI', 'BYD', 'CHERY', 'JAC MOTORS', 'KIA', 'MITSUBISHI',
    'PORSCHE', 'SUBARU', 'SUZUKI', 'MINI', 'RAM', 'LADA', 'SEAT', 'SMART', 'GWM', 'EFFA',
    'HAFEI', 'LIFAN', 'TROLLER', 'JAGUAR', 'LAND ROVER', 'LEXUS', 'MASERATI', 'ALFA ROMEO',
    'ASTON MARTIN', 'FERRARI', 'LAMBORGUINI', 'ROLLS ROYCE', 'TESLA', 'GURGEL', 'ACURA',
    'AM GENERAL GM', 'ASIA MOTORS', 'BUICK', 'CADILLAC', 'CHRYSLER', 'DAEWOO', 'DAIHATSU',
    'DKW VEMAG', 'DODGE', 'EAGLE', 'INFINITI', 'ISUZU', 'LANCIA', 'LINCOLN', 'LOTUS',
    'MAHINDRA', 'MAZDA', 'MERCURY', 'PLYMOUTH', 'PONTIAC GM', 'PUMA', 'ROVER', 'SAAB',
    'SATURN GM', 'SIMCA', 'TAC MOTORS', 'WILLYS OVERLAND'
}

LIGHT_MODEL_KEYWORDS = [
    'UNO', 'COROLLA', 'GOL', 'CIVIC', 'ONIX', 'PALIO', 'HB20', 'SIENA', 'CELTA', 'KA',
    'FIESTA', 'FOCUS', 'FOX', 'POLO', 'FIT', 'CITY', 'HR-V', 'CRETA', 'KICKS', 'ARGO',
    'MOBI', 'KWID', 'SANDERO', 'LOGAN', 'SAVEIRO', 'STRADA', 'HILUX', 'RANGER', 'S10',
    'TORO', 'COMPASS', 'RENEGADE', 'CRONOS', 'FASTBACK', 'PULSE', 'TITANO', 'DUCATO',
    'SCUDO', 'DOBLO', 'FIORINO', 'FUSCA', 'KOMBI', 'PASSAT', 'SANTANA', 'PARATI',
    'JETTA', 'BORA', 'GOLF', 'VIRTUS', 'T-CROSS', 'NIVUS', 'TAOS', 'TIGUAN', 'UP',
    'VOYAGE', 'MONTANA', 'TRACKER', 'EQUINOX', 'SPIN', 'CRUZE', 'PRISMA', 'COBALT',
    'ASTRA', 'VECTRA', 'CORSA', 'MERIVA', 'ZAFIRA', 'OMEGA', 'CHEVETTE', 'KADETT',
    'MONZA', 'OPALA', 'ETIOS', 'YARIS', 'RAV4', 'SW4', 'CAMRY', 'COROLLA CROSS'
]

def classify_vehicle_type(brand: str, model: str, category: str = "") -> str:
    """
    Classifica um veículo em: 'Veículo Passeio / Leve', 'Caminhão Rígido' ou 'Cavalo Mecânico'.
    """
    brand_u = (brand or "").upper().strip()
    model_u = (model or "").upper().strip()
    cat_u = (category or "").upper().strip()

    # Se a marca for de caminhões pesados
    if brand_u in HEAVY_BRANDS:
        if any(k in model_u for k in ['RIGID', 'RÍGIDO', 'RIGIDO', 'TOCO', 'CHASSI', 'BUS', 'ÔNIBUS', 'VOLARE', 'AGRALE']):
            return 'Caminhão Rígido'
        return 'Cavalo Mecânico'

    # Se o modelo for um caminhão pesado (mesmo em marcas mistas como Mercedes, VW, Ford)
    if any(k in model_u for k in HEAVY_MODELS_KEYWORDS):
        if any(k in model_u for k in ['RIGID', 'RÍGIDO', 'RIGIDO', 'TOCO', 'CHASSI', 'BAÚ', 'BAU', 'DELIVERY', 'ACCELO', 'ATEGO']):
            return 'Caminhão Rígido'
        return 'Cavalo Mecânico'

    # Se a marca for de carros de passeio / utilitários leves
    if brand_u in LIGHT_BRANDS:
        return 'Veículo Passeio / Leve'

    # Se o modelo tiver palavra-chave de carro de passeio / utilitário
    if any(k in model_u for k in LIGHT_MODEL_KEYWORDS):
        return 'Veículo Passeio / Leve'

    # Checagem por categoria
    if any(k in cat_u for k in ['PASSENGER', 'PASSEIO', 'CAR', 'AUTOMOVEL', 'AUTOMÓVEL', 'LEVE', 'UTILITARIO', 'UTILITÁRIO', 'SUV', 'PICKUP']):
        return 'Veículo Passeio / Leve'

    if any(k in cat_u or k in model_u for k in ['RIGID', 'RÍGIDO', 'RIGIDO', 'TOCO', '3/4', 'CHASSI']):
        return 'Caminhão Rígido'

    return 'Cavalo Mecânico'
