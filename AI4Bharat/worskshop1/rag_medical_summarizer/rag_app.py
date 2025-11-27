import streamlit as st
import rag_lib as glib
import pdfplumber
import os
from datetime import datetime
import chromadb
from chromadb.utils.embedding_functions import AmazonBedrockEmbeddingFunction
import boto3

# Page config with medical theme
st.set_page_config(
    page_title="Medical RAG Analyzer", 
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title(" Medical Document RAG Analyzer")
st.markdown("**Powered by Amazon Bedrock + ChromaDB** - Upload ANY medical PDF from your computer!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "collection_ready" not in st.session_state:
    st.session_state.collection_ready = False
if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None
if "chroma_path" not in st.session_state:
    st.session_state.chroma_path = "./chroma_db"  # Local folder for ChromaDB

# Create ChromaDB directory if it doesn't exist
os.makedirs(st.session_state.chroma_path, exist_ok=True)

# Sidebar - FULL PDF UPLOAD & PROCESSING
with st.sidebar:
    st.header(" Upload Medical Report")
    st.markdown("**Drag & drop or click to browse**")
    
    # PDF UPLOADER - WORKS WITH ANY EXTERNAL PDF
    uploaded_file = st.file_uploader(
        "Choose Medical PDF", 
        type="pdf",
        help="Upload any medical report PDF from your computer"
    )
    
    if uploaded_file is not None:
        # Display file info
        col1, col2 = st.columns(2)
        col1.metric("File", uploaded_file.name)
        col2.metric("Size", f"{uploaded_file.size/1000:.1f} KB")
        
        # Preview first page
        with st.spinner("Previewing..."):
            try:
                with pdfplumber.open(uploaded_file) as pdf:
                    if pdf.pages:
                        first_page = pdf.pages[0]
                        st.image(first_page.to_image().original, caption="Page 1 Preview")
            except:
                st.info(" PDF preview ready!")
        
        # PROCESS PDF BUTTON
        if st.button(" **PROCESS & INDEX PDF**", type="primary", use_container_width=True):
            with st.spinner(" Extracting medical text → Chunking → Indexing to ChromaDB..."):
                try:
                    # Save uploaded PDF temporarily
                    pdf_path = f"./temp_{uploaded_file.name}"
                    with open(pdf_path, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # EXTRACT TEXT & CREATE CHUNKS
                    chunks = []
                    with pdfplumber.open(pdf_path) as pdf:
                        for page_num, page in enumerate(pdf.pages):
                            text = page.extract_text() or ""
                            # Smart chunking for medical reports
                            for i in range(0, len(text), 400):  # 400 char chunks
                                chunk = text[i:i+500]
                                if len(chunk.strip()) > 80:  # Quality filter
                                    chunks.append({
                                        "id": f"{uploaded_file.name.replace(' ', '_')}_p{page_num+1}_c{i//400}",
                                        "text": chunk.strip(),
                                        "metadata": {
                                            "page": page_num + 1,
                                            "source": uploaded_file.name,
                                            "type": "medical_report"
                                        }
                                    })
                    
                    # INDEX TO CHROMADB
                    session = boto3.Session()
                    embedding_fn = AmazonBedrockEmbeddingFunction(
                        session=session, 
                        model_name="amazon.titan-embed-text-v2:0"
                    )
                    
                    client = chromadb.PersistentClient(path=st.session_state.chroma_path)
                    collection = client.get_or_create_collection(
                        name="medical_reports_collection",
                        embedding_function=embedding_fn
                    )
                    
                    # Clear old docs from same PDF
                    collection.delete(where={"source": uploaded_file.name})
                    
                    # ADD NEW CHUNKS
                    if chunks:
                        collection.add(
                            documents=[c["text"] for c in chunks],
                            metadatas=[c["metadata"] for c in chunks],
                            ids=[c["id"] for c in chunks]
                        )
                        
                        st.session_state.collection_ready = True
                        st.session_state.current_pdf = uploaded_file.name
                        st.session_state.total_chunks = len(chunks)
                        st.session_state.total_pages = len(set(c["metadata"]["page"] for c in chunks))
                        
                        st.success(f" **SUCCESS!** Indexed {len(chunks)} chunks from {st.session_state.total_pages} pages")
                        st.balloons()
                        
                        # Cleanup
                        os.unlink(pdf_path)
                    else:
                        st.error(" No text extracted from PDF. Try another file.")
                        
                except Exception as e:
                    st.error(f" Processing failed: {str(e)}")
                    if 'pdf_path' in locals() and os.path.exists(pdf_path):
                        os.unlink(pdf_path)

# STATUS DISPLAY
if st.session_state.collection_ready and st.session_state.current_pdf:
    col1, col2, col3 = st.columns(3)
    col1.metric(" Active PDF", st.session_state.current_pdf)
    col2.metric(" Chunks", st.session_state.get('total_chunks', 0))
    col3.metric(" Pages", st.session_state.get('total_pages', 0))
    
    st.success("**RAG READY** - Ask questions about your medical report!")
else:
    st.warning("**Upload a PDF and click 'PROCESS & INDEX PDF' first!**")

# CHAT INTERFACE
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander(f"📍 Sources ({len(message['sources'])} chunks)", expanded=False):
                for i, source in enumerate(message["sources"][:3]):
                    page = message.get('pages', ['N/A'])[i]
                    st.info(f"**Page {page}:** {source[:350]}...")

# ENABLE CHAT ONLY WHEN READY
if st.session_state.collection_ready:
    if prompt := st.chat_input("Ask about the medical report..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate RAG response
        with st.chat_message("assistant"):
            with st.spinner("Medical RAG analysis in progress..."):
                response, sources = glib.get_rag_response(prompt)
                st.markdown(response)
                
                # Store with metadata
                st.session_state.messages[-1]["sources"] = sources
                st.session_state.messages[-1]["pages"] = ["N/A"] * len(sources)
    
    # Clear chat
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

else:
    st.info(" **Ready to analyze your medical reports! Upload a PDF above.**")

# Medical query examples
with st.sidebar.expander("🏥 Medical Queries", expanded=True):
    st.markdown("""
    **Lab Results**: "What are the blood test results?"
    **Diagnosis**: "What is the diagnosis?"
    **Treatment**: "Recommended medications?"
    **Vitals**: "Patient vital signs summary"
    **Findings**: "Key clinical findings"
    """)

# Footer
st.markdown("---")
st.markdown("""
🏥 **Medical RAG Analyzer** - Amazon Bedrock + ChromaDB | Drag any PDF from your computer!
""")
