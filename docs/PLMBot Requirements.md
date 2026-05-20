# PLMBot Requirements  
#   
## 1. Overview  
  
This document outlines the requirements for a **PLM RAG (Retrieval-Augmented Generation) prototype**—a low-ops, high-learnability platform designed to answer questions against product lifecycle management (PLM) data and associated technical documents. The prototype’s purpose is to validate **answer accuracy, provenance visibility, and basic operational resilience** in a version-driven PLM environment.  
#   
The prototype will:  
* Combine structured PLM queries with hybrid semantic and keyword-based document retrieval.  
* Support core PLM query patterns such as part lookup, BOM expansion, “where-used” paths, and version comparisons.  
* Provide verifiable answers with document provenance and version awareness.  
* Operate with minimal infrastructure overhead and demonstrate feasibility before full enterprise rollout.  
#   
## 2. Functional Requirements  
  
### 2.1 Core Capabilities  
* **Structured Querying**  
    * Read-only PLM replica or reporting schema access.  
    * Deterministic queries for part lookup, BOM traversal, “where-used” resolution, and as-of-version queries.  
* **Document Retrieval**  
    * Ingest and parse technical documents (PDF, DOCX, XLSX, PPTX, HTML, CSV, images) using Unstructured.  
    * Chunk documents by section/title with version-stamped metadata.  
    * Hybrid retrieval (Postgres full-text + pgvector embedding search) with metadata filtering.  
* **Answer Generation**  
    * Retrieval-augmented responses using LLM prompts with structured facts and top document evidence.  
    * Include provenance in all answers with links to source documents and PLM records.  
* **Version Awareness**  
    * All chunks, embeddings, and documents carry PLM metadata (model_id, model_version, component_id, supplier_id, effective_from/to, document_version, acl_tags).  
    * Immutable indexing by version, with optional "current" aliases for latest releases.  
* **Support limited write-assist workflows for non-destructive PLM interactions.**  
    * The prototype may:  
        * Generate draft Engineering Change Requests (ECRs) or Engineering Change Orders (ECOs).  
        * Propose metadata updates or annotations against PLM entities.  
        * Produce structured change payloads for human review before submission.  
    * The prototype shall not:  
        * Directly modify released BOMs, revisions, supplier assignments, or production PLM records.  
        * Automatically approve or release engineering changes.  
    * All draft write actions must:  
        * Include provenance references to supporting PLM records and retrieved documents.  
        * Capture user identity, timestamp, and generated payload for auditability.  
        * Require explicit human confirmation before persistence or export.  
  
### 2.2 User Experience  
* Chat interface (Next.js/React) with:  
    * Streaming answers from FastAPI backend.  
    * Provenance cards showing document and PLM record sources.  
    * Simple deep links to PLM records.  
#   
### 2.3 Operational Requirements  
* **Ingestion:** Scheduled syncs via Airbyte OSS, plus lightweight Python watchers for file shares.  
* **Refresh:** Triggered by updated_at timestamps, document checksums, or simple CDC where available.  
* **Orchestration:** LangGraph for stateful query routing and operator checkpoints.  
* **Deployment:** Docker Compose or small Kubernetes footprint.  
* **Monitoring & Evaluation:**  
    * OpenTelemetry, Prometheus, Grafana for basic ops.  
    * Langfuse and Ragas for LLM-specific evaluation (context precision, faithfulness).  
* **Audit & Traceability**  
    * All generated draft write actions must be logged with:  
        * Retrieved evidence and source provenance.  
        * Prompt and generated output metadata.  
        * User identity and approval state.  
        * Proposed structured payloads.  
    * Logs should support reproducibility and review of generated recommendations.**Audit & Traceability**  
  
#     
## 3. Critical Design Decisions  
  
**Hybrid Retrieval is Mandatory**  
PLM queries often mix identifiers (requiring keyword or exact SQL match) with narrative engineering text (benefiting from semantic embeddings). Vector-only search is insufficient.  
  
**Version-Aware Indexing**  
Every chunk and embedding is version-stamped; overwriting historical embeddings is forbidden. This ensures reproducibility and avoids silent semantic drift.  
  
**Under-Brokered Architecture**  
The prototype deliberately avoids heavy event brokers or durable orchestration (e.g., Kafka/Temporal) in favor of simplicity. Tradeoff: lower resilience and slower recovery from ingestion failure.  
  
**Minimal Reranking Initially**  
A managed reranker may be added if retrieval precision is insufficient, but early sprints prioritize simplicity.  
  
**Security Scope**  
	OIDC-based auth (Keycloak or enterprise IdP) and basic RBAC are sufficient for pilot usage. Draft write actions require authenticated users and auditable approval checkpoints. Fine-grained ABAC, document-level security, and workflow-integrated authorization are deferred to pilot/enterprise phases.  
  
**Human-in-the-Loop Write Model**  
	The prototype adopts a draft-only write architecture. LLMs may recommend or prepare structured change requests, but authoritative PLM mutations remain under explicit human and workflow control.  
	This approach reduces operational and compliance risk while enabling evaluation of AI-assisted engineering workflows.  
#   
## 4. Non-Functional Requirements  
  
* **Performance:**  
    * Median query latency ≤ 3 seconds with small corpus.  
    * Ingestion refresh cycle ≤ 24 hours for updated documents.  
* **Reliability:**  
    * Prototype tolerates single-node Docker/K8s interruptions; manual restart acceptable.  
* **Maintainability:**  
    * Single Postgres instance holds both relational PLM data and vector embeddings.  
    * Modular Python-based orchestration.  
#   
## 5. Deliverables  
  
* **Prototype Stack:**  
    * Airbyte OSS, Unstructured, pgvector in Postgres, FastAPI backend, LangGraph orchestration, Next.js frontend.  
* **Canonical PLM Query Service**  
    * Exposes read-only access to part lookup, BOM traversal, and version diff queries.  
* **Evaluation Baseline**  
    * 100–200 labeled queries with SME-reviewed answers and RAG performance metrics.  
* **Monitoring Dashboard**  
    * Latency, error rate, token usage, and evaluation scores.  
* **Draft Change Request Prototype**  
    * Prototype workflow for generating structured draft engineering changes with provenance-backed evidence and human approval checkpoints.  
#   
## 6. Open Questions  
  
* Exact PLM schema details and replica capabilities may affect query service design.  
* Document heterogeneity and OCR/table complexity may impact parsing fidelity.  
* Managed vs. self-hosted embedding choice may change with data residency or cost policies.  
#   
## 7. Acceptance Criteria  
  
* Queries return grounded answers with provenance for canonical PLM queries.  
* Version-stamped retrieval prevents cross-version hallucinations.  
* Prototype is deployable on a single-node Docker Compose or minimal K8s cluster.  
* Initial gold set achieves ≥ 70% context precision and ≥ 80% faithfulness in Ragas evaluation.  
* Draft write workflows generate structured, reviewable change proposals with provenance.  
* No autonomous modification of authoritative PLM records occurs.  
* Audit logs capture generated change payloads and supporting evidence.  
#   
