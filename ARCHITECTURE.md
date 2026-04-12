# KubeSentient Architecture

The following diagram illustrates the high-level architecture of the KubeSentient autonomous SRE agent.

```mermaid
graph TD
    subgraph "Observability Layer"
        Prometheus[Prometheus] -->|Alert| AM[AlertManager]
        AM -->|Webhook POST| API[FastAPI Ingestion Layer]
    end

    subgraph "KubeSentient Pod"
        API -->|Async Event| Agent[LangGraph Agent Core]
        
        subgraph "Memory & Knowledge"
            Agent <-->|Query Context| Weaviate[(Weaviate Vector DB)]
            Ingest[Runbook Ingestion] -->|Chunk & Embed| Weaviate
        end
        
        subgraph "Tools"
            Agent -->|Exec| K8sTool[K8s Tool (kubectl)]
            Agent -->|Read| Logs[Log Reader]
            Agent -->|Analysis| RAG[RAG Query Engine]
        end
    end

    subgraph "External Interactions"
        K8sTool -->|API Call| K8sAPI[Kubernetes API Server]
        Agent -->|Proposal/Message| Slack[Slack Integration]
        Slack -->|Approval/Feedback| API
    end

    classDef component fill:#326ce5,stroke:#fff,stroke-width:2px,color:#fff;
    classDef storage fill:#ff9900,stroke:#fff,stroke-width:2px,color:#fff;
    classDef external fill:#ddd,stroke:#333,stroke-width:2px,color:#333;

    class Agent,API,Ingest,K8sTool,RAG component;
    class Weaviate,Prometheus,AM storage;
    class Slack,K8sAPI external;
```

## Core Components
- **FastAPI Layer**: Endpoint for AlertManager webhooks and Slack interactivity.
- **LangGraph Agent**: Stateful orchestration of the investigation and remediation workflow.
- **Weaviate**: Stores chunked runbooks and historical incident context.
- **Kubernetes Tools**: Safe wrappers around `client-python` to inspect cluster state.
