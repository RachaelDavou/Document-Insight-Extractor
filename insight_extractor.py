import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from pydantic import BaseModel, Field
from typing import List
import os
import tempfile
import requests


OPENAI_API_KEY = "your-openai-api-key-here"
st.set_page_config(page_title="Document Insight Extractor", layout="wide")

# Sample documents from GitHub (verified working URLs)
SAMPLE_DOCS = {
    "State of the Union": "https://raw.githubusercontent.com/hwchase17/chroma-langchain/master/state_of_the_union.txt",
    "Paul Graham Essay": "https://raw.githubusercontent.com/gkamradt/langchain-tutorials/main/data/PaulGrahamEssays/startupideas.txt",
}


# Insights extracted from the document
class DocumentInsights(BaseModel):
    title: str = Field(description="The title or main topic of the document")
    document_type: str = Field(description="Type of document: article, report, letter, memo, research paper, etc.")
    summary: str = Field(description="A 3-4 sentence summary of the document")
    key_points: List[str] = Field(description="List of 3-5 main points or takeaways")
    entities: List[str] = Field(description="Important names, organizations, or places mentioned")
    dates: List[str] = Field(description="Any dates or time periods mentioned")
   

# Initialize LLM
@st.cache_resource
def get_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=OPENAI_API_KEY
    )


# Tool: Document Loader (file upload)
# Load document content using appropriate loader
def load_document(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    if uploaded_file.name.endswith(".pdf"):
        loader = PyPDFLoader(tmp_path)
        pages = loader.load()
        content = "\n\n".join([page.page_content for page in pages])
        metadata = {"source": uploaded_file.name, "pages": len(pages), "type": "pdf"}
    else:
        loader = TextLoader(tmp_path)
        docs = loader.load()
        content = docs[0].page_content
        metadata = {"source": uploaded_file.name, "type": "txt"}
    
    os.unlink(tmp_path)
    
    return content, metadata


# Tool: GitHub Document Fetcher
# Fetch document content from GitHub raw URL
def fetch_from_github(url: str):    
    response = requests.get(url)
    response.raise_for_status()
    content = response.text
    
    filename = url.split("/")[-1]
    metadata = {"source": url, "filename": filename, "type": "github"}
    
    return content, metadata


# Tool: Insight Extractor with output

def extract_insights(content: str, llm) -> DocumentInsights:    
    structured_llm = llm.with_structured_output(DocumentInsights)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert document analyst. Extract structured insights from the provided document.
Be thorough but concise. If a field doesn't apply, use an empty list or 'N/A'."""),
        ("user", "Extract insights from this document:\n\n{content}")
    ])
    
    chain = prompt | structured_llm
    
    return chain.invoke({"content": content})


# Helper to display results
def display_results(insights, source_caption=None):
    st.divider()
    st.subheader("Extracted Insights")
    if source_caption:
        st.caption(f"Source: {source_caption}")
    
    # Display fields
    st.markdown(f"**Title:** {insights.title}")
    st.markdown(f"**Document Type:** {insights.document_type}")
    st.markdown(f"**Entities:** {', '.join(insights.entities) if insights.entities else 'None found'}")
    st.markdown(f"**Dates Mentioned:** {', '.join(insights.dates) if insights.dates else 'None found'}")
    
    st.markdown("")
    
    # Summary of the document
    st.markdown("**Summary:**")
    st.write(insights.summary)

    # Key points as bullet list
    st.markdown("**Key Points:**")
    for point in insights.key_points:
        st.write(f"• {point}")
    


# Main UI
st.title("Document Insight Extractor")
st.caption("Extract structured insights from documents using AI tools")

st.divider()

# Initialize session state
if "input_source" not in st.session_state:
    st.session_state.input_source = None
if "insights" not in st.session_state:
    st.session_state.insights = None
if "source_url" not in st.session_state:
    st.session_state.source_url = None

# Two input options
tab1, tab2 = st.tabs(["Load Sample from GitHub", "Upload Document"])

with tab1:
    st.markdown("Select a sample document from GitHub:")
    selected_sample = st.selectbox(
        "Choose a sample",
        options=list(SAMPLE_DOCS.keys()),
        label_visibility="collapsed"
    )
    
    if st.button("Load Sample", use_container_width=True):
        st.session_state.input_source = "github"
        st.session_state.source_url = SAMPLE_DOCS[selected_sample]
        
        llm = get_llm()
        url = SAMPLE_DOCS[selected_sample]
        
        with st.status("Processing document from GitHub", expanded=True) as status:
            st.write("Running: GitHub Fetcher Tool")
            try:
                content, metadata = fetch_from_github(url)
                st.write("✓ Fetched sample document from GitHub")
            except Exception as e:
                st.error(f"Error fetching document: {e}")
                st.stop()
            
            max_chars = 12000
            if len(content) > max_chars:
                content = content[:max_chars]
            
            st.write("Running: Insight Extractor Tool")
            try:
                st.session_state.insights = extract_insights(content, llm)
                st.write("✓ Extracted insights")
            except Exception as e:
                st.error(f"Error extracting insights: {e}")
                st.stop()
            
            status.update(label="Extraction complete!", state="complete")    
    
    
with tab2:
    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt"],
        help="Supported formats: PDF, TXT"
    )
    
    if uploaded_file:
        if st.button("Extract Insights", use_container_width=True, key="upload_btn"):
            st.session_state.input_source = "upload"
            st.session_state.source_url = None
            
            llm = get_llm()
            
            with st.status("Processing document", expanded=True) as status:
                st.write("Running: Document Loader Tool")
                try:
                    content, metadata = load_document(uploaded_file)
                    st.write("✓ Successfully loaded document")
                except Exception as e:
                    st.error(f"Error loading document: {e}")
                    st.stop()
                
                max_chars = 12000
                if len(content) > max_chars:
                    content = content[:max_chars]
                
                st.write("Running: Insight Extractor Tool")
                try:
                    st.session_state.insights = extract_insights(content, llm)
                    st.write("✓ Extracted insights")
                except Exception as e:
                    st.error(f"Error extracting insights: {e}")
                    st.stop()
                
                status.update(label="Extraction complete!", state="complete")


# Display results
if st.session_state.insights:
    if st.session_state.input_source == "github":
        display_results(st.session_state.insights, st.session_state.source_url)
    else:
        display_results(st.session_state.insights)
else:
    st.info("Upload a document or load a sample from GitHub to get started")
    
    st.markdown("### What Gets Extracted")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **Title** - Main topic
        - **Document Type** - Article, report, memo, etc.
        - **Summary** - Brief overview
        - **Key Points** - Main takeaways
        """)
    
    with col2:
        st.markdown("""
        - **Entities** - Names, organizations, places
        - **Dates** - Time references
        """)