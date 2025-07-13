import os
import time
import logging
from dotenv import load_dotenv
from langchain_ollama.llms import OllamaLLM
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from exceptionHandling import *

load_dotenv()
exceptionCoreValue = None
query = None
newQuery = None
result = None

def textToQuery(retry_limit=3, delay_inicial=1):
    global exceptionCoreValue, query, newQuery, result
    newQuery = None
    retry_value = 0
    while retry_value < retry_limit:
        if exceptionCoreValue != None:
            newQuery = redefineQuery(result, exceptionCoreValue)
            print(newQuery)
        try:
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
            Tener en cuenta los siguientes valores como nombres de columnas a las que debes apuntar: "Año - mes","Cód. Cliente","Razón Social","Fecha Emisión Créd.","Tipo Comprob. Créd.","Comprobante Créd.","Tipo Comprob. Déb.","Comprobante Déb.","Fecha Emisión Déb.","Fecha Vto. Créd.","Fecha Vto. Déb.","Importe Créd.","Importe Aplicado","Saldo Créd.","Dias".
            Para cuando la búsqueda sea un rango entre valores, que identifiques como números o fechas, utiliza operadores lógicos.
            Para cuando la búsqueda sea por un valor que reconozcas semánticamente como un sustantivo propio, utiliza 'Like' para estructurar su apartado en la Query.
            El campo "Año - mes" corresponde a una fecha en formato texto con estructura YYYY-MM-DD, respeta eso.
            Recuerda, que el nombre de la columna que detectes, debe estar entre comillas. Ejemplo: "Año - mes".
            Cuando el usuario pregunte por un Cliente, a menos que exprese "Codigo de Cliente" o similar, hace referencia a "Razón Social".
            Considera el uso de LOWER(), para cuando identifiques un sustantivo propio en la Query.
            Pregunta: {input}
            """
            sql_prompt = PromptTemplate(
                input_variables=["input"],
                template=sql_prompt_template
            )

            db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=sql_prompt, verbose=True)
            #print(db.get_usable_table_names())

            if newQuery == None:
                print("----------------------------------")
                query = input("¿Cómo puedo ayudarte? ...  ")

                sql_chain = sql_prompt | llm | StrOutputParser()
                sql_query = sql_chain.invoke({"input": query})

                print("SQL Generada:\n", sql_query)

                result = db.run(sql_query)

                #result = db_chain.run(query)
                with open("output.txt", "w", encoding="utf-8") as f:
                    f.write(result)
                print("----------------------------------")
                print("Resultado obtenido en ./output.txt")
                break
            else:
                sql_chain = sql_prompt | llm | StrOutputParser()
                sql_query = sql_chain.invoke({"input": newQuery})

                result = db.run(sql_query)
                with open("output.txt", "w", encoding="utf-8") as f:
                    f.write(result)
                print("----------------------------------")
                print("Resultado obtenido en ./output.txt")
                break
                
        except Exception as e:
            input("Exception Cycle Initialized...")
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
