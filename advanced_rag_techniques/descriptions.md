# Advanced RAG Techniques - Notebook Descriptions

This folder contains implementations of advanced Retrieval-Augmented Generation (RAG) techniques that go beyond basic RAG to solve specific challenges and improve performance in various scenarios.

## 📝 Notebook Overview

### 1. **Naive RAG** (`naive_rag.ipynb`)
**The Simplest RAG Implementation**

The Naive RAG is the simplest technique in the RAG ecosystem, providing a straightforward approach to combining retrieved data with LLM models for efficient user responses. This notebook implements a basic RAG system using Azure OpenAI and FAISS, demonstrating how to:
- Load and process CSV data into a vector database
- Perform semantic search on documents
- Generate AI responses based on retrieved context
- Handle Windows encoding issues and Azure OpenAI rate limits

**Key Features**: Windows compatibility, rate limit management, educational vectorstore exploration, Azure integration, robust error handling.

**Research Paper**: [RAG](https://arxiv.org/pdf/2005.11401)

---

### 2. **Unstructured RAG** (`basic_unstructured_rag.ipynb`)
**Handling Complex Multi-Modal Documents**

Unstructured or (Semi-Structured) RAG is a method designed to handle documents that combine text, tables, and images. It addresses challenges like broken tables caused by text splitting and the difficulty of embedding tables for semantic search. This implementation uses unstructured.io to parse and separate text, tables, and images from complex PDFs.

**Key Features**: Advanced PDF parsing, multi-modal content processing (text/tables/images), OCR integration, intelligent chunking strategy, high-resolution processing.

**Tool Reference**: [Unstructured](https://unstructured.io/)

---

### 3. **Contextual RAG** (`contextual_rag.ipynb`)
**Intelligent Document Compression**

Contextual Retrieval-Augmented Generation (RAG) is an advanced RAG technique that improves response relevance and efficiency by incorporating contextual compression during the retrieval process. Instead of passing entire retrieved documents to the LLM, it intelligently compresses and filters content to include only the most relevant information for each query.

**Key Features**: Document compression layer, query-aware filtering, cost optimization, noise reduction, LLM-based content extraction.

**Reference**: [Contextual RAG](https://python.langchain.com/docs/how_to/contextual_compression/)

---

### 4. **RAG Fusion** (`fusion_rag.ipynb`)
**Multi-Query Retrieval with Rank Fusion**

RAG-Fusion is an enhanced version of the traditional RAG model that generates multiple sub-queries from a single user question, retrieves documents for each sub-query, then uses Reciprocal Rank Fusion (RRF) to intelligently combine and rank results for optimal context selection. This approach provides more comprehensive coverage of relevant information.

**Key Features**: Multi-query generation, perspective diversification, Reciprocal Rank Fusion scoring, comprehensive topic exploration, production-grade vector database integration.

**Research Paper**: [RAG Fusion](https://arxiv.org/pdf/2402.03367)

---

### 5. **Hybrid RAG** (`hybrid_rag.ipynb`)
**Combining Semantic and Keyword Search**

Hybrid RAG refers to an advanced retrieval technique that combines vector similarity search with traditional search methods, such as full-text search or BM25. This approach enables more comprehensive and flexible information retrieval by leveraging the strengths of both methods: vector similarity for semantic understanding and traditional techniques for precise keyword or text-based matching.

**Key Features**: Dual retrieval system (vector + BM25), ensemble retriever with weighted scoring, semantic and keyword matching, comprehensive search coverage.

**Research Papers**: [Paper 1](https://arxiv.org/pdf/2408.05141) and [Paper 2](https://arxiv.org/pdf/2408.04948)

---

### 6. **HyDE RAG** (`hyde_rag.ipynb`)
**Hypothetical Document Embeddings**

HyDE operates by creating hypothetical document embeddings that represent ideal documents relevant to a given query. This method contrasts with conventional RAG systems, which typically rely on the similarity between a user's query and existing document embeddings. By generating these hypothetical embeddings, HyDE effectively guides the retrieval process towards documents that are more likely to contain pertinent information.

**Key Features**: Hypothetical document generation, ideal answer simulation, enhanced retrieval guidance, enterprise vector database integration, GraphQL API support.

**Research Paper**: [HyDE](https://arxiv.org/pdf/2212.10496)

---

### 7. **Parent Document Retriever** (`parent_document_retriever.ipynb`)
**Hierarchical Document Management**

Parent Document Retriever is a technique where large documents are split into smaller pieces, called "child chunks." These chunks are stored in a way that lets the system find and compare specific parts of a document with a user's query. The large document, or "parent," is still kept but is only retrieved if one of its child chunks is relevant to the query, providing richer context while maintaining precise search capabilities.

**Key Features**: Dual-level document splitting, parent-child relationship mapping, context preservation, precision-richness balance, in-memory storage architecture.

**Reference**: [Parent Document Retriever](https://python.langchain.com/docs/how_to/parent_document_retriever/)

---

### 8. **Rewrite-Retrieve-Read (RRR)** (`rewrite_retrieve_read.ipynb`)
**Query Optimization Framework**

Rewrite-Retrieve-Read is a three-step framework for tasks that involve retrieval augmentation, such as open-domain question answering. It focuses on improving the quality of retrieved information and generating accurate outputs by refining the input query. Instead of using the original user query directly, RRR first optimizes the query for better document matching, then retrieves and generates responses.

**Key Features**: Three-step framework (Rewrite-Retrieve-Read), query optimization, LLM-based query enhancement, semantic alignment improvement, retrieval effectiveness optimization.

**Research Paper**: [Rewrite-Retrieve-Read](https://arxiv.org/pdf/2305.14283)

---

## 🎯 Choosing the Right Technique

- **Start with Naive RAG** for basic understanding and simple use cases
- **Use Unstructured RAG** for documents with tables, images, and complex layouts
- **Apply Contextual RAG** when cost optimization and noise reduction are priorities
- **Implement Fusion RAG** for comprehensive topic coverage and multi-perspective retrieval
- **Choose Hybrid RAG** when you need both semantic understanding and exact keyword matching
- **Use HyDE** when you want to improve retrieval through hypothetical document generation
- **Apply Parent Document Retriever** when you need precise search with rich context
- **Use RRR** when query optimization can significantly improve retrieval quality

## 📚 Common Dependencies

Most notebooks share these core dependencies:
- `langchain` and `langchain-community` for RAG orchestration
- `langchain-openai` for Azure OpenAI integration
- Vector databases: `faiss-cpu`, `chromadb`, `qdrant`, or `weaviate`
- `athina` for RAG evaluation and monitoring
- `pandas` for data handling

## 🔧 Setup Requirements

1. **API Keys**: OpenAI/Azure OpenAI, Athina, and vector database credentials
2. **Environment**: Python 3.8+ with appropriate package installations
3. **Data**: CSV files in the `../data/` directory for testing
4. **System Dependencies**: Some notebooks require additional system packages (OCR tools, PDF processors)

Each notebook includes detailed setup instructions and step-by-step implementation guides for educational purposes.
