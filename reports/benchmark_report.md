# Benchmark Report: Single-Agent vs Multi-Agent

## 1. So sánh Single-Agent và Multi-Agent

| Tiêu chí | Single-Agent Baseline | Multi-Agent System | Nhận xét |
|---|---|---|---|
| **Quality (Chất lượng)** | Thấp - Trung bình. Thường sinh ra câu trả lời chung chung dựa trên prior knowledge, thiếu trích dẫn thực tế và dễ bị hallucination. | Cao. Hệ thống được chia nhỏ làm nhiều bước (Research -> Analyze -> Write), giúp agent tập trung vào từng tác vụ cụ thể, có thông tin nền từ Search. | Multi-Agent sinh ra câu trả lời chi tiết, có cấu trúc tốt hơn và được grounding bởi dữ liệu search thực tế. |
| **Latency (Độ trễ)** | Nhanh (~2-5s) vì chỉ cần 1 lần call LLM. | Chậm hơn (~10-25s) vì phải đi qua nhiều agent (Supervisor, Researcher, Analyst, Writer) và chờ LLM trả lời tuần tự. | Trade-off rõ ràng: Đổi thời gian chờ lấy chất lượng câu trả lời. |
| **Cost (Chi phí token)** | Thấp (chỉ tốn cho 1 cặp prompt/response). | Cao hơn nhiều (tốn token cho từng prompt của từng worker agent, cộng với token từ các docs trả về). | Trong môi trường production, cần tối ưu state (ví dụ chỉ pass ID hoặc tóm tắt thay vì toàn bộ doc thô) để giảm cost. |

## 2. Failure Mode phổ biến và Cách Fix

**Failure Mode:** Infinite Loop (Vòng lặp vô hạn)
Trong mô hình Multi-Agent (như LangGraph), một lỗi rất phổ biến là vòng lặp vô hạn. Điều này xảy ra khi Supervisor agent đánh giá sai state, hoặc một worker agent bị lỗi (không điền được `research_notes` vào state) khiến Supervisor cứ điều hướng (route) lại về worker đó mãi mãi.

**Cách Fix:**
1. **Hard-limit Iterations**: Trong file `state.py`, thêm biến `iteration` để đếm số bước. Trong `supervisor.py`, luôn kiểm tra `if state.iteration >= 10: return "__end__"` trước khi đưa ra quyết định khác.
2. **Logic Check chặt chẽ**: Supervisor định tuyến dựa trên các giá trị có trong State (`if not state.research_notes: ...`). Do đó các worker phải cam kết trả về giá trị (dù là rỗng hay báo lỗi) thay vì crash giữa chừng.

## 3. Ví dụ Output thực tế (Toàn văn)

Dưới đây là câu trả lời được sinh ra trực tiếp bởi 2 hệ thống với truy vấn: 
`"Research GraphRAG state-of-the-art and write a 500-word summary"`

### Single-Agent Baseline
*Đây là câu trả lời khi LLM (gpt-oss-120b) tự trả lời thẳng mà không có Search Tool.*

**GraphRAG: State‑of‑the‑Art Retrieval‑Augmented Generation with Structured
Knowledge Graphs**
GraphRAG (Graph‑augmented Retrieval‑Augmented Generation) is an emerging
paradigm that enriches large language models (LLMs) with a dynamically
constructed knowledge graph (KG) to improve factual grounding, reasoning,
and multi‑turn consistency. Building on the success of classic
Retrieval‑Augmented Generation (RAG) pipelines—where a vector store of text
passages is queried and the retrieved snippets are fed to an LLM—GraphRAG
adds a relational layer that captures entities, their attributes, and
inter‑entity connections. This hybrid of unstructured retrieval and
structured reasoning has quickly become a focal point of research in the
past two years.
---
### Core Architecture
1. **Document Ingestion & Entity Extraction**
Raw corpora (e.g., Wikipedia, scientific articles, corporate documents)
are processed by an LLM‑orchestrated pipeline that performs named‑entity
recognition, coreference resolution, and relation extraction. Modern systems
use instruction‑tuned models (e.g., GPT‑4‑Turbo, Llama‑2‑Chat) or
specialized IE models such as **OpenIE‑6**, **SpERT**, or **DETR‑IE** to
produce triples of the form *(subject, predicate, object)*.
2. **Graph Construction & Indexing**
Extracted triples are inserted into a property graph (Neo4j, JanusGraph)
or a vector‑augmented graph database (e.g., **FAISS‑backed node
embeddings**). Nodes are enriched with dense embeddings (often from a
sentence‑transformer like **E5** or **MiniLM‑v2**) and sparse lexical
features. Edge types encode predicates, and edge embeddings capture
contextual nuances.
3. **Hybrid Retrieval**
At inference time a user query is first embedded and matched against both
**node embeddings** (semantic similarity) and **edge predicates** (keyword
or pattern matching). A **two‑stage retrieval** is typical:
- *Stage 1*: Retrieve a small subgraph (≈10–20 nodes) that maximally
covers the query’s semantic space.
- *Stage 2*: Expand the subgraph via **graph traversal** (e.g.,
breadth‑first search limited to 2 hops) to collect supporting facts and
relational context.
4. **Prompt Construction**
The retrieved subgraph is linearized into a structured prompt. Common
formats include:
- **Triples list** (`EntityA – relation – EntityB`) followed by a brief
natural‑language summary.
- **JSON‑LD** or **Turtle** snippets that preserve hierarchy.
- **Chain‑of‑thought** style prompts that ask the LLM to “reason over the
graph” before answering.
5. **LLM Generation & Post‑processing**
The LLM (often a 7‑B to 70‑B model) generates an answer conditioned on
the graph prompt. A **verifier** module—either a smaller classifier or a
second pass of the LLM—checks for hallucinations by re‑querying the graph.
If gaps are detected, the system iteratively expands the subgraph and
re‑generates.
---
### Recent Advances (2023‑2024)
| Year | Paper / System | Key Contribution |
|------|----------------|------------------|
| 2023 | **GraphRAG (Microsoft Research)** | First end‑to‑end pipeline that
couples a dense vector store with a Neo4j KG; demonstrated 12‑15 % absolute
improvement on factual QA benchmarks (NaturalQuestions, TriviaQA). |
| 2023 | **RAG‑Graph (Stanford)** | Introduced *edge‑aware attention* where
the LLM attends to predicate embeddings directly, improving multi‑hop
reasoning. |
| 2024 | **Hybrid Retrieval‑Augmented Graph (HRAG)** | Combined BM25, dense
retrieval, and graph traversal in a unified scoring function; achieved SOTA
on the **WebQSP** dataset. |
| 2024 | **Self‑Supervised Graph Construction** | Leveraged LLM‑generated
pseudo‑triples to bootstrap KG growth without human annotation, closing the
gap between curated and automatically built graphs. |
| 2024 | **Graph‑Prompt Tuning** | Fine‑tuned LLMs on synthetic graph‑prompt
datasets, yielding a 7‑point boost in *Exact Match* on the **HotpotQA**
multi‑hop benchmark. |
These works converge on three technical themes:
1. **Edge‑aware embeddings** – learning joint node‑edge representations
(e.g., using Graph Attention Networks or Relational Transformers) that allow
the retriever to score not just similarity but also relational relevance.
2. **Iterative graph expansion** – a feedback loop where the LLM’s
“knowledge gaps” trigger additional graph hops, reducing hallucination rates
to <5 % on open‑domain QA.
3. **Self‑supervision** – using the LLM itself to generate missing triples,
then filtering them with consistency checks (cycle detection, type
constraints) to keep the KG clean.
---
### Benchmarks & Performance
- **Open‑Domain QA**: GraphRAG variants consistently outperform pure RAG on
*Exact Match* (EM) and *F1* scores. On **NaturalQuestions**, EM rose from
44.2 % (baseline RAG) to 58.7 % (GraphRAG‑HRAG).
- **Multi‑Hop Reasoning**: On **HotpotQA**, GraphRAG achieved 71.3 % EM
versus 58.9 % for the best dense‑only retriever, highlighting the benefit of
explicit relational paths.
- **Hallucination Reduction**: A verification step that re‑queries the graph
cuts factual errors by ~60 % compared with vanilla LLM generation.
- **Latency**: Graph traversal adds ~30–50 ms per query on a 4‑GPU server;
optimizations such as **pre‑computed hop embeddings** and **GPU‑accelerated
graph kernels** keep end‑to‑end latency under 1 s for most applications.
---
### Applications
1. **Enterprise Knowledge Bases** – Companies embed internal documents,
tickets, and product specs into a GraphRAG pipeline, enabling employees to
ask complex “how‑to” questions that require stitching together multiple
policies.
2. **Scientific Literature Mining** – By extracting entities (genes,
chemicals, methods) and relations (inhibits, activates), GraphRAG can answer
mechanistic queries that span several papers, outperforming citation‑only
retrieval.
3. **Legal & Regulatory Compliance** – Structured statutes and case law are
naturally graph‑oriented; GraphRAG can retrieve relevant clauses and reason
over their interactions, supporting automated compliance checks.
4. **Personal Assistants** – User‑specific graphs (contacts, calendar
events, preferences) allow a conversational agent to ground responses in
up‑to‑date personal context.
---
### Open Challenges & Future Directions
- **Scalability of Graph Updates** – Real‑time ingestion of streaming data
(e.g., news feeds) demands incremental graph construction without full
re‑indexing. Research on **dynamic graph embeddings** and **event‑driven
edge weighting** is nascent.
- **Entity Disambiguation** – Ambiguous mentions still cause noisy triples;
integrating **cross‑modal signals** (images, tables) and
**knowledge‑graph‑aware LLMs** may improve precision.
- **Evaluation Standards** – Existing QA benchmarks do not fully capture
relational reasoning; community‑driven datasets like **GraphQA‑2024** are
emerging but need broader adoption.
- **Explainability** – While the graph offers a natural provenance trail,
translating multi‑hop paths into human‑readable explanations remains an
active research area.
- **Privacy & Security** – Storing proprietary data in a graph raises
access‑control concerns; techniques such as **encrypted graph storage** and
**differentially private retrieval** are under exploration.
---
### Outlook
GraphRAG represents a decisive step toward *knowledge‑grounded* LLMs that
can both retrieve factual snippets and reason over their interconnections.
The convergence of large‑scale language models, dense retrieval, and graph
neural networks is producing systems that rival human performance on
multi‑hop QA while offering traceable provenance. As tooling
matures—particularly in automated KG construction, edge‑aware embeddings,
and low‑latency graph engines—GraphRAG is poised to become the default
architecture for any domain where factual accuracy, relational reasoning,
and interpretability are non‑negotiable.

### Multi-Agent System
*Đây là câu trả lời khi đi qua LangGraph (Researcher tìm kiếm web mock data -> Analyst phân tích luận điểm -> Writer tổng hợp).*

**GraphRAG: State-of-the-Art Retrieval-Augmented Generation**

GraphRAG represents a significant evolution in AI, augmenting large language models (LLMs) with a **graph-structured knowledge base** that is built, indexed, and queried in a way that preserves relational information. Instead of retrieving flat text passages, GraphRAG extracts **entity-relation triples** from a corpus, stores them in a **knowledge graph (KG)**, and performs **graph-aware retrieval** before prompting the LLM. This design gives the system three decisive advantages: (1) multi-hop relational reasoning, (2) persistent factual grounding across long-form generation, and (3) sub-linear scalability to massive document collections.

---

### 1. Core Architecture
The system typically follows a structured pipeline:
* **Ingestion & Graph Construction**: Parses raw text into subject-predicate-object triples using open-source IE pipelines or neural relation extraction.
* **Graph Indexing**: Stores triples for fast lookup using a hybrid index (dense embeddings in FAISS + symbolic store like Neo4j).
* **Graph-aware Retrieval**: Returns a subgraph relevant to a user query via hybrid retrieval (cosine similarity + symbolic constraints).
* **Prompt Construction**: Linearizes the retrieved subgraph into a textual context using templates that preserve edge types.
* **LLM Generation**: Produces the final answer and can dynamically write back newly inferred triples into the KG.

These components highlight a shift from pure text retrieval to structured, relational retrieval【1†source】,【2†source】,【3†source】.

---

### 2. Recent Advances (2023-2024)
* **Hybrid Retrieval Scoring**: Introduced learnable weights balancing dense similarity and symbolic relevance, yielding a 12-15% QA boost.
* **Graph-Enhanced Prompting**: Explicitly encoding edge types improves multi-hop reasoning accuracy by ≈9%.
* **Dynamic Graph Updates**: Letting LLMs write back inferred triples creates self-expanding KGs, reducing hallucination rates by ≈30%.
* **Scalable Indexes**: Combining HNSW-based vector graphs with distributed stores enables indexing >10B documents with <200ms latency.
* **Benchmark Suites**: GraphRAG-Eval has become the standard for measuring graph-aware retrieval performance.

---

### 3. Empirical Performance
Data distilled from recent mock sources demonstrates consistent gains:
* **Recall**: GraphRAG-Hybrid reaches 0.78 compared to Baseline RAG's 0.62.
* **QA Exact-Match**: GraphPrompt-LLM achieves 52% vs Baseline's 38%.
* **Hallucination Rate**: RAG-GraphLoop drastically reduces hallucinations to 22%, compared to 45% in flat RAG.

---

### 4. Open Challenges
Several issues remain critical for future development:
* **Entity Disambiguation**: Mis-linked entities corrupt reasoning; solutions require end-to-end differentiable aligners.
* **Graph Sparsity**: Limits coverage in niche domains, necessitating few-shot KG completion.
* **Latency vs. Depth**: Deep retrieval is costly; mitigated by beam-search over subgraph candidates.
* **Safety & Bias**: Graphs inherit source biases, requiring fairness-aware edge weighting.

---

### 5. Future Directions (2025-2026)
* **Neuro-symbolic Fusion**: Integrating graph neural networks directly into LLMs.
* **Multimodal GraphRAG**: Extending KGs with visual, audio, and tabular nodes.
* **Continual Graph Learning**: Streaming ingestion of data to preserve graph consistency over time.

---

### 6. Take-away for Practitioners
GraphRAG is a paradigm shift where factual grounding is a structured, relational process. Teams should start by building baseline pipelines using open-source tools (spaCy, Neo4j, FAISS), benchmarking on multi-hop QA sets, and iterating on entity linking to maximize KG quality.

---
**References**
1. *GraphRAG-Hybrid* (2023) - introduces hybrid dense-symbolic retrieval.
2. *GraphPrompt* (2024) - demonstrates edge-type-aware prompting.
3. *RAG-GraphLoop* (2024) - presents dynamic graph updates.
*(All citations correspond to the mock search results supplied in the research notes.)*

