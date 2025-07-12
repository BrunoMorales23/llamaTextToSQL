from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def extractExceptionValue(exception_reason):

    llm = OllamaLLM(model="gemma3n", temperature=0)

    exception_value = exception_reason

    # Definir prompt para que responda solo con la palabra que causa la excepción
    prompt_template = """
    Eres un asistente que obtiene motivos de excepciones.
    Responde SOLO con la palabra que está causando la excepción.
    Texto de excepción: {exception_text}
    """

    prompt = PromptTemplate(input_variables=["exception_text"], template=prompt_template)

    # Crear chain con el LLM y el prompt
    chain = LLMChain(llm=llm, prompt=prompt)

    # Ejecutar chain con el texto de la excepción
    result = chain.run(exception_text=exception_value)

    print(result)
    exceptionMainValue = result
    return exceptionMainValue

def removeTrashValues(core_value):

    llm = OllamaLLM(model="gemma3n", temperature=0)

    prompt_template = """
    Eres un asistente que elimina caracteres incorrectos.
    Responde SOLO con la palabra que recibida, pero sin caracteres extra de tipo "/", ".", ",", "@", "-", "_".
    En caso de que entre las palabras, existiera uno de estos tipos de caracter, debes reemplazarlo por un espacio. Ejemplo: "Prueba_Test" -> "Prueba Test".
    Respeta signos de puntuación y acentos.
    Valor a reemplazar: {exception_value}
    """

    prompt = PromptTemplate(input_variables=["exception_value"], template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(exception_value=core_value)

    print(result)
    newCoreWord = result
    return newCoreWord

def redefineQuery(query, core_value):

    llm = OllamaLLM(model="gemma3n", temperature=0)

    prompt_template = """
    Eres un asistente que refactoriza preguntas.
    Dada una pregunta original, identifica y reemplaza dentro de ella el valor que más se asemeje a "{core_value}" por el valor exacto.
    Reemplaza solo una coincidencia, respeta los signos de puntuación y acentos, y responde **únicamente con la pregunta modificada**, sin explicaciones ni ejemplos.
    Pregunta original: {query}
    """

    prompt = PromptTemplate(input_variables=["query", "core_value"], template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(query=query, core_value=core_value)

    print(result)
    newQuery = result
    return newQuery