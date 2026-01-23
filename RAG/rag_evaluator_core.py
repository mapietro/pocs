import time
import pandas as pd
import itertools
from dataclasses import dataclass
from typing import List, Dict, Any, Callable, Optional
from tqdm import tqdm # Para barra de progresso visual

# --- 1. Estruturas de Dados ---

@dataclass
class TestCase:
    query: str
    expected_id: str  # ID ou trecho único que identifica o documento correto
    metadata_filters: Optional[Dict] = None

@dataclass
class EvaluationResult:
    config: Dict[str, Any]
    hit_rate: float
    mrr: float
    avg_latency: float
    raw_data: List[Dict]

# --- 2. A Classe Utilitária "Fodona" ---

class UniversalRAGEvaluator:
    def __init__(self, golden_dataset: List[TestCase]):
        """
        :param golden_dataset: Lista de perguntas e respostas esperadas (Gabarito).
        """
        self.dataset = golden_dataset

    def _calculate_metrics(self, retrieved_docs: List[Any], expected_id: str):
        """Calcula métricas para uma única query."""
        hit = False
        rank = 0
        
        # Tenta extrair conteúdo ou ID dependendo do objeto retornado
        # Isso torna a classe agnóstica a LangChain, LlamaIndex ou Custom
        for i, doc in enumerate(retrieved_docs):
            # Normalização: se for objeto do Langchain pega page_content, senão string
            content = getattr(doc, "page_content", str(doc))
            meta = getattr(doc, "metadata", {})
            doc_id = meta.get("id", "")
            
            # Verifica se é o doc certo (pelo ID ou contendo o texto esperado)
            if expected_id in doc_id or expected_id in content:
                hit = True
                rank = i + 1
                break
        
        reciprocal_rank = 1.0 / rank if hit else 0.0
        return hit, reciprocal_rank

    def run_grid_search(self, rag_factory: Callable[[Dict], Any], param_grid: Dict[str, List[Any]]):
        """
        Testa TODAS as combinações de variáveis possíveis.
        
        :param rag_factory: Uma função que recebe um dict de config e retorna o objeto Retriever (com método .invoke ou .get_relevant_documents)
        :param param_grid: Dicionário com as variaveis. Ex: {'k': [2, 5], 'chunk_size': [100, 500]}
        """
        # 1. Gera todas as combinações (Produto Cartesiano)
        keys, values = zip(*param_grid.items())
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        results_summary = []
        
        print(f"🚀 Iniciando Grid Search com {len(combinations)} cenários...")
        
        # Barra de progresso para acompanhar os testes
        for config in tqdm(combinations, desc="Avaliando Cenários"):
            
            # A. Setup do RAG para este cenário específico (Injeção de Dependência)
            # Aqui é onde a mágica acontece: o factory recria o RAG com os novos parâmetros
            try:
                retriever_instance = rag_factory(config)
            except Exception as e:
                print(f"❌ Erro ao criar RAG com config {config}: {e}")
                continue

            # B. Execução da Prova
            hits = 0
            mrr_sum = 0
            total_latency = 0
            
            scenario_details = []

            for case in self.dataset:
                start_time = time.time()
                
                # Suporta tanto sintaxe LangChain (.invoke) quanto antiga (.get_relevant_documents)
                try:
                    if hasattr(retriever_instance, 'invoke'):
                        docs = retriever_instance.invoke(case.query)
                    elif hasattr(retriever_instance, 'query'): # LlamaIndex
                         response = retriever_instance.query(case.query)
                         docs = response.source_nodes # Adaptação genérica
                    else:
                        docs = retriever_instance.get_relevant_documents(case.query)
                except Exception as e:
                    docs = []
                
                latency = time.time() - start_time
                total_latency += latency
                
                # C. Cálculo de Métricas
                is_hit, reciprocal_rank = self._calculate_metrics(docs, case.expected_id)
                
                if is_hit: hits += 1
                mrr_sum += reciprocal_rank
                
                scenario_details.append({
                    "query": case.query,
                    "expected": case.expected_id,
                    "hit": is_hit,
                    "rank": 1/reciprocal_rank if is_hit else 0,
                    "latency": latency
                })

            # D. Consolidação do Cenário
            num_cases = len(self.dataset)
            summary = {
                **config, # Expande os parâmetros como colunas (k, chunk, strategy...)
                "Hit Rate": hits / num_cases,
                "MRR": mrr_sum / num_cases, # Métrica de 'quão no topo' estava a resposta
                "Avg Latency (s)": round(total_latency / num_cases, 4)
            }
            results_summary.append(summary)
            
            # Opcional: Limpeza de memória se o factory retornar algo pesado
            if hasattr(retriever_instance, 'vectorstore'):
                del retriever_instance.vectorstore

        return pd.DataFrame(results_summary)
    
    # Adicione isso dentro da classe UniversalRAGEvaluator
    def print_report(self, df):
        """Imprime o DataFrame formatado como tabela Markdown bonita."""
        # Tenta importar tabulate, se não tiver, imprime normal
        try:
            import tabulate
        except ImportError:
            print("Instale 'tabulate' para ver tabelas bonitas: pip install tabulate")
            print(df)
            return

        print("\n" + "="*80)
        print(f"📊 REPORT FINAL: {len(df)} CENÁRIOS TESTADOS")
        print("="*80)
        # floatfmt controla as casas decimais
        print(df.to_markdown(index=False, floatfmt=".2f"))
        print("="*80)