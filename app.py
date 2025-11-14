"""Smart Document Finder - Simple, clean search interface."""

import streamlit as st
from model import extract_text, chunk_text, build_index, search, CONFIG, estimate_page
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def highlight_query(text: str, query: str) -> str:
    """Highlight query words in text with yellow background."""
    try:
        # Split query into words and highlight each one
        words = query.split()
        highlighted = text
        
        for word in words:
            if word.strip():
                # Case-insensitive highlighting
                pattern = re.compile(f'({re.escape(word)})', re.IGNORECASE)
                highlighted = pattern.sub(
                    r'<mark style="background-color: #ffff00; font-weight: bold;">\1</mark>',
                    highlighted
                )
        return highlighted
    except:
        return text


def format_export_text(results: list, query: str, file_names: list) -> str:
    """Format results as plain text for export."""
    lines = [
        "=" * 80,
        "SMART DOCUMENT FINDER - SEARCH RESULTS",
        "=" * 80,
        f"Query: {query}",
        f"Results: {len(results)}",
        f"Files: {', '.join(file_names)}",
        f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 80,
        ""
    ]
    
    for i, (text, score) in enumerate(results, 1):
        confidence = int(score * 100)
        lines.extend([
            f"RESULT {i}",
            f"Confidence: {confidence}%",
            f"Score: {score:.4f}",
            "-" * 80,
            text,
            "-" * 80,
            ""
        ])
    
    return "\n".join(lines)


def format_export_markdown(results: list, query: str, file_names: list) -> str:
    """Format results as Markdown for export."""
    lines = [
        "# Search Results",
        f"**Query:** `{query}`",
        f"**Results:** {len(results)}",
        f"**Files:** {', '.join(file_names)}",
        f"**Generated:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    
    for i, (text, score) in enumerate(results, 1):
        confidence = int(score * 100)
        lines.extend([
            f"## Result {i}",
            f"- **Confidence:** {confidence}%",
            f"- **Score:** {score:.4f}",
            "",
            f"```",
            text,
            f"```",
            ""
        ])
    
    return "\n".join(lines)

# Page config
st.set_page_config(page_title="Smart Document Finder", page_icon="📚", layout="wide")

st.title("📚 Smart Document Finder")
st.markdown("Upload documents and search with natural language. Fast, simple, effective.")

# ============================================================================
# FILE UPLOAD
# ============================================================================

uploaded_files = st.file_uploader(
    "Upload documents (PDF, DOCX, TXT)", 
    type=["pdf", "docx", "txt"], 
    accept_multiple_files=True
)

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "last_files" not in st.session_state:
    st.session_state.last_files = None
if "index" not in st.session_state:
    st.session_state.index = None
if "chunks" not in st.session_state:
    st.session_state.chunks = None

# Extract text when files change
if uploaded_files and uploaded_files != st.session_state.last_files:
    st.session_state.last_files = uploaded_files
    
    all_text = ""
    file_names = []
    
    with st.spinner("Extracting text..."):
        for file in uploaded_files:
            text = extract_text(file, file.name)
            if text:
                all_text += text + "\n"
                file_names.append(file.name)
        
        st.session_state.extracted_text = {
            "text": all_text,
            "files": file_names,
            "char_count": len(all_text)
        }
    
    st.success(f"✅ Extracted {len(all_text):,} chars from {len(file_names)} file(s)")

# ============================================================================
# SEARCH
# ============================================================================

if st.session_state.extracted_text:
    full_text = st.session_state.extracted_text["text"]
    file_names = st.session_state.extracted_text["files"]
    
    # Config sliders
    col1, col2, col3 = st.columns(3)
    with col1:
        chunk_size = st.slider("Chunk Size", 300, 1500, CONFIG["CHUNK_SIZE"], 50)
    with col2:
        overlap = st.slider("Overlap", 0, 200, CONFIG["OVERLAP"], 10)
    with col3:
        k = st.slider("Results", 1, 10, CONFIG["K"])
    
    # Check if config changed or first time
    config_key = (chunk_size, overlap)
    if "config_key" not in st.session_state:
        st.session_state.config_key = config_key
    
    # Build index ONLY if config changed or index doesn't exist
    if st.session_state.config_key != config_key or st.session_state.index is None:
        st.session_state.config_key = config_key
        
        with st.spinner("Building search index..."):
            st.session_state.chunks = chunk_text(full_text, chunk_size, overlap)
            st.session_state.index = build_index(st.session_state.chunks)
            st.success(f"✅ Index ready ({len(st.session_state.chunks)} chunks, built in {st.session_state.index['time']:.2f}s)")
    
    # Use cached index and chunks
    chunks = st.session_state.chunks
    index = st.session_state.index
    
    # Search
    st.subheader("🔍 Search")
    query = st.text_input("What are you looking for?", placeholder="e.g., data visualization, storytelling")
    
    if query:
        results = search(query, index, k)
        
        if results:
            st.subheader(f"📋 Results ({len(results)})")
            
            for i, (text, score) in enumerate(results, 1):
                confidence = int(score * 100)
                page = estimate_page(text, full_text)
                
                # Color-coded badge - adjusted for better model
                if confidence >= 80:
                    color = "#10b981"  # Green - excellent match
                elif confidence >= 60:
                    color = "#3b82f6"  # Blue - good match
                elif confidence >= 40:
                    color = "#f59e0b"  # Amber - decent match
                else:
                    color = "#ef4444"  # Red - weak match
                
                # Highlight query in result
                highlighted_text = highlight_query(text[:600], query)
                
                st.markdown(f"""
                <div style="background: #f8fafc; border-left: 5px solid {color}; padding: 16px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <h4 style="margin: 0; color: #1f2937;">Result {i}</h4>
                        <span style="background: {color}; color: white; padding: 6px 14px; border-radius: 20px; font-weight: bold; font-size: 0.9em;">{confidence}% Match</span>
                    </div>
                    <div style="color: #666; font-size: 0.85em; margin-bottom: 12px; display: flex; gap: 16px;">
                        <span>📄 {file_names[0] if len(file_names) == 1 else 'Multiple files'}</span>
                        <span>📖 Page ~{page}</span>
                        <span>⚡ Score: {score:.3f}</span>
                    </div>
                    <div style="color: #1f2937; line-height: 1.7; background: white; padding: 12px; border-radius: 6px; font-family: 'Segoe UI', sans-serif; font-size: 0.95em; border: 1px solid #e5e7eb;">
                        {highlighted_text}{'<span style="color: #999;">...</span>' if len(text) > 600 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No results found. Try different keywords.")
        
        # Export section
        st.divider()
        st.subheader("💾 Export Results")
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            txt_export = format_export_text(results, query, file_names)
            st.download_button(
                label="📥 Download as TXT",
                data=txt_export,
                file_name=f"search_results_{query.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with export_col2:
            md_export = format_export_markdown(results, query, file_names)
            st.download_button(
                label="📥 Download as Markdown",
                data=md_export,
                file_name=f"search_results_{query.replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
