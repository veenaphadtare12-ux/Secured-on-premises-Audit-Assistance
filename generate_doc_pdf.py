import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # Draw Title Page backgrounds
        if self._pageNumber == 1:
            # Decorative left colored bar
            self.setFillColor(colors.HexColor("#1a365d"))
            self.rect(0, 0, 18, 792, fill=True, stroke=False)
            
            # Bottom colored footer stripe
            self.setFillColor(colors.HexColor("#2b6cb0"))
            self.rect(18, 0, 594, 25, fill=True, stroke=False)
            
            self.restoreState()
            return
            
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#7f8c8d"))
        
        # Header text and line
        self.drawString(54, 750, "On-Premises Local AI Financial Audit & BI Assistant — EDI Sem IV")
        self.setStrokeColor(colors.HexColor("#bdc3c7"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer text and line
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "CONFIDENTIAL — ACADEMIC PROJECT DOCUMENTATION")
        self.line(54, 52, 558, 52)
        
        self.restoreState()

def build_pdf(filename="audit_files/project_documentation.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # 54pt margin all around (0.75 in). Letter size is 612 x 792 pt. Printable height: 54 to 738.
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=colors.HexColor("#1a365d"),
        spaceAfter=15,
        spaceBefore=120
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4a5568"),
        spaceAfter=40
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#718096"),
        spaceAfter=8
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1a365d"),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2b6cb0"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2d3748"),
        spaceAfter=8
    )
    
    body_bold_style = ParagraphStyle(
        'CustomBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1a202c"),
        backColor=colors.HexColor("#f7fafc"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )
    
    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2d3748"),
        leftIndent=20,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2d3748")
    )
    
    table_cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#1a365d")
    )

    story = []
    
    # ================= COVER PAGE =================
    story.append(Spacer(1, 40))
    story.append(Paragraph("ACADEMIC PROJECT REPORT", meta_style))
    story.append(Paragraph("On-Premises Local AI Financial Audit & Business Intelligence Assistant", title_style))
    story.append(Paragraph("A Multi-Modal, Privacy-Preserving Agentic Decision System", subtitle_style))
    story.append(Spacer(1, 150))
    
    # Meta box
    meta_info = """
    <b>Course:</b> Engineering Design and Innovation (EDI) - Semester IV<br/>
    <b>Architecture:</b> LangGraph Orchestrated State Machine / RAG / Computer Vision<br/>
    <b>AI Models:</b> Local Llama 3 (Ollama) & Microsoft Florence-2 Base VLM<br/>
    <b>Database:</b> Relational PostgreSQL in Docker & Persistent ChromaDB Vector Store
    """
    story.append(Paragraph(meta_info, body_style))
    story.append(PageBreak())
    
    # ================= SECTION 1 =================
    story.append(Paragraph("1. Executive Summary & Project Goal", h1_style))
    story.append(Paragraph(
        "Modern enterprises handle massive volumes of financial transactions, employee expense sheets, and invoices daily. "
        "Auditing these records to detect discrepancies, fraud, or violations of corporate compliance policies is incredibly complex. "
        "Furthermore, sending proprietary ledgers and scanned visual receipts to external cloud-hosted LLM services (like OpenAI or Anthropic) "
        "presents substantial data privacy risks and security liabilities.",
        body_style
    ))
    story.append(Paragraph(
        "<b>The Solution:</b> This project implements an entirely <b>on-premises, local-first AI assistant</b> designed to perform automated, "
        "multi-modal financial audits and high-fidelity business intelligence analysis. The system runs fully offline on local consumer-grade GPU/CPU "
        "hardware, keeping all enterprise data secure within the organizational firewall.",
        body_style
    ))
    story.append(Paragraph(
        "By orchestrating multiple specialized AI modules, the system accomplishes three core objectives:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Structured Data Querying:</b> Translates colloquial English questions into complex PostgreSQL queries using a local text-to-SQL pipeline.", bullet_style))
    story.append(Paragraph("&bull; <b>Dynamic Business Intelligence:</b> Parses database rows and generates custom visual charts (pie, bar) programmatically using Matplotlib.", bullet_style))
    story.append(Paragraph("&bull; <b>Multi-Modal Compliance Auditing:</b> Performs a three-way verification matching the <b>Database Ledger entry</b>, "
                           "the scanned <b>physical receipt's visual OCR</b>, and <b>corporate guidelines</b> retrieved via a Vector Database.", bullet_style))
    story.append(Spacer(1, 10))
    
    # ================= SECTION 2 =================
    story.append(Paragraph("2. System Architecture & High-Level Workflow", h1_style))
    story.append(Paragraph(
        "The application is structured as a multi-layered agentic system coordinated by a LangGraph workflow. The modular design "
        "separates parsing, database access, document search, and orchestration into independent nodes.",
        body_style
    ))
    
    story.append(Paragraph("The workflow transitions through several core phases:", h2_style))
    
    story.append(Paragraph("<b>1. Input Query & Planning:</b> The user submits an arbitrary text command via a REST API. "
                           "The <i>Planner Node</i> analyzes the prompt and classifies the intent using a strict Pydantic JSON schema.", body_style))
    story.append(Paragraph("<b>2. Decision-Based Routing:</b> Based on the intent, the LangGraph router directs execution into one of three isolated lanes:", body_style))
    
    # Indented block or table for the lanes
    lane_data = [
        [Paragraph("<b>Lane</b>", table_header_style), Paragraph("<b>Execution Workflow</b>", table_header_style)],
        [Paragraph("<b>Visualization Lane</b>", table_cell_bold_style), Paragraph("Fetches SQL data &rarr; structures values using LLM &rarr; renders and saves a high-quality chart using Matplotlib.", table_cell_style)],
        [Paragraph("<b>Analysis Lane</b>", table_cell_bold_style), Paragraph("Fetches relational rows &rarr; feeds them to the LLM &rarr; synthesizes a short, precise corporate performance summary.", table_cell_style)],
        [Paragraph("<b>Audit Lane</b>", table_cell_bold_style), Paragraph("Extracts transaction ID &rarr; queries PostgreSQL ledger &rarr; scans visual receipt using Florence-2 VLM &rarr; queries ChromaDB for relevant policies &rarr; synthesizes final compliance report.", table_cell_style)]
    ]
    t_lanes = Table(lane_data, colWidths=[130, 374])
    t_lanes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1a365d")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    story.append(t_lanes)
    story.append(Spacer(1, 15))
    story.append(PageBreak())
    
    # ================= SECTION 3 =================
    story.append(Paragraph("3. Detailed File-by-File Breakdown", h1_style))
    story.append(Paragraph(
        "The codebase is modular, keeping data generation, ML processing, relational database management, "
        "and HTTP APIs fully separated. Below is a comprehensive list and technical breakdown of each file in the workspace:",
        body_style
    ))
    
    # Create big list of files
    file_details = [
        ("docker-compose.yml", 
         "<b>Type:</b> Configuration File<br/>"
         "<b>Technologies:</b> Docker, PostgreSQL 15 Alpine<br/>"
         "<b>Detailed Description:</b> Defines the local container services. It spins up a PostgreSQL relational database on port 5432, "
         "pre-configured with the user <i>audit_admin</i>, database name <i>corporate_ledger</i>, and a secure password. "
         "A Docker volume is mounted to make the data persistent."),
         
        ("setup_db.py", 
         "<b>Type:</b> Database Initiator<br/>"
         "<b>Technologies:</b> SQLite, Pandas, Random<br/>"
         "<b>Detailed Description:</b> Generates a baseline local SQLite database file named <i>corporate_ledger.db</i> with an <i>expenses</i> table. "
         "It generates 2,500 random corporate transaction rows spanning multiple categories (Travel, Hardware, software, Food & Bev, Consulting, Shipping) "
         "to serve as sample data."),
         
        ("data_pipeline.py",
         "<b>Type:</b> Production Data Generator<br/>"
         "<b>Technologies:</b> PostgreSQL, SQLAlchemy, Pandas, Faker<br/>"
         "<b>Detailed Description:</b> Creates a more realistic dataset consisting of 1,500 enterprise rows. Unlike `setup_db.py`, it inserts this "
         "data directly into the running PostgreSQL Docker container. It defines category-specific price bounds (e.g. software/hardware ranges from "
         "$1,000 to $25,000 while travel ranges from $50 to $3,000) for realistic business metrics."),
         
        ("migrate_to_postgres.py",
         "<b>Type:</b> Database Migration Script<br/>"
         "<b>Technologies:</b> SQLAlchemy, Pandas, SQLite, PostgreSQL<br/>"
         "<b>Detailed Description:</b> Performs a database migration. It queries the local SQLite file's system catalogs, extracts "
         "all database tables, and copies their entire schema and records into the running PostgreSQL container, safely replacing outdated rows."),
         
        ("generate_docs.py",
         "<b>Type:</b> Mock Unstructured Data Generator<br/>"
         "<b>Technologies:</b> ReportLab, Pillow (PIL)<br/>"
         "<b>Detailed Description:</b> Programmatically builds PDF policies (e.g., travel policies with VP spending thresholds and approved hardware vendors) "
         "and physical receipt images (PNG files) with embedded transaction details. It injects intentional anomalies (e.g. TXN-1004 has an image amount "
         "of $990 but a database amount of $890, and TXN-1003 exceeds the VP travel budget limit of $1000) for testing AI accuracy."),
         
        ("generate_receipts.py",
         "<b>Type:</b> Dynamic Bulk Receipt Generator<br/>"
         "<b>Technologies:</b> PostgreSQL, SQLAlchemy, Pandas, Pillow (PIL), Random<br/>"
         "<b>Detailed Description:</b> Fetches the live transaction database from PostgreSQL, samples 50 rows, and creates highly realistic "
         "scanned receipts for them. It injects random anomalies: 15% have ledger mismatches (fraud), 15% are missing completely, and 70% match perfectly."),
         
        ("ingest_pdfs.py",
         "<b>Type:</b> Knowledge Ingestion Pipeline<br/>"
         "<b>Technologies:</b> LangChain, PyPDFDirectoryLoader, ChromaDB, HuggingFaceEmbeddings<br/>"
         "<b>Detailed Description:</b> Processes raw unstructured policy PDFs in <i>audit_files/policies</i>. It loads pages, divides them into small "
         "500-character blocks with 50-character overlaps, converts them into high-dimensional vectors via the <i>all-MiniLM-L6-v2</i> model, and saves "
         "the records into a local vector database directory called <i>chroma_db/</i>.")
    ]
    
    # Render first half of files in table
    table_data = [[Paragraph("<b>File Name</b>", table_header_style), Paragraph("<b>Detailed Purpose & Features</b>", table_header_style)]]
    for filename, desc in file_details:
        table_data.append([
            Paragraph(f"<b>{filename}</b>", table_cell_bold_style),
            Paragraph(desc, table_cell_style)
        ])
        
    t_files1 = Table(table_data, colWidths=[130, 374])
    t_files1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1a365d")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    
    story.append(t_files1)
    story.append(PageBreak())
    
    # Remaining files
    file_details2 = [
        ("chat_with_pdfs.py",
         "<b>Type:</b> Conversational Policy Engine<br/>"
         "<b>Technologies:</b> ChromaDB, LangChain, ChatOllama (Llama 3)<br/>"
         "<b>Detailed Description:</b> Features a command-line RAG application that queries local corporate compliance guidelines. "
         "It retrieves the 3 most relevant context blocks from ChromaDB based on the user's prompt and sends them to Llama 3 for a precise, "
         "context-bounded compliance answer. It also houses `query_policy` for programmatic LangGraph lookups."),
         
        ("sql_tools.py",
         "<b>Type:</b> Natural Language Database Tool<br/>"
         "<b>Technologies:</b> LangChain, SQLDatabase, ChatOllama (Llama 3)<br/>"
         "<b>Detailed Description:</b> Implements a robust text-to-SQL utility. When fed a sentence, it dynamically fetches the PostgreSQL catalog schema, "
         "generates correct SQL, executes the query via LangChain's SQL runner, and pipes the outcome and original prompt to Llama 3 to formulate a natural response."),
         
        ("planner_node.py",
         "<b>Type:</b> Intent Classifier & Step Planner<br/>"
         "<b>Technologies:</b> Pydantic, LangChain, ChatOllama (Llama 3)<br/>"
         "<b>Detailed Description:</b> Standardizes inputs entering the system. Using strict Pydantic schemas, it asks Llama 3 to output JSON containing "
         "the user's underlying category (intent) and a list of tool steps (e.g. <i>[fetch_sql_data, generate_chart]</i>) to follow."),
         
        ("receipt_parser.py",
         "<b>Type:</b> Vision OCR & Formatting Node<br/>"
         "<b>Technologies:</b> PyTorch, Transformers, Florence-2 Base, ChatOllama<br/>"
         "<b>Detailed Description:</b> Orchestrates visual document parsing. It passes visual invoice images to Microsoft's Florence-2 model to extract "
         "printed characters using the model's native <i>&lt;OCR&gt;</i> task. It then uses Llama 3 to parse the unstructured text block into a rigid JSON structure "
         "({vendor, txn_id, amount}). Includes a patch to run locally without requiring flash attention dependencies."),
         
        ("master_agent.py",
         "<b>Type:</b> Workflow Orchestration Core<br/>"
         "<b>Technologies:</b> LangGraph, Matplotlib, ChatOllama (Llama 3), Regex<br/>"
         "<b>Detailed Description:</b> The central state machine. It establishes the LangGraph nodes, routing edges, and shared memory (BIState). "
         "It coordinates executing the Visualization Lane (programmatic Matplotlib charts), Analysis Lane (conversational stats analysis), "
         "or the Audit Lane (a multi-modal audit verifying database logs vs receipt OCR vs company policy RAG contexts)."),
         
        ("api.py",
         "<b>Type:</b> REST API Daemon Gateway<br/>"
         "<b>Technologies:</b> FastAPI, Uvicorn, CORS, StaticFiles<br/>"
         "<b>Detailed Description:</b> Serves the backend AI to user interfaces. It runs on port 8123 and features a single POST endpoint <i>/ask</i>. "
         "It accepts text queries, invokes the compiled LangGraph agent, returns the synthesized textual report, and maps static file paths "
         "to display dynamically generated charts."),
         
        ("test_llm.py",
         "<b>Type:</b> Diagnostics Script<br/>"
         "<b>Technologies:</b> LangChain, ChatOllama (Llama 3)<br/>"
         "<b>Detailed Description:</b> A simple diagnostics tool to verify that the local connection to your Ollama model is operating properly. "
         "It outputs standard test code while timing local model generation speeds.")
    ]
    
    table_data2 = [[Paragraph("<b>File Name</b>", table_header_style), Paragraph("<b>Detailed Purpose & Features</b>", table_header_style)]]
    for filename, desc in file_details2:
        table_data2.append([
            Paragraph(f"<b>{filename}</b>", table_cell_bold_style),
            Paragraph(desc, table_cell_style)
        ])
        
    t_files2 = Table(table_data2, colWidths=[130, 374])
    t_files2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1a365d")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f7fafc")]),
    ]))
    
    story.append(t_files2)
    story.append(Spacer(1, 15))
    story.append(PageBreak())
    
    # ================= SECTION 4 =================
    story.append(Paragraph("4. The 3-Way Auditing Match Logic", h1_style))
    story.append(Paragraph(
        "The crown jewel of the system is the <b>Multi-Modal Audit Lane</b> in <code>master_agent.py</code>. "
        "It automates checks that typically consume hours of manual audit time. Here is exactly how the 3-way matching logic operates:",
        body_style
    ))
    
    story.append(Paragraph("<b>Step 1: Database Querying</b>", h2_style))
    story.append(Paragraph(
        "Using the identified transaction ID (e.g. <i>TXN-1004</i>), the agent queries the PostgreSQL database using SQL tools "
        "to pull the formal amount and vendor recorded on the ledger: <code>db_data = sql_response['answer']</code>.",
        body_style
    ))
    
    story.append(Paragraph("<b>Step 2: Scanned Receipt Analysis (Vision VLM)</b>", h2_style))
    story.append(Paragraph(
        "The agent checks the physical server for a scanned file matching the pattern <code>receipt_TXN-1004.png</code>. "
        "It sends this picture through the <b>Florence-2 vision model</b>. The vision model performs a dense Optical Character Recognition (OCR) "
        "scan to extract all visible text. That text is immediately passed to a local Llama 3 formatter that extracts the vendor and actual visual "
        "invoice total: <code>receipt_data = extract_receipt_data(image_path)</code>.",
        body_style
    ))
    
    story.append(Paragraph("<b>Step 3: Corporate Policy Verification (RAG)</b>", h2_style))
    story.append(Paragraph(
        "The agent automatically performs a vector lookup query inside ChromaDB: <i>'What is the policy for receipt discrepancies, "
        "matching amounts, and manual review thresholds?'</i> and pulls the exact text matching those policies.",
        body_style
    ))
    
    story.append(Paragraph("<b>Step 4: AI Audit and Compliance Verdict</b>", h2_style))
    story.append(Paragraph(
        "The agent feeds the outputs of all three channels into a final Llama 3 prompt, acting as a strict audit supervisor. It evaluates:",
        body_style
    ))
    story.append(Paragraph("1. Did the database ledger amount match the visual receipt total exactly?", bullet_style))
    story.append(Paragraph("2. Does the expense violate vendor limitations (e.g., procurement of non-approved brands)?", bullet_style))
    story.append(Paragraph("3. Does the transaction size exceed specific executive limits requiring documented VP approval?", bullet_style))
    story.append(Paragraph("Finally, the AI outputs a concise corporate verdict: <b>APPROVED</b> or <b>FLAGGED FOR REVIEW</b> along with a clear summary.", body_style))
    story.append(Spacer(1, 10))
    
    # ================= SECTION 5 =================
    story.append(Paragraph("5. Execution & Deployment Guide", h1_style))
    story.append(Paragraph(
        "To run the complete workspace locally in a unified flow, follow these terminal steps:",
        body_style
    ))
    
    step_code = """# 1. Start the local database container
docker-compose up -d

# 2. Build the fake databases, documents, and policies
python setup_db.py
python generate_docs.py
python ingest_pdfs.py

# 3. Migrate database tables and load PostgreSQL
python migrate_to_postgres.py
python data_pipeline.py
python generate_receipts.py

# 4. Boot up the local web service gateway
python api.py"""
    story.append(Paragraph(step_code.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print("[SUCCESS] Premium Documentation PDF generated successfully at 'audit_files/project_documentation.pdf'")

if __name__ == "__main__":
    build_pdf()
