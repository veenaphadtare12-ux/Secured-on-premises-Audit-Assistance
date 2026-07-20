# Secured On-Premises Audit Assistance

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-White?style=for-the-badge&logo=ollama&logoColor=black)
![SQLite/PostgreSQL](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-336791?style=for-the-badge&logo=postgresql&logoColor=white)

An enterprise-grade, **100% on-premises AI Auditing Assistant** designed for secure corporate environments. Built using **LangGraph** and local LLMs (via Ollama) to ensure that highly sensitive financial data, corporate ledgers, and employee receipts never leave the internal network.

##  Key Features

https://github.com/user-attachments/assets/aea45aa1-3f24-46f4-9240-532a8890c966

Uses an advanced agentic workflow where a **Planner Node** intelligently analyzes the user's intent and routes the query to specialized expert lanes (Visualization, Policy RAG, or Receipt Auditing).

###  Automated Business Intelligence
Can automatically convert natural language questions (e.g., *"What were our travel expenses in Q3?"*) into strict SQL queries against the corporate ledger. It then uses Llama 3 to structure the raw database output and deterministically renders beautiful, corporate-ready charts using Matplotlib.

###  Secure Document RAG
Features a Retrieval-Augmented Generation (RAG) pipeline to ingest and index hundreds of pages of corporate policy PDFs. Auditors can query the AI for specific compliance rules and receive instant answers cited directly from the internal rulebook.

###  Automated Receipt Auditing
An OCR/LLM-based pipeline that ingests raw scanned receipts, extracts structured financial data (vendor, date, total, tax), and flags potential policy violations or ledger discrepancies.

##  Technology Stack
*   **AI Framework:** LangChain & LangGraph
*   **Local LLMs:** Ollama (Llama 3) for 100% data privacy
*   **Databases:** SQLite (Local) / PostgreSQL (Production via Docker)
*   **Data Science:** Matplotlib (Automated Visualizations), Pandas
*   **Vector Search:** Local embeddings for PDF RAG pipeline

