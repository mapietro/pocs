import pandas as pd
import time
import warnings

# --- IMPORTS DE BASE ---
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma # Tenta o community se o langchain_chroma falhar
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever

# Suprime avisos de depreciação para limpar o output
warnings.filterwarnings("ignore")

# ==============================================================================
# 0. A SOLUÇÃO ARQUITETURAL (Ensemble Local)
# Substituímos o import quebrado por nossa própria classe de fusão.
# ==============================================================================

class SimpleEnsembleRetriever:
    """
    Implementação manual do Ensemble Retriever.
    Usa o algoritmo 'Weighted Reciprocal Rank Fusion' para misturar
    resultados de vetores e palavras-chave.
    """
    def __init__(self, retrievers, weights):
        self.retrievers = retrievers
        self.weights = weights

    def invoke(self, query):
        # 1. Coleta resultados de cada retriever (BM25, Vetor, etc)
        results_by_retriever = []
        for i, retriever in enumerate(self.retrievers):
            try:
                # Tenta chamar invoke (versão nova) ou get_relevant_documents (antiga)
                if hasattr(retriever, "invoke"):
                    docs = retriever.invoke(query)
                else:
                    docs = retriever.get_relevant_documents(query)
                results_by_retriever.append((docs, self.weights[i]))
            except Exception as e:
                print(f"Erro em um dos retrievers: {e}")
                results_by_retriever.append(([], 0))

        # 2. Algoritmo de Fusão (RRF - Reciprocal Rank Fusion)
        # Pontuação = Peso * (1 / (Rank + Constant))
        doc_scores = {}
        doc_map = {}
        
        for docs, weight in results_by_retriever:
            for rank, doc in enumerate(docs):
                # Usamos o conteúdo como ID único para deduplicação
                doc_id = doc.page_content
                doc_map[doc_id] = doc
                
                # O 1º lugar ganha mais pontos que o 2º, ponderado pelo peso do retriever
                score = weight * (1 / (rank + 1))
                
                if doc_id in doc_scores:
                    doc_scores[doc_id] += score
                else:
                    doc_scores[doc_id] = score
        
        # 3. Ordena pelos documentos mais votados e retorna
        sorted_ids = sorted(doc_scores, key=doc_scores.get, reverse=True)
        return [doc_map[id] for id in sorted_ids]

# ==============================================================================
# 1. GOLDEN DATASET & DOCUMENTOS
# ==============================================================================

RAW_TEXT = """
O framework LangGraph permite criar agentes cíclicos com controle de estado.
Diferente do LangChain padrão que é linear (DAG), o LangGraph suporta loops.
A técnica HyDE (Hypothetical Document Embeddings) gera uma resposta falsa para buscar a real.
RAGOps é a prática de aplicar DevOps e observabilidade em pipelines de RAG.
O parâmetro 'k' define quantos documentos são retornados.
O 'Score Threshold' corta documentos com baixa similaridade para evitar alucinações.
A busca Híbrida combina BM25 (palavras-chave) com busca vetorial (semântica).
"""

GOLDEN_DATASET = [
    {"query": "Qual a diferença entre LangGraph e LangChain?", "expected_content": "agentes cíclicos", "id_check": "langgraph"},
    {"query": "O que a técnica HyDE faz?", "expected_content": "resposta falsa", "id_check": "hyde"},
    {"query": "Como evitar alucinações no retrieval?", "expected_content": "Score Threshold", "id_check": "threshold"},
    {"query": "O que é busca mista ou hibrida?", "expected_content": "combina BM25", "id_check": "hybrid"},
]

# ==============================================================================
# 2. FUNÇÕES AUXILIARES
# ==============================================================================

def mock_hyde_generator(query):
    return f"{query} contexto técnico definição explicação detalhada"

def setup_vectorstore(chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = splitter.create_documents([RAW_TEXT])
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # Usa Chroma em memória
    return Chroma.from_documents(docs, embeddings), docs

# ==============================================================================
# 3. O MOTOR DE AVALIAÇÃO
# ==============================================================================

def run_experiment(scenario_name, chunk_size, chunk_overlap, strategy, threshold, k, use_hyde):
    print(f"🧪 Executando Experimento: {scenario_name}...")
    
    # A. Setup
    vectorstore, splits = setup_vectorstore(chunk_size, chunk_overlap)
    
    search_kwargs = {"k": k}
    search_type = "similarity"
    
    if threshold > 0:
        search_type = "similarity_score_threshold"
        search_kwargs["score_threshold"] = threshold

    vector_retriever = vectorstore.as_retriever(search_type=search_type, search_kwargs=search_kwargs)

    # B. Estratégia
    final_retriever = None
    
    if strategy == "hybrid":
        bm25_retriever = BM25Retriever.from_documents(splits)
        bm25_retriever.k = k
        # AQUI USAMOS NOSSA CLASSE MANUAL
        final_retriever = SimpleEnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever], weights=[0.5, 0.5]
        )
    else:
        final_retriever = vector_retriever

    # C. Teste
    hits = 0
    total_score = 0
    
    for case in GOLDEN_DATASET:
        query = case["query"]
        if use_hyde:
            query = mock_hyde_generator(query)
            
        try:
            results = final_retriever.invoke(query)
            
            is_hit = False
            for doc in results:
                if case["expected_content"] in doc.page_content:
                    is_hit = True
                    break
            
            if is_hit:
                hits += 1
                total_score += 1 
                
        except Exception:
            pass

    # D. Limpeza
    vectorstore.delete_collection()
    
    return {
        "Experiment": scenario_name,
        "Strategy": strategy,
        "Collection": f"recursive_{chunk_size}_{chunk_overlap}",
        "Threshold": threshold,
        "Count (k)": k,
        "HyDE": str(use_hyde),
        "Score": round(total_score / len(GOLDEN_DATASET), 2),
        "True Rate": f"{hits}/{len(GOLDEN_DATASET)}"
    }

# ==============================================================================
# 4. EXECUÇÃO
# ==============================================================================

scenarios_to_test = [
    # Cenário 1: Chunks pequenos, busca híbrida (Geralmente o melhor)
    {"name": "recursive_fine_hybrid", "size": 100, "overlap": 20, "strat": "hybrid", "thresh": 0.6, "k": 2, "hyde": False},
    
    # Cenário 2: Chunks pequenos, HyDE ativado (Tenta adivinhar contexto)
    {"name": "token_fine_hyde",       "size": 100, "overlap": 20, "strat": "standard", "thresh": 0.6, "k": 2, "hyde": True},
    
    # Cenário 3: Busca Padrão "Ingênua" (Naive RAG)
    {"name": "semantic_standard",     "size": 100, "overlap": 20, "strat": "standard", "thresh": 0.0, "k": 2, "hyde": False},
    
    # Cenário 4: Chunks Grandes demais (Perde precisão específica)
    {"name": "page_strategy_large",   "size": 500, "overlap": 50, "strat": "standard", "thresh": 0.7, "k": 2, "hyde": False},
    
    # Cenário 5: Threshold muito alto (Causa falha de recuperação/silêncio)
    {"name": "high_threshold_strict", "size": 100, "overlap": 20, "strat": "standard", "thresh": 0.95, "k": 2, "hyde": False},
]

results_data = []

print("🚀 Iniciando Bateria de Testes RAGOps...\n")

for sc in scenarios_to_test:
    res = run_experiment(
        scenario_name=sc["name"],
        chunk_size=sc["size"],
        chunk_overlap=sc["overlap"],
        strategy=sc["strat"],
        threshold=sc["thresh"],
        k=sc["k"],
        use_hyde=sc["hyde"]
    )
    results_data.append(res)

df = pd.DataFrame(results_data)

print("\n\n" + "="*80)
print("COMPARISON OF RETRIEVAL STRATEGIES (OUTPUT SIMULADO)")
print("="*80)
print(df.to_markdown(index=False))
print("="*80)