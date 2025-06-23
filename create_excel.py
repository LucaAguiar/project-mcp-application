# Esse script cria um arquivo Excel com dados fictícios de colaboradores, incluindo nome, data de nascimento e cidade.
# Rode com Python para gerar o arquivo "excel_data.xlsx". Comando: Python create_excel.py
import pandas as pd

df = pd.DataFrame({
    "id": [1, 2, 3, 4, 5, 6],
    "name": [
        "Alice Wonderland",
        "Bob The Builder",
        "Charlie Chaplin",
        "João da Silva",
        "João Pedro Oliveira",
        "Carlos Eduardo"
    ],
    "birth_date": [
        "1990-05-10",
        "1990-05-15",
        "1990-05-20",
        "1985-07-12",
        "1992-03-22",
        "1988-11-03"
    ],
    "city": [
        "Curitiba",
        "São Paulo",
        "Florianópolis",
        "Londrina",
        "Cascavel",
        "Porto Alegre"
    ]
})


# Salvar como Excel
df.to_excel("excel_data.xlsx", index=False)
print("Arquivo criado com sucesso.")
