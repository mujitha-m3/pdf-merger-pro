import streamlit as st
import PyPDF2
import io
import os
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="PDF Merger Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main { padding: 2rem; }
    .premium-badge { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .free-badge {
        background: #e0e0e0;
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'premium_key' not in st.session_state:
    st.session_state.premium_key = None
if 'is_premium' not in st.session_state:
    st.session_state.is_premium = False
if 'files_merged_today' not in st.session_state:
    st.session_state.files_merged_today = 0

FREE_FILE_LIMIT = 5  # Free users can merge up to 5 files
PREMIUM_FILE_LIMIT = 100  # Premium users can merge up to 100 files

# Valid premium keys (in production, use a database)
VALID_PREMIUM_KEYS = {
    "PREMIUM2026": {"email": "premium_user@example.com", "valid_until": "2026-12-31"},
    # Add more keys as needed
}

def verify_premium_key(key):
    """Verify premium key"""
    if key in VALID_PREMIUM_KEYS:
        return True
    return False

def merge_pdfs(files):
    """Merge multiple PDF files"""
    try:
        merger = PyPDF2.PdfMerger()
        
        for uploaded_file in files:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            # Create a file-like object
            merger.append(uploaded_file)
        
        # Write to bytes
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Error merging PDFs: {str(e)}")
        return None

# Sidebar
with st.sidebar:
    st.title("🔐 Account")
    
    # Premium status
    if st.session_state.is_premium:
        st.markdown('<div class="premium-badge">✨ PREMIUM</div>', unsafe_allow_html=True)
        st.success("Premium features unlocked!")
    else:
        st.markdown('<div class="free-badge">FREE</div>', unsafe_allow_html=True)
        st.info(f"Files merged today: {st.session_state.files_merged_today}/{FREE_FILE_LIMIT}")
    
    st.divider()
    
    # Premium key input
    st.subheader("Unlock Premium")
    premium_key = st.text_input("Enter Premium Key", type="password")
    
    if st.button("Activate Premium"):
        if premium_key and verify_premium_key(premium_key):
            st.session_state.is_premium = True
            st.session_state.premium_key = premium_key
            st.success("🎉 Premium activated!")
            st.rerun()
        elif premium_key:
            st.error("Invalid premium key")
    
    st.divider()
    
    # Pricing
    st.subheader("💰 Pricing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Free**
        - Merge up to 5 files
        - Basic features
        - File size limit
        """)
    
    with col2:
        st.markdown("""
        **Premium**
        - Merge up to 100 files
        - Priority support
        - No file limits
        """)
    
    st.divider()
    
    # Contact/Buy
    st.markdown("""
    ### Get Premium Key
    💌 [Contact us](mailto:your-email@example.com)
    🛒 [Buy now](https://your-payment-link.com)
    """)
    
    st.divider()
    st.caption("Made with ❤️ by Your Team")

# Main content
st.title("📄 PDF Merger Pro")
st.markdown("Merge your PDF files easily and quickly!")

# Check file limits
file_limit = PREMIUM_FILE_LIMIT if st.session_state.is_premium else FREE_FILE_LIMIT

col1, col2, col3 = st.columns(3)

with col1:
    if st.session_state.is_premium:
        st.metric("Your Plan", "Premium ✨", "Unlimited files")
    else:
        remaining = FREE_FILE_LIMIT - st.session_state.files_merged_today
        st.metric("Your Plan", "Free", f"{remaining} merges left today")

with col2:
    st.metric("File Limit", f"{file_limit} files", "per merge")

with col3:
    if not st.session_state.is_premium:
        st.info("🚀 [Upgrade to Premium](https://your-payment-link.com)")

st.divider()

# Main upload area
st.subheader("📤 Upload PDF Files")
st.info("👇 Upload multiple PDF files below and click 'Merge PDFs'")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type="pdf",
    accept_multiple_files=True,
    key="pdf_uploader"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) selected")
    
    # Check file limit
    if len(uploaded_files) > file_limit:
        st.error(f"❌ You can only merge up to {file_limit} files. {len(uploaded_files)} files selected.")
        if not st.session_state.is_premium:
            st.warning(f"💡 Upgrade to Premium to merge up to {PREMIUM_FILE_LIMIT} files!")
    else:
        # Display file list
        with st.expander("View selected files"):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size / 1024:.1f} KB)")
        
        # Merge button
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            output_name = st.text_input(
                "Output filename",
                value="merged_document.pdf",
                help="Name for your merged PDF"
            )
        
        with col2:
            merge_button = st.button("🔗 Merge PDFs", use_container_width=True, type="primary")
        
        if merge_button:
            if not output_name.endswith('.pdf'):
                output_name += '.pdf'
            
            with st.spinner("🔄 Merging PDFs..."):
                merged_pdf = merge_pdfs(uploaded_files)
            
            if merged_pdf:
                st.success("✅ PDFs merged successfully!")
                
                # Update counter
                st.session_state.files_merged_today += 1
                
                # Download button
                st.download_button(
                    label="📥 Download Merged PDF",
                    data=merged_pdf,
                    file_name=output_name,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                # Show file info
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"📊 Output size: {len(merged_pdf.getvalue()) / 1024:.1f} KB")
                with col2:
                    st.info(f"📄 Total pages merged: {len(uploaded_files)}")

st.divider()

# Features section
st.subheader("✨ Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🚀 Fast
    Merge PDFs in seconds
    """)

with col2:
    st.markdown("""
    ### 🔒 Secure
    Files deleted after download
    """)

with col3:
    st.markdown("""
    ### 📱 Online
    Works on any device
    """)

st.divider()

# FAQ Section
with st.expander("❓ Frequently Asked Questions"):
    st.markdown("""
    **Q: Are my files safe?**
    
    A: Yes! Your files are processed in memory and deleted immediately after you download the merged PDF. We don't store anything on our servers.
    
    **Q: How many files can I merge?**
    
    A: Free users can merge up to 5 files per operation. Premium members can merge up to 100 files.
    
    **Q: What's the file size limit?**
    
    A: Free: 50MB total. Premium: 500MB total per merge.
    
    **Q: Can I merge scanned PDFs?**
    
    A: Yes! We support all PDF types including scanned documents.
    
    **Q: How do I get a premium key?**
    
    A: Contact us at your-email@example.com or visit our payment page.
    """)

st.divider()

# Footer
st.markdown("""
<hr>
<p style="text-align: center;">
    Made with ❤️ | 
    <a href="mailto:your-email@example.com">Contact</a> | 
    <a href="https://your-privacy-policy.com">Privacy</a>
</p>
""", unsafe_allow_html=True)
