import os
import time
import logging
from dotenv import load_dotenv
from langchain_ollama.llms import OllamaLLM
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
from exceptionHandling import *

load_dotenv()
exceptionCoreValue = None
query = None
newQuery = None
result = None

def textToQuery(retry_limit=3, delay_inicial=1):
    global exceptionCoreValue, query, newQuery, result
    retry_value = 0
    input("...")
    while retry_value < retry_limit:
        input("...")
        if exceptionCoreValue != None:
            newQuery = redefineQuery(result, exceptionCoreValue)
            print(newQuery)
        try:
            input("...")
            # Crear instancia del modelo llama 3.2 (ajustá el nombre si usás otro)
            llm = OllamaLLM(model="gemma3n", temperature=0)

            # Conectar a la base SQLite
            sqlite_path = os.getenv("SQLPATH")
            db = SQLDatabase.from_uri(f"sqlite:///{sqlite_path}")
            print("Database conectada correctamente")

            # Crear chain SQL
            # Prompt personalizado para que el LLM devuelva solo la consulta SQL limpia, sin backticks ni formato Markdown
            sql_prompt_template = """
            Eres un asistente que traduce lenguaje natural a SQL.
            Responde SOLO con la consulta SQL sin ningún formato de código ni backticks.
            Siempre debes apuntar a la tabla 'csv_table'.
            Para la columna, a menos que sea indicado, **evita generar signos, respeta el nombre tal cuál es**.
            Pregunta: {input}
            SQLQuery:
            """

            sql_prompt = PromptTemplate(
                input_variables=["input"],
                template=sql_prompt_template
            )

            db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=sql_prompt, verbose=True)
            print(db.get_usable_table_names())

            # Crear chain SQL
            #db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
            #print(db_chain)

            # Pregunta en lenguaje natural
            if newQuery == None:
                query = "¿Cuántos clientes con Razón Social: Banco de la Ciudad de Buenos Aires hay?"
                result = db_chain.run(query)
                input("...")
                print(result)
            else:
                result = db_chain.run(newQuery)
                input("...")
                print(result)
                
        except Exception as e:
            input("...")
            retry_value += 1
            logging.warning(f"Excepción capturada. {e}.")
            if retry_value == retry_limit:
                logging.error("Se agotaron los intentos, propagando excepción")
                raise  # Propagar la excepción después de agotar los reintentos
            else:
                # Esperar antes de reintentar (backoff exponencial)
                exceptionCoreValue = extractExceptionValue(e)
                input("...")
                if exceptionCoreValue != "":
                    logging.warning(f"Valor principal de excepción obtenido: {exceptionCoreValue}")
                    exceptionCoreValue = removeTrashValues(exceptionCoreValue)
                    time.sleep(delay_inicial)
                else:
                    logging.error("No se pudo obtener valor principal de la excepción.")
                    raise

    return exceptionCoreValue, query
