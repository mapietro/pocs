import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.retrievers import BM25Retriever
from rag_evaluator_core import UniversalRAGEvaluator, TestCase

# ==============================================================================
# 1. CLASSES UTILITÁRIAS (WRAPPER E HYBRID)
# ==============================================================================

class SimpleEnsembleRetriever:
    """Implementação manual de Busca Híbrida (Vetor + Keyword)"""
    def __init__(self, retrievers, weights):
        self.retrievers = retrievers
        self.weights = weights

    def invoke(self, query):
        doc_scores = {}
        doc_map = {}
        
        for i, retriever in enumerate(self.retrievers):
            try:
                # Compatibilidade invoke/get_relevant
                docs = retriever.invoke(query) if hasattr(retriever, "invoke") else retriever.get_relevant_documents(query)
                weight = self.weights[i]
                
                for rank, doc in enumerate(docs):
                    # Usa o conteúdo como ID para deduplicar
                    key = doc.page_content[:100] 
                    doc_map[key] = doc
                    # Algoritmo RRF (Reciprocal Rank Fusion) simplificado
                    score = weight * (1 / (rank + 1))
                    doc_scores[key] = doc_scores.get(key, 0) + score
            except Exception:
                pass
        
        # Ordena e retorna
        sorted_keys = sorted(doc_scores, key=doc_scores.get, reverse=True)
        return [doc_map[k] for k in sorted_keys]

class HydeRetrieverWrapper:
    """Adiciona camada de HyDE (Alucinação controlada) antes da busca"""
    def __init__(self, base_retriever):
        self.base_retriever = base_retriever
    
    def invoke(self, query):
        # MOCK HYDE: Simula a geração de um documento hipotético para não gastar API do GPT-4o no teste
        # Na vida real: hypothetical_doc = llm.invoke(f"Escreva um artigo sobre: {query}")
        hypothetical_doc = f"{query} performance stock market high growth analysis report 2024"
        return self.base_retriever.invoke(hypothetical_doc)

# ==============================================================================
# 2. CARGA DE DADOS
# ==============================================================================

print("📂 Carregando PDF Stock Market...")
loader = PyPDFLoader("Stock_Market_Performance_2024.pdf")
raw_docs = loader.load()
FULL_TEXT = "\n\n".join([d.page_content for d in raw_docs])

# GABARITO (Extraído do PDF)
gabarito = [
    TestCase(query="Qual o retorno do S&P 500?", expected_id="25%"), # [cite: 4]
    TestCase(query="Quais empresas são as Magnificent 7?", expected_id="Apple, Microsoft"), # [cite: 10]
    TestCase(query="Quanto a Palantir (PLTR) subiu?", expected_id="340%"), # 
    TestCase(query="Performance da Tesla vs Lucro", expected_id="fell by over 50%"), # 
]

# ==============================================================================
# 3. A FÁBRICA SUPER PODEROSA (Lida com todas as variáveis)
# ==============================================================================

def factory_rag_ultimate(config):
    
    # A. CHUNKING
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config['chunk_size'], chunk_overlap=config.get('overlap', 100)
    )
    splits = splitter.create_documents([FULL_TEXT])
    
    # B. VECTOR STORE (Transient/Memory)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    # Collection name único para evitar colisão entre testes
    unique_name = f"test_{config['chunk_size']}_{config.get('threshold', 0)}_{config.get('strategy', 'std')}"
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, collection_name=unique_name)
    
    # C. BASE RETRIEVER (Com ou sem Threshold)
    search_kwargs = {"k": config['k']}
    search_type = "similarity"
    
    if config.get('threshold', 0) > 0:
        search_type = "similarity_score_threshold"
        search_kwargs["score_threshold"] = config['threshold']
        
    vector_retriever = vectorstore.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
    
    # D. ESTRATÉGIA (Standard vs Hybrid)
    final_retriever = vector_retriever
    
    if config.get('strategy') == 'hybrid':
        bm25_retriever = BM25Retriever.from_documents(splits)
        bm25_retriever.k = config['k']
        final_retriever = SimpleEnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever], 
            weights=[0.4, 0.6] # 40% Keyword, 60% Vector
        )
        
    # E. HYDE (Camada final)
    if config.get('hyde') is True:
        final_retriever = HydeRetrieverWrapper(final_retriever)
        
    return final_retriever

# ==============================================================================
# 4. EXECUÇÃO DO GRID SEARCH
# ==============================================================================

print("🚀 Iniciando Teste Multidimensional...")
evaluator = UniversalRAGEvaluator(gabarito)

# AQUI ESTÃO TODAS AS VARIÁVEIS QUE VOCÊ QUERIA TESTAR
parametros = {
    "chunk_size": [500, 1000],          # Tamanho do corte
    "k": [3],                           # Quantos docs trazer
    "threshold": [0.0, 0.75],           # Nota de corte (Rigor)
    "strategy": ["standard", "hybrid"], # Vetor puro vs Híbrido
    "hyde": [False, True]               # Busca direta vs Alucinada
}

# Isso vai gerar 2 x 1 x 2 x 2 x 2 = 16 Cenários diferentes!
df_results = evaluator.run_grid_search(factory_rag_ultimate, parametros)

# Exibe formatado
if hasattr(evaluator, 'print_report'):
    evaluator.print_report(df_results)
else:
    print(df_results.to_markdown())