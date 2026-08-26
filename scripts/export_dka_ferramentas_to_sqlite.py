"""
Exporter Script: MySQL (dkaferramentas) -> SQLite (dka_ferramentas.db)
Exporta todas as entidades globais e operacionais com esquema unificado (Laravel + Tkinter).
"""
import os
import sys
import sqlite3
import subprocess
import shutil
from datetime import datetime
from typing import List, Dict, Any, Tuple

MYSQL_USER = "antonio2"
MYSQL_PASS = "12312311"
MYSQL_HOST = "127.0.0.1"
MYSQL_DB = "dkaferramentas"

TARGET_DB_PATH = "/home/antonio/cea/dka-tkinter/dka_ferramentas.db"
APP_DB_DIR_PATH = "/home/antonio/cea/dka-tkinter/database/dka_ferramentas.db"

def fetch_mysql_table(table_name: str) -> Tuple[List[str], List[List[Any]]]:
    """Executa query via CLI mysql e retorna colunas + linhas formatadas."""
    cmd = [
        "mysql",
        "-u", MYSQL_USER,
        f"-p{MYSQL_PASS}",
        "-h", MYSQL_HOST,
        MYSQL_DB,
        "-B",
        "-e", f"SELECT * FROM `{table_name}`;"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    lines = res.stdout.splitlines()
    if not lines or not lines[0]:
        return [], []
    
    headers = lines[0].split("\t")
    data_rows = []
    for line in lines[1:]:
        parts = line.split("\t")
        row = []
        for v in parts:
            if v == "NULL":
                row.append(None)
            else:
                row.append(v)
        while len(row) < len(headers):
            row.append(None)
        data_rows.append(row)
        
    return headers, data_rows

def create_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. brands
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS brands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    # 2. vehicle_models
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicle_models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (brand_id) REFERENCES brands(id) ON DELETE CASCADE
    );
    """)

    # 3. trucks (Compatibilidade com Tkinter TruckModel)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trucks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand_code TEXT NOT NULL,
        brand_name TEXT NOT NULL,
        category TEXT DEFAULT 'TRUCK',
        model_name TEXT NOT NULL,
        rim_size TEXT DEFAULT '22',
        axles_count INTEGER DEFAULT 3
    );
    """)

    # 4. vehicle_categories & categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicle_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        default_front_axles INTEGER NOT NULL DEFAULT 1,
        default_rear_axles INTEGER NOT NULL DEFAULT 1,
        is_truck INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        default_front_axles INTEGER NOT NULL DEFAULT 1,
        default_rear_axles INTEGER NOT NULL DEFAULT 1,
        is_truck INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    # 5. vehicles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_model_id INTEGER NOT NULL,
        vehicle_category_id INTEGER,
        year_start INTEGER NOT NULL,
        year_end INTEGER,
        version TEXT,
        drive_type TEXT,
        created_at TEXT,
        updated_at TEXT,
        deleted_at TEXT,
        FOREIGN KEY (vehicle_model_id) REFERENCES vehicle_models(id) ON DELETE CASCADE,
        FOREIGN KEY (vehicle_category_id) REFERENCES vehicle_categories(id) ON DELETE SET NULL
    );
    """)

    # 6. vehicle_axle_specs & axle_specs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vehicle_axle_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        axle_number INTEGER NOT NULL,
        axle_type TEXT NOT NULL,
        camber_min REAL,
        camber_nominal REAL,
        camber_max REAL,
        caster_min REAL,
        caster_nominal REAL,
        caster_max REAL,
        toe_min REAL,
        toe_nominal REAL,
        toe_max REAL,
        kpi_min REAL,
        kpi_nominal REAL,
        kpi_max REAL,
        track REAL,
        ride_height REAL,
        reference_rim REAL,
        measure_unit TEXT NOT NULL DEFAULT 'degrees',
        suspension_type TEXT NOT NULL DEFAULT 'mechanical',
        version INTEGER NOT NULL DEFAULT 1,
        is_current INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE,
        UNIQUE(vehicle_id, axle_number, version)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS axle_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id INTEGER NOT NULL,
        axle_number INTEGER NOT NULL,
        axle_type TEXT NOT NULL,
        camber_min REAL,
        camber_nominal REAL,
        camber_max REAL,
        caster_min REAL,
        caster_nominal REAL,
        caster_max REAL,
        toe_min REAL,
        toe_nominal REAL,
        toe_max REAL,
        kpi_min REAL,
        kpi_nominal REAL,
        kpi_max REAL,
        track REAL,
        ride_height REAL,
        reference_rim REAL,
        measure_unit TEXT NOT NULL DEFAULT 'degrees',
        suspension_type TEXT NOT NULL DEFAULT 'mechanical',
        version INTEGER NOT NULL DEFAULT 1,
        is_current INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE
    );
    """)

    # 7. companies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cnpj TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT,
        deleted_at TEXT
    );
    """)

    # 8. roles & users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT,
        description TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        email_verified_at TEXT,
        password TEXT NOT NULL,
        two_factor_secret TEXT,
        two_factor_recovery_codes TEXT,
        two_factor_confirmed_at TEXT,
        remember_token TEXT,
        created_at TEXT,
        updated_at TEXT,
        role_id INTEGER,
        FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE SET NULL
    );
    """)

    # 9. clients (Esquema Unificado Laravel + Tkinter)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL DEFAULT 1,
        name TEXT NOT NULL,
        document TEXT NOT NULL,
        nome TEXT,
        cpf_cnpj TEXT,
        email TEXT,
        phone TEXT,
        mobile TEXT,
        celular TEXT,
        telefone_fixo TEXT,
        address TEXT,
        logradouro TEXT,
        address_number TEXT,
        numero TEXT,
        address_complement TEXT,
        complemento TEXT,
        neighborhood TEXT,
        bairro TEXT,
        city TEXT,
        cidade TEXT,
        state TEXT,
        uf TEXT DEFAULT 'SP',
        zip_code TEXT,
        cep TEXT,
        notes TEXT,
        observacoes TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        ativo INTEGER NOT NULL DEFAULT 1,
        date_service TEXT,
        created_at TEXT,
        updated_at TEXT,
        deleted_at TEXT,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
    );
    """)

    # 10. physical_units
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS physical_units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        vehicle_id INTEGER,
        license_plate TEXT NOT NULL,
        chassis_number TEXT,
        mileage INTEGER NOT NULL DEFAULT 0,
        unit_type TEXT NOT NULL DEFAULT 'truck_tractor',
        created_at TEXT,
        updated_at TEXT,
        deleted_at TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL
    );
    """)

    # 11. attendances (Esquema Unificado Laravel + Tkinter)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL DEFAULT 1,
        client_id INTEGER NOT NULL DEFAULT 1,
        technician_id INTEGER,
        started_by INTEGER,
        finalized_by INTEGER,
        cancelled_by INTEGER,
        license_plate TEXT,
        mileage TEXT,
        observations TEXT,
        pdf_path TEXT,
        name TEXT,
        status TEXT NOT NULL DEFAULT 'draft',
        date_formatted TEXT,
        date_iso TEXT,
        model TEXT,
        plate TEXT,
        client TEXT,
        pdf_url TEXT,
        created_at TEXT,
        updated_at TEXT,
        deleted_at TEXT,
        FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
        FOREIGN KEY (technician_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (started_by) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (finalized_by) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (cancelled_by) REFERENCES users(id) ON DELETE SET NULL
    );
    """)

    # 12. attendance_compositions & attendance_units
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_compositions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attendance_id INTEGER NOT NULL,
        physical_unit_id INTEGER NOT NULL,
        acouplement_order INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (attendance_id) REFERENCES attendances(id) ON DELETE CASCADE,
        FOREIGN KEY (physical_unit_id) REFERENCES physical_units(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_units (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attendance_id INTEGER NOT NULL,
        physical_unit_id INTEGER NOT NULL,
        acouplement_order INTEGER NOT NULL DEFAULT 1,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (attendance_id) REFERENCES attendances(id) ON DELETE CASCADE,
        FOREIGN KEY (physical_unit_id) REFERENCES physical_units(id) ON DELETE CASCADE
    );
    """)

    # 13. attendance_measurements & attendance_readings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attendance_id INTEGER NOT NULL,
        physical_unit_id INTEGER NOT NULL,
        axle_number INTEGER NOT NULL,
        axle_type TEXT NOT NULL,
        measurements TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (attendance_id) REFERENCES attendances(id) ON DELETE CASCADE,
        FOREIGN KEY (physical_unit_id) REFERENCES physical_units(id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        attendance_id INTEGER NOT NULL,
        physical_unit_id INTEGER NOT NULL,
        axle_number INTEGER NOT NULL,
        axle_type TEXT NOT NULL,
        measurements TEXT NOT NULL,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY (attendance_id) REFERENCES attendances(id) ON DELETE CASCADE,
        FOREIGN KEY (physical_unit_id) REFERENCES physical_units(id) ON DELETE CASCADE
    );
    """)

    conn.commit()

def populate_table(conn: sqlite3.Connection, table_name: str, alias_names: List[str] = None):
    print(f"--> Exportando tabela '{table_name}'...")
    headers, rows = fetch_mysql_table(table_name)
    if not headers or not rows:
        print(f"    Sem registros em '{table_name}'.")
        return

    placeholders = ", ".join(["?"] * len(headers))
    cols_str = ", ".join([f"`{h}`" for h in headers])
    sql = f"INSERT OR REPLACE INTO `{table_name}` ({cols_str}) VALUES ({placeholders});"

    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF;")

    conn.executemany(sql, rows)
    conn.commit()
    print(f"    Inseridos {len(rows)} registros em '{table_name}'.")

    if alias_names:
        for alias in alias_names:
            alias_sql = f"INSERT OR REPLACE INTO `{alias}` ({cols_str}) VALUES ({placeholders});"
            conn.executemany(alias_sql, rows)
            conn.commit()
            print(f"    Inseridos {len(rows)} registros na alias '{alias}'.")

    cursor.execute("PRAGMA foreign_keys = ON;")

def sync_bridge_columns(conn: sqlite3.Connection):
    print("--> Sincronizando colunas cruzadas (Laravel <-> Tkinter) em 'clients' e 'attendances'...")
    cursor = conn.cursor()

    # 1. Sincronizar clientes (nome, cpf_cnpj, cidade, uf, etc.)
    cursor.execute("""
    UPDATE clients
    SET 
        nome = COALESCE(name, 'Cliente'),
        cpf_cnpj = COALESCE(document, '000.000.000-00'),
        celular = COALESCE(mobile, phone, ''),
        telefone_fixo = COALESCE(phone, ''),
        logradouro = COALESCE(address, ''),
        numero = COALESCE(address_number, ''),
        complemento = COALESCE(address_complement, ''),
        bairro = COALESCE(neighborhood, ''),
        cidade = COALESCE(city, 'São Paulo'),
        uf = COALESCE(state, 'SP'),
        observacoes = COALESCE(notes, ''),
        ativo = COALESCE(is_active, 1),
        date_service = COALESCE(SUBSTR(created_at, 1, 10), '18/08/2026')
    WHERE nome IS NULL OR nome = '';
    """)

    # 2. Sincronizar attendances (date_formatted, date_iso, model, plate, client, pdf_url)
    cursor.execute("""
    UPDATE attendances
    SET
        date_formatted = COALESCE(SUBSTR(created_at, 1, 16), '18/08/2026 14:00'),
        date_iso = COALESCE(SUBSTR(created_at, 1, 10), '2026-08-18'),
        model = COALESCE(name, 'Volvo FH 540'),
        plate = COALESCE(license_plate, 'ABC-1D23'),
        client = (SELECT COALESCE(c.nome, c.name, 'Cliente') FROM clients c WHERE c.id = attendances.client_id),
        pdf_url = COALESCE(pdf_path, '')
    WHERE plate IS NULL OR plate = '';
    """)

    conn.commit()
    print("    Colunas sincronizadas com sucesso.")

def populate_trucks_table(conn: sqlite3.Connection):
    print("--> Sincronizando tabela 'trucks' a partir dos modelos de veículos exportados...")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO trucks (id, brand_code, brand_name, category, model_name, rim_size, axles_count)
    SELECT 
        vm.id AS id,
        b.slug AS brand_code,
        b.name AS brand_name,
        'TRUCK' AS category,
        vm.name AS model_name,
        '22' AS rim_size,
        3 AS axles_count
    FROM vehicle_models vm
    JOIN brands b ON b.id = vm.brand_id;
    """)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM trucks;")
    cnt = cursor.fetchone()[0]
    print(f"    Sincronizados {cnt} registros na tabela 'trucks'.")

def main():
    if os.path.exists(TARGET_DB_PATH):
        os.remove(TARGET_DB_PATH)

    os.makedirs(os.path.dirname(APP_DB_DIR_PATH), exist_ok=True)

    print("Conectando ao banco SQLite target:", TARGET_DB_PATH)
    conn = sqlite3.connect(TARGET_DB_PATH)

    print("Criando schema no SQLite...")
    create_schema(conn)

    tables_to_migrate = [
        ("brands", []),
        ("vehicle_models", []),
        ("vehicle_categories", ["categories"]),
        ("vehicles", []),
        ("vehicle_axle_specs", ["axle_specs"]),
        ("companies", []),
        ("roles", []),
        ("users", []),
        ("clients", []),
        ("physical_units", []),
        ("attendances", []),
        ("attendance_compositions", ["attendance_units"]),
        ("attendance_measurements", ["attendance_readings"])
    ]

    for tbl, aliases in tables_to_migrate:
        populate_table(conn, tbl, aliases)

    populate_trucks_table(conn)
    sync_bridge_columns(conn)

    print("\n==========================================")
    print("VALIDAÇÃO E CONTAGEM DE REGISTROS (COUNT)")
    print("==========================================")

    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    validation_tables = [
        "brands",
        "vehicle_models",
        "trucks",
        "vehicles",
        "vehicle_axle_specs",
        "axle_specs",
        "vehicle_categories",
        "categories",
        "companies",
        "roles",
        "users",
        "clients",
        "physical_units",
        "attendances",
        "attendance_compositions",
        "attendance_units",
        "attendance_measurements",
        "attendance_readings"
    ]

    for v_tbl in validation_tables:
        cursor.execute(f"SELECT COUNT(*) FROM `{v_tbl}`;")
        cnt = cursor.fetchone()[0]
        print(f"  Tabela '{v_tbl}': {cnt} registros")

    shutil.copy2(TARGET_DB_PATH, APP_DB_DIR_PATH)
    print(f"\nBanco de dados copiado para: {APP_DB_DIR_PATH}")
    print("Migração concluída com 100% de sucesso!")

    conn.close()

if __name__ == "__main__":
    main()
