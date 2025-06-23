# Esse arquivo estão implementadas as ferramentas que serão utilizadas pelo Claude para responder às perguntas dos usuários.
# Essas ferramentas incluem busca de aniversários, previsão de temperatura, férias e formações dos colaboradores
# utilizando dados de um arquivo Excel, banco de dados PostgreSQL e MongoDB.
import pandas as pd
import requests
from pymongo import MongoClient
import psycopg2
import os
from dotenv import load_dotenv

# Carrega variáveis do .env(necessário criar um arquivo .env com as credenciais do banco de dados e chave de API da Anthropic)
load_dotenv()

# Excel
df_excel = pd.read_excel("excel_data.xlsx")
df_excel["birth_date"] = pd.to_datetime(df_excel["birth_date"])

# PostgreSQL
pg_conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "tcc_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASS", "admin"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432")
)

# MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/") # Ajuste o URI se necessário(Rodando localmente no docker)
ferias_col = mongo_client["ferias"]["colaboradores"]

def buscar_aniversario_por_nome(nome: str) -> dict:
    """
    Retorna a data de nascimento e cidade de um colaborador pelo nome completo ou parte do nome, considere o ano 2025.

    Obs:
        O nome do colaborador pode variar (ex: apelidos, erros de digitação ou somente o primeiro nome),
        portanto, tente considerar nomes aproximados ao cruzar com outras tools. 
        Caso venha só o primeiro nome, retorne o primeiro resultado compatível.

    Args:
        nome: Parte do nome ou apelido do colaborador.

    Returns:
        Dicionário com nome, data de nascimento e cidade.
    """
    nome = nome.lower().strip()

    # Garante consistência no dataframe
    df_excel["name"] = df_excel["name"].astype(str).str.lower().str.strip()

    match = df_excel[df_excel["name"].str.contains(nome)]

    if match.empty:
        return {"error": "Nome não encontrado"}

    row = match.iloc[0]
    return {
        "name": row["name"].title(),
        "birth_date": row["birth_date"].strftime("%Y-%m-%d"),
        "city": row["city"]
    }



def temperatura_em_data(cidade: str, data: str) -> dict:
    """
    Retorna a temperatura prevista ou histórica de uma cidade em uma data.

    Entrada:
        cidade: Nome da cidade (pode conter variações).
        data: Data no formato YYYY-MM-DD.

    Saída:
        Dicionário com cidade, data e temperatura.

    Obs:
        Nomes de cidades podem variar, tente considerar aproximações.
    """
    cidade = cidade.strip()

    # 1. Geocodificação
    geo = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": cidade, "format": "json", "limit": 1},
        headers={"User-Agent": "tcc-app"}
    )

    if geo.status_code != 200 or not geo.json():
        return {
            "city": cidade,
            "date": data,
            "temperature": None,
            "error": "Geocoding failed"
        }

    loc = geo.json()[0]
    lat = loc["lat"]
    lon = loc["lon"]

    # 2. Consulta à previsão
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

    if meteo.status_code != 200 or not meteo.json().get("daily", {}).get("temperature_2m_max"):
        return {
            "city": cidade,
            "date": data,
            "temperature": None,
            "error": "Weather API failed or no data found"
        }

    temp = meteo.json()["daily"]["temperature_2m_max"][0]

    return {
        "city": cidade,
        "date": data,
        "temperature": float(temp)
    }


def ferias_por_nome(parcial: str) -> list[dict]:
    """
    Retorna os períodos de férias dos colaboradores com nome aproximado.
    Entrada: parte do nome ou apelido.
    Saída: lista com apelido, início e fim das férias.
    Obs:
        Os nomes dos colaboradores podem variar (ex: apelidos, erros de digitação),
        portanto, tente considerar nomes aproximados ao cruzar com outras tools.
    """
    docs = ferias_col.find({"nickname": {"$regex": parcial, "$options": "i"}})
    return [
        {
            "nickname": d["nickname"],
            "start": d["start"],
            "end": d["end"]
        }
        for d in docs
    ]

def formacoes_por_nome(parcial: str) -> list[dict]:
    """
    Retorna os cursos e treinamentos feitos por um colaborador.
    Entrada: nome ou parte do nome do colaborador.
    Saída: lista com nome, curso, status e datas.
    Obs:
        Os nomes dos colaboradores, cursos podem variar (ex: apelidos, erros de digitação),
        portanto, tente considerar nomes aproximados ao cruzar com outras tools.
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
