# Esse arquivo contém a aplicação Streamlit que utiliza o Claude como LLM para responder perguntas sobre colaboradores.
# As ferramentas implementadas no arquivo `tools.py` são utilizadas para buscar aniversários, temperaturas, férias e formações dos colaboradores.
# A aplicação é simples, com um campo de entrada de texto para perguntas e um botão para enviar a consulta ao agente Claude.
# Rode com Python para iniciar a aplicação: `streamlit run app.py`
# Certifique-se das instalações necessárias: `pip install streamlit langchain langchain-anthropic python-dotenv pymongo pandas psycopg2-binary` e as outras dependências do projeto.
import streamlit as st
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent_types import AgentType
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
import os
import json
import inspect
import tools

# Carrega variáveis de ambiente (.env)
load_dotenv()

# Função robusta para interpretar entradas do LLM
def handle_input(x, func):
    try:
        parsed = json.loads(x)
        if isinstance(parsed, dict):
            return json.dumps(func(**parsed))
        elif isinstance(parsed, list):
            return json.dumps(func(*parsed))
    except Exception:
        pass
    args = [arg.strip() for arg in x.split(",")]
    return json.dumps(func(*args))

# Monta tools com docstrings e entrada flexível
def build_tool(name, func):
    return Tool(
        name=name,
        func=lambda x: handle_input(x, func),
        description=inspect.getdoc(func)
    )

# Lista de tools
tool_list = [
    build_tool("buscar_aniversario_por_nome", tools.buscar_aniversario_por_nome),
    build_tool("temperatura_em_data", tools.temperatura_em_data),
    build_tool("ferias_por_nome", tools.ferias_por_nome),
    build_tool("formacoes_por_nome", tools.formacoes_por_nome),
]

# Claude como LLM via LangChain
llm = ChatAnthropic(
    model="claude-opus-4-20250514",
    temperature=0,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Agente com raciocínio por descrição (sem function calling)
agent = initialize_agent(
    tool_list,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Interface Streamlit
st.title("🤖 Assistente de Colaboradores (Claude)")

query = st.text_input("Digite sua pergunta em linguagem natural")

if st.button("Responder") and query:
    with st.spinner("Consultando..."):
        resposta = agent.run(query)
        st.success(resposta)
