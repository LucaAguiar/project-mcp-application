# Esse script implementa um servidor MCP com várias ferramentas para gerenciar informações de colaboradores, como aniversários, temperaturas, férias e formações.
# Ele é utilizado apenas com a interface nativa do Claude, sem integração com Streamlit ou outros front-ends.
# Foi um teste do protocolo MCP para ver como funcionaria com o Claude, mas não foi utilizado na versão final do projeto.
import os
import pandas as pd
import psycopg2
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Carrega variáveis do .env(necessário criar um arquivo .env com as credenciais do banco de dados)
load_dotenv()

# === Conexões ===

# PostgreSQL
pg_conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
pg_conn.autocommit = True

# MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/") # Ajuste o URI se necessário(Rodando localmente no docker)
mongo_db = mongo_client["ferias"]
ferias_col = mongo_db["colaboradores"]

# Excel
df_excel = pd.read_excel("C:\\Users\\lucac\\Desktop\\TCC - 2\\excel_data.xlsx") # Necessário ajustar o caminho do arquivo
df_excel["birth_date"] = pd.to_datetime(df_excel["birth_date"])

# MCP Server
mcp = FastMCP("TCCMCPServer")

# === Tool 1: Aniversariantes do mês ===
@mcp.tool()
def aniversariantes_mes(mes: int) -> list[dict]:
    """
    Retorna os colaboradores que fazem aniversário em um determinado mês.

    Args:
        mes: Número do mês (1 a 12).

    Returns:
        Lista de dicionários com nome, data de nascimento e cidade.
    """
    df_filtrado = df_excel[df_excel["birth_date"].dt.month == mes]
    return [
        {
            "name": row["name"],
            "birth_date": row["birth_date"].strftime("%Y-%m-%d"),
            "city": row["city"]
        }
        for _, row in df_filtrado.iterrows()
    ]

# === Tool 2: Temperatura por cidade e data (com previsão) ===
@mcp.tool()
def temperatura_em_data(cidade: str, data: str) -> dict:
    """
    Retorna a temperatura prevista ou histórica para uma cidade em uma data.

    Args:
        cidade: Nome da cidade.
        data: Data no formato YYYY-MM-DD.

    Returns:
        Dicionário com cidade, data e temperatura.
    """
    geo = requests.get(
        f"https://nominatim.openstreetmap.org/search",
        params={"q": cidade, "format": "json", "limit": 1},
        headers={"User-Agent": "mcp-tcc-app"}
    )
    if geo.status_code != 200 or not geo.json():
        return {"city": cidade, "date": data, "temperature": None, "error": "Geocoding failed"}

    loc = geo.json()[0]
    lat = loc["lat"]
    lon = loc["lon"]

    meteo = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max",
            "timezone": "America/Sao_Paulo",
            "start_date": data,
            "end_date": data
        }
    )
    if meteo.status_code != 200:
        return {"city": cidade, "date": data, "temperature": None, "error": "Weather API failed"}

    try:
        temp = meteo.json()["daily"]["temperature_2m_max"][0]
        return {
            "city": cidade,
            "date": data,
            "temperature": float(temp)
        }
    except Exception:
        return {
            "city": cidade,
            "date": data,
            "temperature": None
        }

# === Tool 3: Buscar férias por nome aproximado ===
@mcp.tool()
def ferias_por_nome(parcial: str) -> list[dict]:
    """
    Retorna os períodos de férias de colaboradores com nomes que contenham o texto fornecido.

    Args:
        parcial: Parte do nome ou apelido do colaborador.

    Returns:
        Lista de dicionários com apelido, data de início e fim das férias.
    """
    docs = ferias_col.find({"nickname": {"$regex": parcial, "$options": "i"}})
    return [
        {
            "nickname": doc["nickname"],
            "start": doc["start"],
            "end": doc["end"]
        }
        for doc in docs
    ]

# === Tool 4: Formações, cursos e certificações ===
@mcp.tool()
def formacoes_por_nome(parcial: str) -> list[dict]:
    """
    Retorna os cursos e treinamentos de um colaborador pelo nome.

    Args:
        parcial: Nome ou parte do nome do colaborador.

    Returns:
        Lista de dicionários com nome, curso, status e datas de início/fim.
    """
    cur = pg_conn.cursor()
    cur.execute(
        "SELECT nome, curso, status, data_inicio, data_fim FROM formacoes WHERE nome ILIKE %s ORDER BY data_fim DESC;",
        (f"%{parcial}%",)
    )
    rows = cur.fetchall()
    return [
        {
            "name": r[0],
            "course": r[1],
            "status": r[2],
            "start": r[3].strftime("%Y-%m-%d"),
            "end": r[4].strftime("%Y-%m-%d") if r[4] else None
        }
        for r in rows
    ]

# === Rodar o servidor ===
if __name__ == "__main__":
    mcp.run()
