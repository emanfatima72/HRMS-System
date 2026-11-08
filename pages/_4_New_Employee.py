import streamlit as st
import datetime
import os
import pandas as pd
import re
import uuid
import base64
from PIL import Image
import io
from dotenv import load_dotenv
from backend.database import SessionLocal
from backend.models.employee import Employee
from utils.audit_logger import add_audit_log, get_current_user

load_dotenv()

def show():
    # ===== PAGE STYLING =====
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            }
            .main .block-container {
                padding-top: 1rem;
            }
            .page-title {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 5px;
            }
            .page-subtitle {
                color: #a0aec0;
                font-size: 14px;
                margin-bottom: 20px;
            }
            .section-card {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 20px 24px;
                margin-bottom: 20px;
            }
            .section-title {
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .section-title .step-badge {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 3px 14px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
            }
            .section-title .badge {
                font-size: 12px;
                font-weight: 400;
                color: #a0aec0;
                background: rgba(255,255,255,0.06);
                padding: 4px 14px;
                border-radius: 20px;
            }
            
            .extract-section {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                padding: 15px 18px;
                margin: 10px 0;
                border: 1px solid rgba(255,255,255,0.06);
            }
            .extract-section .extract-title {
                font-size: 14px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .extract-section .extract-title .badge {
                font-size: 10px;
                font-weight: 500;
                padding: 2px 12px;
                border-radius: 20px;
                background: rgba(102, 126, 234, 0.3);
                color: #a0aec0;
            }
            
            .skill-tag {
                display: inline-block;
                background: rgba(102, 126, 234, 0.2);
                color: #cbd5e0;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                margin: 3px 5px 3px 0;
                border: 1px solid rgba(102, 126, 234, 0.15);
            }
            
            .mandatory-warning {
                color: #ed8936;
                font-size: 14px;
                margin-bottom: 15px;
            }
            
            .upload-box {
                border: 2px dashed rgba(255,255,255,0.15);
                border-radius: 12px;
                padding: 25px;
                text-align: center;
                color: #a0aec0;
                transition: all 0.3s ease;
            }
            .upload-box:hover {
                border-color: rgba(102, 126, 234, 0.4);
                background: rgba(255,255,255,0.02);
            }
            .upload-box .icon {
                font-size: 40px;
                display: block;
                margin-bottom: 10px;
            }
            
            .edu-block {
                background: rgba(255,255,255,0.03);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
                border-left: 3px solid #667eea;
            }
            .edu-block.missing {
                border-left-color: #fc8181;
                background: rgba(252,129,129,0.05);
            }
            .edu-block.found {
                border-left-color: #48bb78;
                background: rgba(72,187,120,0.05);
            }
            .missing-label {
                color: #fc8181;
                font-size: 11px;
                font-weight: 500;
            }
            .found-label {
                color: #48bb78;
                font-size: 11px;
                font-weight: 500;
            }
            
            .status-pending {
                background: #ed8936;
                color: white;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                display: inline-block;
            }
            .status-rejected {
                background: #fc8181;
                color: white;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                display: inline-block;
            }
            
            .criminal-box {
                background: rgba(252,129,129,0.08);
                border: 1px solid rgba(252,129,129,0.2);
                border-radius: 8px;
                padding: 12px 16px;
                margin: 8px 0;
            }
            
            .found-highlight {
                color: #48bb78;
            }
            .missing-highlight {
                color: #fc8181;
            }
            
            .success-toast {
                background: rgba(72,187,120,0.15);
                border: 1px solid rgba(72,187,120,0.3);
                border-radius: 10px;
                padding: 12px 18px;
                color: #48bb78;
                text-align: center;
                margin: 10px 0 15px 0;
            }
            
            .profile-card {
                background: rgba(255,255,255,0.04);
                border-radius: 12px;
                padding: 12px 16px;
                border: 1px solid rgba(255,255,255,0.06);
                margin: 4px 0;
            }
            .profile-card .label {
                color: #a0aec0;
                font-size: 12px;
            }
            .profile-card .value {
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
            }
            
            .rejected-card {
                background: rgba(252,129,129,0.05);
                border: 1px solid rgba(252,129,129,0.15);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
            }
            .rejected-card .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-wrap: wrap;
            }
            .rejected-card .name {
                color: #ffffff;
                font-weight: 600;
                font-size: 16px;
            }
            .rejected-card .email {
                color: #a0aec0;
                font-size: 13px;
                margin-left: 10px;
            }
            .rejected-card .emp-id {
                color: #4a5568;
                font-size: 12px;
                margin-left: 10px;
            }
            .rejected-card .reason-box {
                background: rgba(252,129,129,0.05);
                border-radius: 6px;
                padding: 10px;
                margin-top: 8px;
            }
            .rejected-card .reason-label {
                color: #fc8181;
                font-weight: 600;
            }
            .rejected-card .reason-text {
                color: #cbd5e0;
            }
            .rejected-card .date {
                color: #4a5568;
                font-size: 12px;
                margin-top: 6px;
            }
            
            .photo-upload-area {
                background: rgba(255,255,255,0.02);
                border: 1px dashed rgba(255,255,255,0.15);
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                transition: all 0.3s ease;
            }
            .photo-upload-area:hover {
                border-color: rgba(102,126,234,0.4);
                background: rgba(255,255,255,0.04);
            }
            .photo-upload-area .upload-icon {
                font-size: 28px;
                margin-bottom: 4px;
            }
            .photo-upload-area .upload-hint {
                font-size: 11px;
                color: #4a5568;
            }
            
            .photo-preview-container {
                display: flex;
                justify-content: center;
                margin-top: 8px;
            }
            .photo-preview-container img {
                border-radius: 10px;
                border: 2px solid rgba(255,255,255,0.1);
                max-width: 180px;
            }
            .photo-success {
                color: #48bb78;
                font-size: 13px;
                text-align: center;
                margin-top: 4px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # ===== HEADER =====
    st.markdown("""
        <div class="page-title">New Employee Onboarding</div>
        <div class="page-subtitle">CV scanning, review, and approval workflow</div>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # DATABASE CONNECTION
    # ============================================================
    db = SessionLocal()
    
    def get_pending_employees():
        return db.query(Employee).filter(Employee.status == "Pending").all()
    
    def get_rejected_employees():
        return db.query(Employee).filter(Employee.status == "Rejected").all()
    
    def get_employee_by_email(email):
        return db.query(Employee).filter(Employee.email == email).first()
    
    def delete_employee_from_db(email):
        emp = db.query(Employee).filter(Employee.email == email).first()
        if emp:
            db.delete(emp)
            db.commit()
            return True
        return False
    
    def generate_employee_id():
        return f"EMP-{datetime.datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"
    
    # ============================================================
    # 🔥 FUNCTION TO ADD EMPLOYEE TO CURRENT EMPLOYEES SESSION
    # ============================================================
    def add_to_current_employees(emp):
        """Add approved employee to current employees session state"""
        if 'current_employees_data' not in st.session_state:
            st.session_state.current_employees_data = []
        
        # Check if already exists
        exists = any(e.get('Email') == emp.email for e in st.session_state.current_employees_data)
        if not exists:
            new_emp = {
                "Name": emp.name,
                "Email": emp.email,
                "Type": emp.employee_type or "Permanent",
                "Department": emp.department or "N/A",
                "Salary": emp.salary or 0,
                "Active Days": 0,
                "Extra Work (Hrs)": 0,
                "emp_id": emp.emp_id
            }
            st.session_state.current_employees_data.append(new_emp)
            return True
        return False
    
    # ============================================================
    # CV PARSING
    # ============================================================
    def parse_cv_fallback(file):
        try:
            from utils.cv_parser import parse_cv
            return parse_cv(file)
        except Exception as e:
            return None
    
    # ============================================================
    # HANDLE FORM CLEAR
    # ============================================================
    if 'clear_form' in st.session_state and st.session_state.clear_form:
        edu_keys = ["matric", "inter", "bachelor", "master", "phd"]
        for key in edu_keys:
            if f"edu_{key}" in st.session_state:
                st.session_state[f"edu_{key}"] = ""
        for i in range(1, 9):
            if f"skill_{i}" in st.session_state:
                st.session_state[f"skill_{i}"] = ""
        if 'additional_docs' in st.session_state:
            for doc in st.session_state.additional_docs:
                doc["uploaded"] = False
        st.session_state.clear_form = False
        st.rerun()
    
    # ============================================================
    # TABS
    # ============================================================
    tab1, tab2, tab3 = st.tabs(["Add New Employee", "On Vision (Pending)", "Rejected"])
    
    # ============================================================
    # TAB 1: ADD NEW EMPLOYEE
    # ============================================================
    with tab1:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    <span><span class="step-badge">Form</span> Fill Employee Details</span>
                    <span class="badge">CV Auto-Fill</span>
                </div>
        """, unsafe_allow_html=True)
        
        # CV Upload
        st.markdown("""
            <div class="upload-box" style="margin-bottom:15px;">
                <span class="icon">CV</span>
                Upload CV for auto-fill (PDF/DOCX)
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_cv = st.file_uploader("Upload CV", type=["pdf", "docx"], key="new_cv_upload", label_visibility="collapsed")
        
        parsed_data = None
        if uploaded_cv:
            with st.spinner("AI is scanning the CV..."):
                parsed_data = parse_cv_fallback(uploaded_cv)
                if parsed_data and "error" not in parsed_data:
                    st.success("CV parsed successfully! Form auto-filled below.")
                else:
                    st.info("Please fill the form manually. CV could not be parsed.")
        
        edu_keys = ["matric", "inter", "bachelor", "master", "phd"]
        
        if parsed_data and "education" in parsed_data:
            edu_data = parsed_data.get('education', {})
            for key in edu_keys:
                session_key = f"edu_{key}"
                value = edu_data.get(key, "")
                if value:
                    st.session_state[session_key] = value
        
        if parsed_data and "skills" in parsed_data:
            skills_list = parsed_data.get('skills', [])
            for i in range(1, 9):
                session_key = f"skill_{i}"
                if i <= len(skills_list) and skills_list[i-1]:
                    st.session_state[session_key] = skills_list[i-1]
        
        # ===== FORM =====
        with st.form("add_new_employee_form"):
            # Personal Information
            st.markdown("""
                <div class="extract-section">
                    <div class="extract-title">PERSONAL INFORMATION</div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *", 
                    value=parsed_data.get('first_name', '') if parsed_data else '', 
                    placeholder="Enter first name"
                )
                last_name = st.text_input("Last Name *", 
                    value=parsed_data.get('last_name', '') if parsed_data else '', 
                    placeholder="Enter last name"
                )
                email = st.text_input("Email *", 
                    value=parsed_data.get('email', '') if parsed_data else '', 
                    placeholder="email@example.com"
                )
                phone = st.text_input("Phone *", 
                    value=parsed_data.get('phone', '') if parsed_data else '', 
                    placeholder="0300-1234567"
                )
                address = st.text_input("Current Address", 
                    value=parsed_data.get('address', '') if parsed_data else '', 
                    placeholder="House, Street, City"
                )
            
            with col2:
                city = st.text_input("City / Country", 
                    value=parsed_data.get('city', '') if parsed_data else '', 
                    placeholder="Lahore, Pakistan"
                )
                linkedin = st.text_input("LinkedIn Profile", 
                    value=parsed_data.get('linkedin', '') if parsed_data else '', 
                    placeholder="linkedin.com/in/username"
                )
                github = st.text_input("GitHub Profile", 
                    value=parsed_data.get('github', '') if parsed_data else '', 
                    placeholder="github.com/username"
                )
                dob = st.date_input("Date of Birth", 
                    value=datetime.date(2000, 1, 1), 
                    max_value=datetime.date.today()
                )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Education
            st.markdown("""
                <div class="extract-section">
                    <div class="extract-title">EDUCATIONAL INFORMATION</div>
            """, unsafe_allow_html=True)
            
            edu_fields = [
                {"key": "matric", "label": "Matriculation / O-Levels", "placeholder": "Matriculation (Science) — M.H Sufi Foundation School"},
                {"key": "inter", "label": "Intermediate / A-Levels", "placeholder": "FSc Pre-Engineering — Punjab College"},
                {"key": "bachelor", "label": "Bachelor's Degree", "placeholder": "BS Computer Science — UET Lahore"},
                {"key": "master", "label": "Master's Degree", "placeholder": "MS Data Science — LUMS"},
                {"key": "phd", "label": "PhD / Doctorate", "placeholder": "PhD in AI — Stanford University"}
            ]
            
            for edu_field in edu_fields:
                key = edu_field["key"]
                session_key = f"edu_{key}"
                current_value = st.session_state.get(session_key, "")
                found = bool(current_value and current_value.strip())
                block_class = "edu-block found" if found else "edu-block missing"
                label_class = "found-label" if found else "missing-label"
                status_text = "Found" if found else "Missing"
                
                st.markdown(f'<div class="{block_class}">', unsafe_allow_html=True)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text_input(
                        edu_field["label"], 
                        value=current_value,
                        placeholder=edu_field["placeholder"], 
                        key=session_key
                    )
                with col2:
                    st.markdown(f'<div style="text-align:right;padding-top:6px;"><span class="{label_class}">{status_text}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Skills
            st.markdown("""
                <div class="extract-section">
                    <div class="extract-title">SKILLS</div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.text_input("Skill 1", value=st.session_state.get("skill_1", ""), placeholder="e.g., Python", key="skill_1")
                st.text_input("Skill 2", value=st.session_state.get("skill_2", ""), placeholder="e.g., React", key="skill_2")
            with col2:
                st.text_input("Skill 3", value=st.session_state.get("skill_3", ""), placeholder="e.g., Django", key="skill_3")
                st.text_input("Skill 4", value=st.session_state.get("skill_4", ""), placeholder="e.g., AWS", key="skill_4")
            with col3:
                st.text_input("Skill 5", value=st.session_state.get("skill_5", ""), placeholder="e.g., Docker", key="skill_5")
                st.text_input("Skill 6", value=st.session_state.get("skill_6", ""), placeholder="e.g., Git", key="skill_6")
            with col4:
                st.text_input("Skill 7", value=st.session_state.get("skill_7", ""), placeholder="e.g., Linux", key="skill_7")
                st.text_input("Skill 8", value=st.session_state.get("skill_8", ""), placeholder="e.g., SQL", key="skill_8")
            
            all_skills = [st.session_state.get(f"skill_{i}", "") for i in range(1, 9)]
            filtered_skills = [s.strip() for s in all_skills if s and s.strip()]
            
            if filtered_skills:
                st.markdown("""
                    <div style="margin-top:10px;">
                """, unsafe_allow_html=True)
                skills_html = ""
                for skill in filtered_skills[:20]:
                    skills_html += f'<span class="skill-tag">{skill}</span>'
                st.markdown(f"""
                    <div style="padding: 5px 0;">
                        {skills_html}
                    </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            if parsed_data:
                if parsed_data.get('total_experience'):
                    st.info(f"Total Experience: {parsed_data.get('total_experience')}")
                if parsed_data.get('companies'):
                    st.info(f"Companies: {', '.join(parsed_data.get('companies', []))}")
                if parsed_data.get('languages'):
                    st.info(f"Languages: {', '.join(parsed_data.get('languages', []))}")
            
            # ============================================================
            # STEP 3: MANDATORY DOCUMENTS (CLEAN UI - PHOTO PREVIEW ONLY)
            # ============================================================
            st.markdown("""
                <div class="extract-section">
                    <div class="extract-title">MANDATORY DOCUMENTS</div>
                    <div class="mandatory-warning">Compulsory: Upload 2 recent photographs</div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div style="color:#a0aec0;font-size:14px;margin-bottom:8px;">Photo 1</div>
                    <div class="photo-upload-area">
                        <div class="upload-icon">📷</div>
                        <div class="upload-hint">JPG, PNG, GIF, WEBP, JFIF, BMP</div>
                    </div>
                """, unsafe_allow_html=True)
                
                pic1 = st.file_uploader(
                    "Upload Photo 1", 
                    type=["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff", "ico", "jfif"], 
                    key="new_pic1",
                    label_visibility="collapsed"
                )
                
                if pic1:
                    try:
                        from PIL import Image
                        import io
                        image_data = pic1.getvalue()
                        image = Image.open(io.BytesIO(image_data))
                        
                        if image.mode in ('RGBA', 'LA', 'P'):
                            image = image.convert('RGB')
                        
                        st.markdown('<div class="photo-preview-container">', unsafe_allow_html=True)
                        st.image(image, caption=None, width=180, use_container_width=False)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.markdown(f"""
                            <div class="photo-success">✅ {pic1.name}</div>
                        """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div style="color:#a0aec0;font-size:14px;margin-bottom:8px;">Photo 2</div>
                    <div class="photo-upload-area">
                        <div class="upload-icon">📷</div>
                        <div class="upload-hint">JPG, PNG, GIF, WEBP, JFIF, BMP</div>
                    </div>
                """, unsafe_allow_html=True)
                
                pic2 = st.file_uploader(
                    "Upload Photo 2", 
                    type=["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff", "ico", "jfif"], 
                    key="new_pic2",
                    label_visibility="collapsed"
                )
                
                if pic2:
                    try:
                        from PIL import Image
                        import io
                        image_data = pic2.getvalue()
                        image = Image.open(io.BytesIO(image_data))
                        
                        if image.mode in ('RGBA', 'LA', 'P'):
                            image = image.convert('RGB')
                        
                        st.markdown('<div class="photo-preview-container">', unsafe_allow_html=True)
                        st.image(image, caption=None, width=180, use_container_width=False)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.markdown(f"""
                            <div class="photo-success">✅ {pic2.name}</div>
                        """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ============================================================
            # ADDITIONAL DOCUMENTS
            # ============================================================
            st.markdown("""
                <div class="extract-section">
                    <div class="extract-title">ADDITIONAL DOCUMENTS</div>
            """, unsafe_allow_html=True)
            
            if 'additional_docs' not in st.session_state:
                st.session_state.additional_docs = [
                    {"name": "CNIC Front", "uploaded": False},
                    {"name": "CNIC Back", "uploaded": False},
                    {"name": "Matric Certificate", "uploaded": False},
                    {"name": "Intermediate Certificate", "uploaded": False},
                    {"name": "University Degree", "uploaded": False}
                ]
            
            doc_names = [doc["name"] for doc in st.session_state.additional_docs]
            selected_doc = st.selectbox("Select Document Type", doc_names, key="new_doc_select")
            
            uploaded_doc = st.file_uploader(f"Upload {selected_doc}", type=["jpg", "png", "pdf"], key="new_doc_upload", label_visibility="collapsed")
            
            if uploaded_doc:
                if st.form_submit_button("Upload Document", use_container_width=True, key="new_doc_upload_btn"):
                    for doc in st.session_state.additional_docs:
                        if doc["name"] == selected_doc:
                            doc["uploaded"] = True
                            break
                    st.success(f"{selected_doc} uploaded successfully!")
                    st.rerun()
            
            uploaded_docs = [doc["name"] for doc in st.session_state.additional_docs if doc["uploaded"]]
            if uploaded_docs:
                st.markdown("""
                    <div style="margin-top:10px;">
                        <div style="color:#cbd5e0;font-size:13px;font-weight:600;margin-bottom:8px;">Uploaded Documents</div>
                """, unsafe_allow_html=True)
                cols = st.columns(3)
                for i, doc_name in enumerate(uploaded_docs):
                    with cols[i % 3]:
                        st.markdown(f"""
                            <div style="background:rgba(72,187,120,0.1);border:1px solid rgba(72,187,120,0.2);border-radius:8px;padding:8px 12px;margin-bottom:5px;display:flex;align-items:center;gap:8px;">
                                <span style="color:#48bb78;">✓</span>
                                <span style="color:#cbd5e0;font-size:12px;">{doc_name}</span>
                            </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="color:#4a5568;font-size:13px;padding:10px 0;">
                        No documents uploaded yet. Select a document type and upload.
                    </div>
                """, unsafe_allow_html=True)
            
            with st.expander("Add New Document Type"):
                new_doc_name = st.text_input("Document Name", placeholder="Experience Certificate", key="new_doc_name")
                if st.form_submit_button("Add Document Type", use_container_width=True):
                    if new_doc_name and new_doc_name not in [doc["name"] for doc in st.session_state.additional_docs]:
                        st.session_state.additional_docs.append({"name": new_doc_name, "uploaded": False})
                        st.success(f"Document type '{new_doc_name}' added!")
                        st.rerun()
                    elif new_doc_name in [doc["name"] for doc in st.session_state.additional_docs]:
                        st.error("Document type already exists!")
                    else:
                        st.error("Please enter a document name!")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ===== SUBMIT BUTTON =====
            st.markdown("---")
            submitted = st.form_submit_button("Submit for Review", use_container_width=True)
            
            # ===== SUCCESS MESSAGE =====
            if submitted:
                if first_name and email and phone and pic1 and pic2:
                    existing = get_employee_by_email(email)
                    if existing:
                        st.error(f"Employee with email {email} already exists in the system!")
                    else:
                        full_name = f"{first_name} {last_name}".strip() if last_name else first_name
                        emp_id = generate_employee_id()
                        
                        education_dict = {
                            "matric": st.session_state.get('edu_matric', ''),
                            "inter": st.session_state.get('edu_inter', ''),
                            "bachelor": st.session_state.get('edu_bachelor', ''),
                            "master": st.session_state.get('edu_master', ''),
                            "phd": st.session_state.get('edu_phd', '')
                        }
                        
                        skills = []
                        for i in range(1, 9):
                            skill = st.session_state.get(f'skill_{i}', '')
                            if skill and skill.strip():
                                skills.append(skill.strip())
                        
                        new_employee = Employee(
                            emp_id=emp_id,
                            name=full_name,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            phone=phone,
                            address=address,
                            city=city,
                            linkedin=linkedin,
                            github=github,
                            dob=dob.strftime("%Y-%m-%d"),
                            education=education_dict,
                            skills=skills,
                            cv_path=uploaded_cv.name if uploaded_cv else "",
                            photo1=pic1.name if pic1 else "",
                            photo2=pic2.name if pic2 else "",
                            additional_docs=uploaded_docs,
                            status="Pending",
                            submitted_on=datetime.datetime.now()
                        )
                        
                        db.add(new_employee)
                        db.commit()
                        
                        # 🔥 ADD AUDIT LOG
                        add_audit_log(
                            get_current_user(),
                            "Add New Employee",
                            f"Added new employee: {full_name} ({email}) - {emp_id}"
                        )
                        
                        st.session_state.clear_form = True
                        st.session_state.submission_success = True
                        st.session_state.submission_message = f"{full_name} (ID: {emp_id}) submitted for review!"
                        
                        st.rerun()
                else:
                    st.error("Please fill all required fields and upload 2 photos!")
        
        # ===== SUCCESS MESSAGE DISPLAY =====
        if 'submission_success' in st.session_state and st.session_state.submission_success:
            st.markdown(f"""
                <div class="success-toast">
                    {st.session_state.submission_message}
                </div>
            """, unsafe_allow_html=True)
            st.session_state.submission_success = False
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # TAB 2: ON VISION (PENDING) - WITH AUTO APPROVE TO CURRENT
    # ============================================================
    with tab2:
        pending_employees = get_pending_employees()
        
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    <span>On Vision - Pending Review</span>
                    <span class="badge">{len(pending_employees)} Pending</span>
                </div>
        """, unsafe_allow_html=True)
        
        if pending_employees:
            for emp in pending_employees:
                with st.expander(f"📋 {emp.emp_id} - {emp.name} ({emp.email})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                            **Personal Information**
                            - Employee ID: {emp.emp_id}
                            - Name: {emp.name}
                            - Email: {emp.email}
                            - Phone: {emp.phone}
                            - Address: {emp.address or 'Not provided'}
                            - City: {emp.city or 'Not provided'}
                            - LinkedIn: {emp.linkedin or 'Not provided'}
                            - GitHub: {emp.github or 'Not provided'}
                            - DOB: {emp.dob}
                        """)
                    
                    with col2:
                        st.markdown("**Education**")
                        edu_labels = {"matric": "Matric", "inter": "Inter", "bachelor": "Bachelor", "master": "Master", "phd": "PhD"}
                        if emp.education:
                            for key, label in edu_labels.items():
                                value = emp.education.get(key, '')
                                if value and value.strip():
                                    st.markdown(f'- {label}: <span class="found-highlight">✅ {value}</span>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'- {label}: <span class="missing-highlight">❌ Missing</span>', unsafe_allow_html=True)
                        else:
                            st.markdown("No education data available")
                        
                        if emp.skills and len(emp.skills) > 0:
                            skills_html = ""
                            for skill in emp.skills:
                                if skill and skill.strip():
                                    skills_html += f'<span class="skill-tag">{skill}</span>'
                            st.markdown(f"""
                                **Skills**
                                <div style="margin-top:4px;">{skills_html}</div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("**Skills:** No skills listed")
                    
                    st.markdown("---")
                    
                    # Criminal Record
                    st.markdown("""
                        <div class="criminal-box">
                            <strong style="color:#fc8181;">Criminal Record Check</strong>
                            <div style="color:#a0aec0;font-size:13px;margin-top:4px;">
                                Upload clearance certificate or police verification letter
                            </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        criminal_letter = st.file_uploader(
                            "Upload Criminal Record Clearance", 
                            type=["pdf", "jpg", "png"], 
                            key=f"criminal_{emp.id}",
                            label_visibility="collapsed"
                        )
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if criminal_letter:
                            if st.button("Upload Letter", key=f"criminal_btn_{emp.id}", use_container_width=True):
                                emp.criminal_letter = criminal_letter.name
                                db.commit()
                                st.success("Criminal record letter uploaded!")
                                st.rerun()
                    
                    if emp.criminal_letter:
                        st.markdown(f"""
                            <div style="color:#48bb78;font-size:12px;">
                                Letter uploaded: {emp.criminal_letter}
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div style="color:#4a5568;font-size:12px;">
                                No criminal record letter uploaded yet
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # ============================================================
                    # 🔥 APPROVE / REJECT - WITH AUTO ADD TO CURRENT EMPLOYEES
                    # ============================================================
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        with st.popover("Approve", use_container_width=True):
                            salary = st.number_input("Salary (PKR)", min_value=0, value=50000, step=1000, key=f"salary_{emp.id}")
                            employee_type = st.selectbox("Employee Type", ["Permanent", "Temporary", "Contract"], key=f"type_{emp.id}")
                            department = st.selectbox("Department", ["IT", "HR", "Marketing", "Finance", "Operations"], key=f"dept_{emp.id}")
                            joining_date = st.date_input("Joining Date", datetime.date.today(), key=f"join_{emp.id}")
                            
                            st.caption("Employee will be added to Current Employees")
                            if st.button("Confirm Approve", key=f"approve_{emp.id}"):
                                # Update employee status in database
                                emp.status = "Active"
                                emp.salary = salary
                                emp.employee_type = employee_type
                                emp.department = department
                                emp.joining_date = joining_date
                                emp.active_days = 0
                                emp.extra_work = 0
                                db.commit()
                                
                                # 🔥 AUDIT LOG - Approve Employee
                                add_audit_log(
                                    get_current_user(),
                                    "Approve Employee",
                                    f"Approved employee: {emp.name} ({emp.email}) - {department}"
                                )
                                
                                # 🔥 AUTO ADD TO CURRENT EMPLOYEES SESSION
                                add_to_current_employees(emp)
                                
                                st.success(f"{emp.name} approved and added to Current Employees!")
                                st.rerun()
                    
                    with col2:
                        with st.popover("Reject", use_container_width=True):
                            reject_reason = st.text_area("Reason for Rejection", placeholder="e.g., Documents incomplete", key=f"reason_{emp.id}")
                            st.caption("Employee will be moved to Rejected tab")
                            if st.button("Confirm Reject", key=f"reject_{emp.id}"):
                                if reject_reason:
                                    emp.status = "Rejected"
                                    emp.reject_reason = reject_reason
                                    emp.rejected_on = datetime.datetime.now()
                                    db.commit()
                                    
                                    # 🔥 AUDIT LOG - Reject Employee
                                    add_audit_log(
                                        get_current_user(),
                                        "Reject Employee",
                                        f"Rejected employee: {emp.name} ({emp.email}) - Reason: {reject_reason}"
                                    )
                                    
                                    st.success(f"{emp.name} rejected. Reason: {reject_reason}")
                                    st.rerun()
                                else:
                                    st.error("Please provide a reason for rejection!")
        else:
            st.info("No employees pending review. Submit new employees from the 'Add New Employee' tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================================
    # TAB 3: REJECTED
    # ============================================================
    with tab3:
        rejected_employees = get_rejected_employees()
        
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    <span>Rejected Employees</span>
                    <span class="badge">{len(rejected_employees)} Rejected</span>
                </div>
        """, unsafe_allow_html=True)
        
        if rejected_employees:
            for emp in rejected_employees:
                st.markdown(f"""
                    <div class="rejected-card">
                        <div class="header">
                            <div>
                                <span class="name">{emp.name}</span>
                                <span class="email">{emp.email}</span>
                                <span class="emp-id">ID: {emp.emp_id}</span>
                            </div>
                            <span class="status-rejected">Rejected</span>
                        </div>
                        <div class="reason-box">
                            <span class="reason-label">Reason:</span>
                            <span class="reason-text">{emp.reject_reason}</span>
                        </div>
                        <div class="date">
                            Rejected on: {emp.rejected_on.strftime('%Y-%m-%d %H:%M') if emp.rejected_on else 'N/A'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View", key=f"view_rejected_{emp.id}", use_container_width=True):
                        st.session_state.view_rejected = emp.id
                        st.rerun()
                
                with col2:
                    if st.button("Delete", key=f"delete_rejected_{emp.id}", use_container_width=True):
                        if delete_employee_from_db(emp.email):
                            if emp.email in st.session_state.employee_profiles:
                                del st.session_state.employee_profiles[emp.email]
                            st.success(f"{emp.name} deleted from rejected records!")
                            st.rerun()
                        else:
                            st.error("Failed to delete employee!")
                
                st.markdown("---")
                
                if st.session_state.get('view_rejected') == emp.id:
                    st.markdown(f"### Profile: {emp.name}")
                    
                    def get_download_link(file_name, file_display):
                        try:
                            file_path = os.path.join("uploads", file_name)
                            if os.path.exists(file_path):
                                with open(file_path, "rb") as f:
                                    data = f.read()
                                b64 = base64.b64encode(data).decode()
                                href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}" style="color:#667eea;text-decoration:underline;">📄 {file_display}</a>'
                                return href
                            else:
                                return f'<span style="color:#4a5568;">📄 {file_display} (file not found)</span>'
                        except:
                            return f'<span style="color:#4a5568;">📄 {file_display}</span>'
                    
                    salary_val = emp.salary or 0
                    salary_str = f"PKR {int(salary_val):,}" if salary_val else "PKR 0"
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            <div class="profile-card"><div class="label">Employee ID</div><div class="value">{emp.emp_id}</div></div>
                            <div class="profile-card"><div class="label">Full Name</div><div class="value">{emp.name}</div></div>
                            <div class="profile-card"><div class="label">Email</div><div class="value">{emp.email}</div></div>
                            <div class="profile-card"><div class="label">Phone</div><div class="value">{emp.phone or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">Address</div><div class="value">{emp.address or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">City</div><div class="value">{emp.city or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">LinkedIn</div><div class="value">{emp.linkedin or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">GitHub</div><div class="value">{emp.github or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">DOB</div><div class="value">{emp.dob or 'N/A'}</div></div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="profile-card"><div class="label">Department</div><div class="value">{emp.department or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">Employee Type</div><div class="value">{emp.employee_type or 'N/A'}</div></div>
                            <div class="profile-card"><div class="label">Salary</div><div class="value">{salary_str}</div></div>
                            <div class="profile-card"><div class="label">Status</div><div class="value"><span class="status-rejected">Rejected</span></div></div>
                            <div class="profile-card"><div class="label">Rejected Reason</div><div class="value">{emp.reject_reason}</div></div>
                            <div class="profile-card"><div class="label">Rejected On</div><div class="value">{emp.rejected_on.strftime('%Y-%m-%d %H:%M') if emp.rejected_on else 'N/A'}</div></div>
                        """, unsafe_allow_html=True)
                    
                    # Education
                    if emp.education:
                        st.markdown("### Education")
                        edu_labels = {"matric": "Matric", "inter": "Inter", "bachelor": "Bachelor", "master": "Master", "phd": "PhD"}
                        for key, label in edu_labels.items():
                            value = emp.education.get(key, '')
                            if value:
                                st.markdown(f"- **{label}:** {value}")
                    
                    # Skills
                    if emp.skills and len(emp.skills) > 0:
                        st.markdown("### Skills")
                        skills_html = ""
                        for skill in emp.skills:
                            if skill and skill.strip():
                                skills_html += f'<span class="skill-tag">{skill}</span>'
                        st.markdown(skills_html, unsafe_allow_html=True)
                    
                    # Documents
                    st.markdown("### Documents")
                    if emp.cv_path:
                        st.markdown(get_download_link(emp.cv_path, f"CV: {emp.cv_path}"), unsafe_allow_html=True)
                    if emp.photo1:
                        st.markdown(get_download_link(emp.photo1, f"Photo 1: {emp.photo1}"), unsafe_allow_html=True)
                    if emp.photo2:
                        st.markdown(get_download_link(emp.photo2, f"Photo 2: {emp.photo2}"), unsafe_allow_html=True)
                    if emp.criminal_letter:
                        st.markdown(get_download_link(emp.criminal_letter, f"Criminal Letter: {emp.criminal_letter}"), unsafe_allow_html=True)
                    if emp.additional_docs:
                        for doc in emp.additional_docs:
                            st.markdown(get_download_link(doc, f"Document: {doc}"), unsafe_allow_html=True)
                    
                    if st.button("Close Profile", use_container_width=True, key=f"close_rejected_view_{emp.id}"):
                        st.session_state.view_rejected = None
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("No rejected employees yet.")
        
        if rejected_employees:
            if st.button("Clear All Rejected Records", use_container_width=True):
                for emp in rejected_employees:
                    delete_employee_from_db(emp.email)
                st.success("All rejected records cleared!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    db.close()