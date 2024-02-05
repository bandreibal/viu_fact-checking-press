from langchain_openai import ChatOpenAI
from langchain.llms import Cohere
import os
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

def get_clean_source(full_path):
    import re
    pattern = re.compile(r'\\([^\\]+)\.txt$')

    return pattern.search(full_path).group(1)

def create_context(query, vectorstore, news):
    from collections import defaultdict
    docs = []

    for n in ['abc', 'elplural', 'elmundo', 'okdiario']:
        docs = docs + (vectorstore.similarity_search_with_score(query, 4, filter=dict(source=f'data\\sources_txt\\{n}.txt')))

    grouped_texts = defaultdict(str)

    for doc in docs:
        source = doc[0].metadata.get('source')
        grouped_texts[source] += doc[0].page_content + ' '

    result_dict = dict(grouped_texts)
    rel_sources = [get_clean_source(n) for n in result_dict.keys()]


    resultado = "Las siguientes fuentes no contienen información al respecto: " + ", ".join([n for n in ['abc', 'elplural', 'elmundo', 'okdiario'] if n not in rel_sources])+ \
    """\n\nLas siguientes fuentes sí contienen información: 
    """ + '\n'.join([f"{get_clean_source(source)}: {content} \n\n" for source, content in result_dict.items()])

    return resultado

def consulta(q, vectorstore, model="gpt-3.5-turbo-0125", news=['abc', 'elplural', 'elmundo', 'okdiario']):
    from prompts.prompts import template_solojustificacion
    from prompts.prompts import template_clasificacion

    contexto = create_context(q, vectorstore, news)

    print(model)

    if model == 'cohere':
        llm=Cohere(model="command", temperature=0)

        response = llm.invoke(f"La afirmación es: {q}" + template_solojustificacion + contexto)
        # display(response['context'])
        # Markdown(response['answer'])
        response2 = llm.invoke(template_clasificacion + response)
        return response2, contexto

    else:
        llm = ChatOpenAI(model_name=model, # gpt-4-0125-preview gpt-3.5-turbo-0125
                    temperature=0,
                    openai_api_key=OPENAI_API_KEY)

        response = llm.invoke(f"La afirmación es: {q}" + template_solojustificacion + contexto)
        # display(response['context'])
        # Markdown(response['answer'])
        response2 = llm.invoke(template_clasificacion + response.content)
        return response2.content, contexto