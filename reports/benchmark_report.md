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

## 3. Ví dụ Output thực tế (Trích đoạn)

### Single-Agent Baseline
> "GraphRAG has matured from a proof‑of‑concept in 2023 to a robust, production‑ready architecture that couples dense retrieval, graph‑structured reasoning, and LLM generation. The state‑of‑the‑art pipeline leverages hybrid text‑graph construction, graph‑aware reranking (GraphBERT‑Rerank, Diffusion‑RAG), and grounding mechanisms..."
*(Sinh ra trực tiếp từ kiến thức có sẵn của mô hình)*

### Multi-Agent System
> "GraphRAG extracts **entity‑relation triples** from a corpus, stores them in a **knowledge graph (KG)**, and performs **graph‑aware retrieval** before prompting the LLM. This design gives the system three decisive advantages: (1) multi‑hop relational reasoning, (2) persistent factual grounding across long‑form generation, and (3) sub‑linear scalability... **References**: 1. GraphRAG-Hybrid (2023), 2. GraphPrompt (2024), 3. RAG-GraphLoop (2024)"
*(Tổng hợp chi tiết, có số liệu và reference trích xuất từ Search Client)*
