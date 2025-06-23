# Esse script conecta ao MongoDB local e insere dados de colaboradores com nomes abreviados.
# Rode com Python para popular a coleção "colaboradores" no banco de dados "ferias". Comando: Python load_mongo.py
# Certifique-se de que o MongoDB esteja rodando localmente na porta padrão (27017).
from pymongo import MongoClient

# Conexão com MongoDB local
client = MongoClient("mongodb://localhost:27017/")
db = client["ferias"]
collection = db["colaboradores"]

# Apaga tudo antes de inserir
collection.delete_many({})

# Insere dados com nomes abreviados
collection.insert_many([
    {"nickname": "A. Wonderland", "start": "2025-07-01", "end": "2025-07-15"},
    {"nickname": "B. Builder", "start": "2025-06-15", "end": "2025-06-30"},
    {"nickname": "C. Chaplin", "start": "2025-08-01", "end": "2025-08-15"},
    {"nickname": "J. da Silva", "start": "2025-07-20", "end": "2025-08-05"},
    {"nickname": "João P. Oliveira", "start": "2025-12-01", "end": "2025-12-15"},
    {"nickname": "Joãozinho", "start": "2025-01-10", "end": "2025-01-25"},
    {"nickname": "Carlos E.", "start": "2025-09-05", "end": "2025-09-20"},
    {"nickname": "Maria F.", "start": "2025-04-01", "end": "2025-04-15"}
])


print("Dados inseridos.")
