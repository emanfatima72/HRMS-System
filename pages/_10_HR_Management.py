import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import uuid
import re
import tempfile
from dotenv import load_dotenv
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.employee import Employee
from utils.audit_logger import add_audit_log, get_current_user
import bcrypt
from PIL import Image
import io
import json

load_dotenv()

# ============================================================
# CV PARSING FUNCTION
# ============================================================
def parse_cv_text(text):
    data = {
        "first_name": "",
        "last_name": "",
        "email": "",
        "phone": "",
        "city": "",
        "linkedin": "",
        "github": "",
        "designation": "",
        "education": {
            "matric": "",
            "inter": "",
            "bachelor": "",
            "master": "",
            "phd": ""
        },
        "skills": [],
        "experience": [],
        "companies": [],
        "total_experience": "",
        "languages": []
    }
    
    lines = text.split('\n')
    text_lower = text.lower()
    
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        data["email"] = email_match.group(0)
    
    phone_patterns = [
        r'(?:\+92|0092)[\s\-]?3[0-9]{2}[\s\-]?[0-9]{7}',
        r'03[0-9]{2}[\s\-]?[0-9]{7}',
        r'03[0-9]{9}',
        r'3[0-9]{2}[\s\-]?[0-9]{7}',
        r'\+92[0-9]{10}',
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone_found = phone_match.group(0)
            phone_found = re.sub(r'[\s\-\(\)]', '', phone_found)
            if phone_found.startswith('3'):
                phone_found = '0' + phone_found
            data["phone"] = phone_found
            break
    
    linkedin_match = re.search(r'linkedin\.com/in/[A-Za-z0-9\-_]+', text_lower)
    if linkedin_match:
        data["linkedin"] = "linkedin.com/in/" + linkedin_match.group(0).split('/')[-1]
    
    github_match = re.search(r'github\.com/[A-Za-z0-9\-_]+', text_lower)
    if github_match:
        data["github"] = "github.com/" + github_match.group(0).split('/')[-1]
    
    designation_keywords = ['hr', 'human resource', 'recruiter', 'talent acquisition', 'payroll', 'training', 'people', 'employee']
    for line in lines[:20]:
        line_lower = line.lower()
        if any(kw in line_lower for kw in designation_keywords):
            if 'summary' not in line_lower and 'profile' not in line_lower:
                words = line.split()
                if 1 <= len(words) <= 6:
                    data["designation"] = line.strip()[:100]
                    break
    
    name_found = False
    for line in lines[:15]:
        line_clean = line.strip()
        if not line_clean:
            continue
        skip_keywords = ['email', 'phone', 'contact', 'address', 'linkedin', 'github', 
                       'summary', 'profile', 'objective', 'education', 'skills']
        if any(kw in line_clean.lower() for kw in skip_keywords):
            continue
        words = line_clean.split()
        if 1 <= len(words) <= 5 and len(line_clean) < 50:
            if line_clean[0].isupper() or any(c.isupper() for c in line_clean):
                name_parts = line_clean.split()
                data["first_name"] = name_parts[0] if name_parts else ""
                data["last_name"] = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
                name_found = True
                break
    
    if not name_found and lines:
        first_line = lines[0].strip()
        if first_line and len(first_line.split()) <= 5 and len(first_line) < 40:
            name_parts = first_line.split()
            data["first_name"] = name_parts[0] if name_parts else ""
            data["last_name"] = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
    
    city_match = re.search(r'(?:based in|location|city)[:\s]+([A-Za-z\s,]+)', text_lower)
    if city_match:
        data["city"] = city_match.group(1).strip().title()
    
    education_data = {
        "matric": "",
        "inter": "",
        "bachelor": "",
        "master": "",
        "phd": ""
    }
    
    edu_keywords = {
        "matric": ['matric', 'matriculation', 'secondary school', 'ssc', 'o-level', 'o levels', 'high school', '10th', '10 class'],
        "inter": ['inter', 'intermediate', 'fsc', 'f.sc', 'hsc', 'higher secondary', 'a-level', 'a levels', '12th', '12 class'],
        "bachelor": ['bs', 'bsc', 'ba', 'bcs', 'b.tech', 'b.com', 'bba', 'bachelor', 'undergraduate', 'b.e', 'b.s', 'bscs', 'bcs', 'hons', 'honours'],
        "master": ['ms', 'msc', 'ma', 'mcs', 'm.tech', 'm.com', 'mba', 'master', 'postgraduate', 'm.sc'],
        "phd": ['phd', 'ph.d', 'doctorate', 'd.phil', 'doctoral']
    }
    
    education_lines = []
    in_education_section = False
    
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            continue
        line_lower = line_clean.lower()
        
        if any(kw in line_lower for kw in ['education', 'academic qualification', 'educational qualification']):
            in_education_section = True
            continue
        
        if in_education_section:
            if any(kw in line_lower for kw in ['skills', 'experience', 'work experience', 'projects', 'certifications', 'achievements', 'languages', 'professional']):
                break
        
        if in_education_section:
            has_edu_keyword = False
            for level, keywords in edu_keywords.items():
                if any(kw in line_lower for kw in keywords):
                    has_edu_keyword = True
                    break
            has_year = re.search(r'\b(19|20)\d{2}\b', line_clean)
            if has_edu_keyword or has_year:
                cleaned = re.sub(r'^[•\-*0-9.)]+\s*', '', line_clean)
                if cleaned and len(cleaned) > 3:
                    education_lines.append(cleaned)
    
    if not education_lines:
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            line_lower = line_clean.lower()
            for level, keywords in edu_keywords.items():
                if any(kw in line_lower for kw in keywords):
                    if not any(section in line_lower for section in ['skills', 'experience', 'summary', 'profile']):
                        cleaned = re.sub(r'^[•\-*0-9.)]+\s*', '', line_clean)
                        if cleaned and len(cleaned) > 3:
                            education_lines.append(cleaned)
                        break
    
    for edu_line in education_lines:
        edu_lower = edu_line.lower()
        assigned = False
        for level, keywords in edu_keywords.items():
            if any(kw in edu_lower for kw in keywords):
                if not education_data[level]:
                    cleaned = re.sub(r'^[•\-*0-9.)]+\s*', '', edu_line)
                    education_data[level] = cleaned
                    assigned = True
                    break
        
        if not assigned:
            if 'bs' in edu_lower or 'bsc' in edu_lower or 'bachelor' in edu_lower or 'hons' in edu_lower:
                if not education_data["bachelor"]:
                    education_data["bachelor"] = edu_line
            elif 'ms' in edu_lower or 'msc' in edu_lower or 'master' in edu_lower:
                if not education_data["master"]:
                    education_data["master"] = edu_line
            elif 'phd' in edu_lower or 'doctorate' in edu_lower:
                if not education_data["phd"]:
                    education_data["phd"] = edu_line
            elif 'fsc' in edu_lower or 'inter' in edu_lower or 'a-level' in edu_lower:
                if not education_data["inter"]:
                    education_data["inter"] = edu_line
            elif 'matric' in edu_lower or 'o-level' in edu_lower:
                if not education_data["matric"]:
                    education_data["matric"] = edu_line
    
    data["education"] = education_data
    
    skills_found = []
    
    all_skills = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift', 'Kotlin', 'SQL', 'HTML', 'CSS',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel', 'WordPress', 'Bootstrap', 'Tailwind',
        'Machine Learning', 'Deep Learning', 'AI', 'Artificial Intelligence', 'CNN', 'NLP', 'Computer Vision', 
        'TensorFlow', 'PyTorch', 'Scikit-learn', 'Keras', 'OpenCV',
        'Data Analysis', 'Data Science', 'Pandas', 'NumPy', 'Tableau', 'Power BI', 'Excel', 'Matplotlib', 'Seaborn',
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD', 'Terraform',
        'Cybersecurity', 'Kali Linux', 'Nmap', 'Metasploit', 'Penetration Testing', 'Ethical Hacking', 'OWASP',
        'Git', 'Linux', 'VS Code', 'PyCharm', 'Jupyter', 'Selenium', 'MS Office', 'Google Workspace', 'Figma',
        'Communication', 'Problem Solving', 'Teamwork', 'Leadership', 'Time Management',
        'SEO', 'Content Writing', 'Plugin Management', 'Networking', 'Cisco', 'Packet Tracer',
        'Recruitment', 'Payroll', 'Training', 'Employee Relations', 'HR Policies', 'Talent Acquisition'
    ]
    
    in_skills_section = False
    skill_lines = []
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_lower = line_clean.lower()
        
        if any(kw in line_lower for kw in ['skills', 'technical skills', 'core competencies']):
            in_skills_section = True
            continue
        
        if in_skills_section:
            if any(kw in line_lower for kw in ['education', 'experience', 'work experience', 'projects', 'certifications', 'achievements', 'languages']):
                break
            skill_lines.append(line_clean)
    
    for line in skill_lines:
        line_lower = line.lower()
        for skill in all_skills:
            if skill.lower() in line_lower:
                if skill not in skills_found:
                    skills_found.append(skill)
    
    if not skills_found:
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            line_lower = line_clean.lower()
            if any(section in line_lower for section in ['education', 'experience', 'summary', 'profile']):
                continue
            for skill in all_skills:
                if skill.lower() in line_lower:
                    if skill not in skills_found:
                        skills_found.append(skill)
    
    skills_found = list(set(skills_found))[:8]
    data["skills"] = skills_found
    
    experience = []
    companies = []
    in_experience_section = False
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_lower = line_clean.lower()
        
        if any(kw in line_lower for kw in ['experience', 'work experience', 'professional experience', 'employment']):
            in_experience_section = True
            continue
        
        if in_experience_section and any(kw in line_lower for kw in ['education', 'skills', 'projects', 'certifications', 'achievements', 'languages']):
            break
        
        if in_experience_section:
            cleaned = re.sub(r'^[•\-*0-9.)]+\s*', '', line_clean)
            if cleaned and len(cleaned) > 5:
                experience.append(cleaned)
                company_match = re.search(r'(?:at|with|for)\s+([A-Za-z0-9\s&.]+)', cleaned, re.IGNORECASE)
                if company_match:
                    company = company_match.group(1).strip()
                    if company and company not in companies:
                        companies.append(company)
    
    data["experience"] = experience[:4]
    data["companies"] = list(set(companies))[:3]
    
    exp_match = re.search(r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)', text_lower)
    if exp_match:
        data["total_experience"] = f"{exp_match.group(1)} years"
    elif experience:
        data["total_experience"] = f"{len(experience)} positions"
    
    languages = []
    lang_list = ['Urdu', 'English', 'Punjabi', 'Sindhi', 'Pashto', 'Balochi', 'Arabic', 'French', 'Spanish', 'German', 'Chinese', 'Japanese']
    
    in_lang_section = False
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        line_lower = line_clean.lower()
        
        if 'languages' in line_lower or 'language' in line_lower:
            in_lang_section = True
            continue
        
        if in_lang_section and any(kw in line_lower for kw in ['education', 'skills', 'experience', 'projects']):
            break
        
        if in_lang_section:
            for lang in lang_list:
                if lang.lower() in line_lower:
                    if lang not in languages:
                        languages.append(lang)
    
    if not languages:
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
            for lang in lang_list:
                if lang.lower() in line_clean.lower():
                    if not any(section in line_clean.lower() for section in ['summary', 'profile', 'education', 'skills']):
                        if lang not in languages:
                            languages.append(lang)
    
    data["languages"] = list(set(languages))[:5]
    
    return data

def parse_cv_file(uploaded_file):
    try:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        text = ""
        
        if file_ext == 'pdf':
            import pdfplumber
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            try:
                with pdfplumber.open(tmp_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
            finally:
                os.unlink(tmp_path)
        elif file_ext == 'docx':
            import docx2txt
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name
            try:
                text = docx2txt.process(tmp_path)
            finally:
                os.unlink(tmp_path)
        else:
            return {"error": "Unsupported file format"}
        
        if not text or len(text.strip()) < 50:
            return {"error": "Could not extract text from CV"}
        
        return parse_cv_text(text)
        
    except Exception as e:
        return {"error": f"Error parsing CV: {str(e)}"}

def display_uploaded_image(uploaded_file, width=200):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            st.image(image, width=width, use_container_width=False)
            return True
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")
            return False
    return False

def show():
    st.markdown("""
        <style>
            .stApp { background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); }
            .main .block-container { padding-top: 1rem; }
            .page-title { font-size: 28px; font-weight: 700; color: #ffffff; margin-bottom: 5px; }
            .page-subtitle { color: #a0aec0; font-size: 14px; margin-bottom: 20px; }
            
            .section-card {
                background: rgba(255,255,255,0.05);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 20px 24px;
                margin-bottom: 20px;
            }
            .section-title {
                font-size: 16px; font-weight: 600; color: #ffffff; margin-bottom: 15px;
                display: flex; justify-content: space-between; align-items: center;
            }
            .section-title .badge {
                font-size: 12px; font-weight: 400; color: #a0aec0;
                background: rgba(255,255,255,0.06); padding: 4px 14px; border-radius: 20px;
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
            .missing-label { color: #fc8181; font-size: 11px; font-weight: 500; }
            .found-label { color: #48bb78; font-size: 11px; font-weight: 500; }
            
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
            
            .upload-box {
                border: 2px dashed rgba(255,255,255,0.15);
                border-radius: 12px;
                padding: 25px;
                text-align: center;
                color: #a0aec0;
                transition: all 0.3s ease;
                margin: 10px 0;
            }
            .upload-box:hover {
                border-color: rgba(102, 126, 234, 0.4);
                background: rgba(255,255,255,0.02);
            }
            .upload-box .icon { font-size: 32px; display: block; margin-bottom: 10px; }
            
            .image-preview-container {
                background: rgba(0,0,0,0.2);
                border-radius: 8px;
                padding: 10px;
                margin: 5px 0;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .image-uploaded-badge {
                background: #48bb78;
                color: white;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 11px;
                margin-top: 5px;
            }
            
            .status-badge {
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
                display: inline-block;
            }
            .status-pending {
                background: rgba(237,137,54,0.2);
                color: #ed8936;
            }
            .status-approved {
                background: rgba(72,187,120,0.2);
                color: #48bb78;
            }
            .status-rejected {
                background: rgba(252,129,129,0.2);
                color: #fc8181;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="page-title">New HR Management</div>
        <div class="page-subtitle">Add, review, and manage new HR staff</div>
    """, unsafe_allow_html=True)
    
    db = SessionLocal()
    
    def get_password_hash(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def create_hr_employee(employee_data):
        designation = employee_data.get('designation', '')[:100] if employee_data.get('designation') else ''
        name = employee_data.get('name', '')[:100] if employee_data.get('name') else ''
        first_name = employee_data.get('first_name', '')[:50] if employee_data.get('first_name') else ''
        last_name = employee_data.get('last_name', '')[:50] if employee_data.get('last_name') else ''
        
        existing_emp = db.query(Employee).filter(Employee.email == employee_data.get('email')).first()
        if existing_emp:
            return None, "Employee with this email already exists!"
        
        employee = Employee(
            emp_id=employee_data.get('id', f"HR-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"),
            name=name,
            first_name=first_name,
            last_name=last_name,
            email=employee_data.get('email', ''),
            phone=employee_data.get('phone', '')[:20] if employee_data.get('phone') else '',
            city=employee_data.get('city', '')[:100] if employee_data.get('city') else '',
            linkedin=employee_data.get('linkedin', '')[:255] if employee_data.get('linkedin') else '',
            github=employee_data.get('github', '')[:255] if employee_data.get('github') else '',
            designation=designation,
            department=employee_data.get('department', 'HR')[:100] if employee_data.get('department') else 'HR',
            joining_date=datetime.strptime(employee_data.get('joining_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
            education=employee_data.get('education', {}),
            skills=employee_data.get('skills', []),
            status="Pending"
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        
        # Add audit log
        add_audit_log(
            get_current_user(),
            "Add HR Employee",
            f"Added new HR employee: {name} ({employee_data.get('email')}) - {designation}"
        )
        
        return employee, None
    
    def approve_hr_employee(employee_id):
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            username = employee.email.split('@')[0]
            existing_user = db.query(User).filter(User.username == username).first()
            
            if existing_user:
                existing_user.email = employee.email
                existing_user.full_name = employee.name
                existing_user.role = "HR"
                existing_user.is_active = True
                db.commit()
                user = existing_user
            else:
                hashed = get_password_hash("hr@123456")
                user = User(
                    username=username,
                    email=employee.email,
                    hashed_password=hashed,
                    full_name=employee.name,
                    role="HR",
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            employee.status = "Active"
            db.commit()
            db.refresh(employee)
            
            # Add audit log
            add_audit_log(
                get_current_user(),
                "Approve HR Employee",
                f"Approved HR employee: {employee.name} ({employee.email})"
            )
            
            return True
        return False
    
    def reject_hr_employee(employee_id, reason):
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if employee:
            employee.status = "Rejected"
            employee.reject_reason = reason
            employee.rejected_on = datetime.now()
            db.commit()
            db.refresh(employee)
            
            # Add audit log
            add_audit_log(
                get_current_user(),
                "Reject HR Employee",
                f"Rejected HR employee: {employee.name} ({employee.email}) - Reason: {reason}"
            )
            
            return True
        return False
    
    def generate_hr_id():
        return f"HR-{datetime.now().strftime('%Y')}-{str(uuid.uuid4())[:8].upper()}"
    
    def get_pending_employees():
        return db.query(Employee).filter(Employee.department == "HR", Employee.status == "Pending").all()
    
    def get_current_hr_employees():
        return db.query(Employee).filter(Employee.department == "HR", Employee.status == "Active").all()
    
    def get_rejected_employees():
        return db.query(Employee).filter(Employee.department == "HR", Employee.status == "Rejected").all()
    
    def clear_hr_session_state():
        edu_fields = [
            {"key": "matric"},
            {"key": "inter"},
            {"key": "bachelor"},
            {"key": "master"},
            {"key": "phd"}
        ]
        skill_keys = ['skill_1', 'skill_2', 'skill_3', 'skill_4', 'skill_5', 'skill_6', 'skill_7', 'skill_8']
        
        st.session_state.parsed_hr_data = None
        
        for edu_field in edu_fields:
            key = edu_field["key"]
            session_key = f"hr_edu_cv_{key}"
            if session_key in st.session_state:
                del st.session_state[session_key]
        
        for key in skill_keys:
            session_key = f"hr_skill_{key}"
            if session_key in st.session_state:
                del st.session_state[session_key]
        
        st.session_state.hr_pic1_cv_main = None
        st.session_state.hr_pic2_cv_main = None
    
    if 'hr_edu_cv_matric' not in st.session_state:
        st.session_state.hr_edu_cv_matric = ''
    if 'hr_edu_cv_inter' not in st.session_state:
        st.session_state.hr_edu_cv_inter = ''
    if 'hr_edu_cv_bachelor' not in st.session_state:
        st.session_state.hr_edu_cv_bachelor = ''
    if 'hr_edu_cv_master' not in st.session_state:
        st.session_state.hr_edu_cv_master = ''
    if 'hr_edu_cv_phd' not in st.session_state:
        st.session_state.hr_edu_cv_phd = ''
    
    tab1, tab2, tab3, tab4 = st.tabs(["Add New HR", "Review Applications", "Current HR", "Rejected"])
    
    with tab1:
        st.markdown("""
            <div class="section-card">
                <div class="section-title">
                    Add HR via CV Upload
                    <span class="badge">AI-Powered Parsing</span>
                </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="upload-box">
                <span class="icon">📄</span>
                Upload CV (PDF/DOCX)<br>
                <span style="font-size:12px;color:#4a5568;">AI will parse the CV and auto-fill the form</span>
            </div>
        """, unsafe_allow_html=True)
        
        uploaded_cv = st.file_uploader("Upload CV", type=["pdf", "docx"], key="new_hr_cv_upload_main", label_visibility="collapsed")
        
        parsed_data = None
        if uploaded_cv:
            with st.spinner("AI is scanning the CV..."):
                parsed_data = parse_cv_file(uploaded_cv)
                if parsed_data and "error" not in parsed_data:
                    st.success("CV parsed successfully! Form auto-filled below.")
                    st.session_state.parsed_hr_data = parsed_data
                else:
                    st.error(f"Error: {parsed_data.get('error', 'Parsing failed')}")
                    st.session_state.parsed_hr_data = None
        
        if st.session_state.get('parsed_hr_data'):
            parsed_data = st.session_state.parsed_hr_data
        
        with st.form("add_hr_cv_form"):
            st.markdown("""<div style="color:#cbd5e0;font-size:14px;font-weight:600;margin-bottom:10px;">Personal Information</div>""", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *", value=parsed_data.get('first_name', '') if parsed_data else '')
                last_name = st.text_input("Last Name *", value=parsed_data.get('last_name', '') if parsed_data else '')
                email = st.text_input("Email *", value=parsed_data.get('email', '') if parsed_data else '')
                phone = st.text_input("Phone", value=parsed_data.get('phone', '') if parsed_data else '')
            with col2:
                city = st.text_input("City", value=parsed_data.get('city', '') if parsed_data else '')
                linkedin = st.text_input("LinkedIn", value=parsed_data.get('linkedin', '') if parsed_data else '')
                github = st.text_input("GitHub", value=parsed_data.get('github', '') if parsed_data else '')
                desig_val = parsed_data.get('designation', '')[:100] if parsed_data else ''
                designation_input = st.text_input("Designation *", value=desig_val, placeholder="e.g., HR Executive")
            
            col1, col2 = st.columns(2)
            with col1:
                department = st.selectbox("Department", ["HR", "Recruitment", "Payroll", "Training"])
            with col2:
                joining_date = st.date_input("Joining Date", datetime.now())
            
            st.markdown("""<div style="color:#cbd5e0;font-size:14px;font-weight:600;margin:15px 0 10px 0;">Educational Information</div>""", unsafe_allow_html=True)
            
            edu_data = {}
            if parsed_data and isinstance(parsed_data, dict):
                if 'education' in parsed_data:
                    edu_data = parsed_data['education']
                    if isinstance(edu_data, str):
                        try:
                            edu_data = json.loads(edu_data)
                        except:
                            edu_data = {}
                    if not isinstance(edu_data, dict):
                        edu_data = {}
            
            edu_fields = [
                {"key": "matric", "label": "Matriculation / O-Levels"},
                {"key": "inter", "label": "Intermediate / A-Levels"},
                {"key": "bachelor", "label": "Bachelor's Degree"},
                {"key": "master", "label": "Master's Degree"},
                {"key": "phd", "label": "PhD / Doctorate"}
            ]
            
            for edu_field in edu_fields:
                key = edu_field["key"]
                session_key = f"hr_edu_cv_{key}"
                if session_key not in st.session_state or not st.session_state[session_key]:
                    if key in edu_data:
                        val = edu_data[key]
                        if val and isinstance(val, str):
                            st.session_state[session_key] = val
                        elif val:
                            st.session_state[session_key] = str(val)
                    else:
                        st.session_state[session_key] = ''
            
            for edu_field in edu_fields:
                key = edu_field["key"]
                session_key = f"hr_edu_cv_{key}"
                value = st.session_state.get(session_key, '')
                
                found = bool(value and value.strip())
                block_class = "edu-block found" if found else "edu-block missing"
                label_class = "found-label" if found else "missing-label"
                status_text = "Found" if found else "Missing"
                
                st.markdown(f'<div class="{block_class}">', unsafe_allow_html=True)
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text_input(edu_field["label"], value=value, placeholder=f"Enter {edu_field['label']} details", key=session_key)
                with col2:
                    st.markdown(f'<div style="text-align:right;padding-top:6px;"><span class="{label_class}">{status_text}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("""<div style="color:#cbd5e0;font-size:14px;font-weight:600;margin:15px 0 10px 0;">Skills</div>""", unsafe_allow_html=True)
            
            skills_data = []
            if parsed_data and isinstance(parsed_data, dict):
                skills_data = parsed_data.get('skills', [])
                if not isinstance(skills_data, list):
                    skills_data = []
            
            while len(skills_data) < 8:
                skills_data.append('')
            
            skill_keys = ['skill_1', 'skill_2', 'skill_3', 'skill_4', 'skill_5', 'skill_6', 'skill_7', 'skill_8']
            for i, key in enumerate(skill_keys):
                session_key = f"hr_skill_{key}"
                if session_key not in st.session_state or not st.session_state[session_key]:
                    if i < len(skills_data) and skills_data[i]:
                        st.session_state[session_key] = skills_data[i]
                    else:
                        st.session_state[session_key] = ''
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                val1 = st.session_state.get('hr_skill_skill_1', '')
                s1 = st.text_input("Skill 1", value=val1, placeholder="e.g., Python", key="hr_skill_skill_1")
                val2 = st.session_state.get('hr_skill_skill_2', '')
                s2 = st.text_input("Skill 2", value=val2, placeholder="e.g., React", key="hr_skill_skill_2")
            with col2:
                val3 = st.session_state.get('hr_skill_skill_3', '')
                s3 = st.text_input("Skill 3", value=val3, placeholder="e.g., Django", key="hr_skill_skill_3")
                val4 = st.session_state.get('hr_skill_skill_4', '')
                s4 = st.text_input("Skill 4", value=val4, placeholder="e.g., AWS", key="hr_skill_skill_4")
            with col3:
                val5 = st.session_state.get('hr_skill_skill_5', '')
                s5 = st.text_input("Skill 5", value=val5, placeholder="e.g., Docker", key="hr_skill_skill_5")
                val6 = st.session_state.get('hr_skill_skill_6', '')
                s6 = st.text_input("Skill 6", value=val6, placeholder="e.g., Git", key="hr_skill_skill_6")
            with col4:
                val7 = st.session_state.get('hr_skill_skill_7', '')
                s7 = st.text_input("Skill 7", value=val7, placeholder="e.g., Linux", key="hr_skill_skill_7")
                val8 = st.session_state.get('hr_skill_skill_8', '')
                s8 = st.text_input("Skill 8", value=val8, placeholder="e.g., SQL", key="hr_skill_skill_8")
            
            skills_final = [s.strip() for s in [s1, s2, s3, s4, s5, s6, s7, s8] if s.strip()]
            
            if skills_final:
                skills_html = ""
                for skill in skills_final:
                    skills_html += f'<span class="skill-tag">#{skill}</span>'
                st.markdown(f'<div style="padding:5px 0;margin-top:5px;">{skills_html}</div>', unsafe_allow_html=True)
            
            st.markdown("""<div style="color:#cbd5e0;font-size:14px;font-weight:600;margin:15px 0 10px 0;">Mandatory Documents</div>""", unsafe_allow_html=True)
            st.markdown('<div class="mandatory-warning">Compulsory: Upload 2 recent photographs</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                pic1 = st.file_uploader("Photo 1 (Passport Size)", type=["jpg", "jpeg", "png", "gif", "bmp", "webp", "jfif"], key="hr_pic1_cv_main", label_visibility="collapsed")
                if pic1 is not None:
                    display_uploaded_image(pic1, width=150)
            
            with col2:
                pic2 = st.file_uploader("Photo 2 (Full Body)", type=["jpg", "jpeg", "png", "gif", "bmp", "webp", "jfif"], key="hr_pic2_cv_main", label_visibility="collapsed")
                if pic2 is not None:
                    display_uploaded_image(pic2, width=150)
            
            st.markdown("---")
            if st.form_submit_button("Submit for Review", use_container_width=True):
                edu_dict = {}
                for edu_field in edu_fields:
                    key = edu_field["key"]
                    session_key = f"hr_edu_cv_{key}"
                    edu_dict[key] = st.session_state.get(session_key, '')
                
                if first_name and last_name and email and designation_input and pic1 and pic2:
                    full_name = f"{first_name} {last_name}".strip()
                    
                    employee_data = {
                        "id": generate_hr_id(),
                        "name": full_name,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone if phone else "-",
                        "city": city if city else "-",
                        "linkedin": linkedin if linkedin else "-",
                        "github": github if github else "-",
                        "designation": designation_input[:100] if designation_input else '',
                        "department": department,
                        "joining_date": joining_date.strftime("%Y-%m-%d"),
                        "education": edu_dict,
                        "skills": skills_final
                    }
                    
                    try:
                        employee, error = create_hr_employee(employee_data)
                        if employee:
                            st.success(f"HR application for {full_name} submitted for review!")
                            clear_hr_session_state()
                            st.rerun()
                        else:
                            st.error(f"Error: {error}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error("Please fill all required fields and upload 2 photos!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        pending_employees = get_pending_employees()
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    Review Applications
                    <span class="badge">{len(pending_employees)} Pending</span>
                </div>
        """, unsafe_allow_html=True)
        
        if pending_employees:
            for emp in pending_employees:
                with st.expander(f"ID: {emp.emp_id} - {emp.name} ({emp.email})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            **Personal Information**
                            - Name: {emp.name}
                            - Email: {emp.email}
                            - Phone: {emp.phone}
                            - Designation: {emp.designation}
                            - Department: {emp.department}
                            - City: {emp.city}
                        """)
                    with col2:
                        st.markdown("**Education**")
                        edu_data = emp.education or {}
                        for key, label in [("matric", "Matric"), ("inter", "Inter"), ("bachelor", "Bachelor"), ("master", "Master"), ("phd", "PhD")]:
                            value = edu_data.get(key, '')
                            st.markdown(f"- {label}: {value if value else 'Not provided'}")
                        
                        if emp.skills:
                            st.markdown("**Skills**")
                            skills_html = ""
                            for skill in emp.skills:
                                skills_html += f'<span class="skill-tag">{skill}</span>'
                            st.markdown(skills_html, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Approve", key=f"approve_{emp.id}", use_container_width=True):
                            if approve_hr_employee(emp.id):
                                st.success(f"HR {emp.name} approved and added to Current HR!")
                                st.rerun()
                            else:
                                st.error("Failed to approve!")
                    
                    with col2:
                        if st.button("Reject", key=f"reject_{emp.id}", use_container_width=True):
                            reason = st.text_input("Rejection Reason", key=f"reason_{emp.id}")
                            if reason:
                                if reject_hr_employee(emp.id, reason):
                                    st.warning(f"HR {emp.name} rejected!")
                                    st.rerun()
                            else:
                                st.warning("Please provide a rejection reason.")
        else:
            st.info("No pending applications for review.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        current_hr = get_current_hr_employees()
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    Current HR Employees
                    <span class="badge">{len(current_hr)} HR Staff</span>
                </div>
        """, unsafe_allow_html=True)
        
        if current_hr:
            data = []
            for emp in current_hr:
                data.append({
                    "ID": emp.id,
                    "Name": emp.name,
                    "Email": emp.email,
                    "Designation": emp.designation or "N/A",
                    "Department": emp.department or "N/A",
                    "Status": "Active"
                })
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.success(f"{len(current_hr)} HR employees are currently active.")
        else:
            st.info("No HR employees found. Add HR from 'Add New HR' tab and approve from 'Review Applications'.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        rejected_employees = get_rejected_employees()
        st.markdown(f"""
            <div class="section-card">
                <div class="section-title">
                    Rejected Applications
                    <span class="badge">{len(rejected_employees)} Rejected</span>
                </div>
        """, unsafe_allow_html=True)
        
        if rejected_employees:
            for emp in rejected_employees:
                st.markdown(f"""
                    <div style="background:rgba(252,129,129,0.05);border:1px solid rgba(252,129,129,0.15);border-radius:10px;padding:15px;margin-bottom:10px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#ffffff;font-weight:600;">{emp.name}</span>
                            <span style="color:#fc8181;">{emp.email}</span>
                        </div>
                        <div style="color:#a0aec0;margin-top:5px;">
                            <strong>Designation:</strong> {emp.designation or 'N/A'}
                        </div>
                        <div style="color:#fc8181;margin-top:5px;">
                            <strong>Reason:</strong> {emp.reject_reason or 'N/A'}
                        </div>
                        <div style="color:#4a5568;font-size:12px;margin-top:5px;">
                            Rejected on: {emp.rejected_on.strftime('%Y-%m-%d %H:%M') if emp.rejected_on else 'N/A'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Delete", key=f"delete_rejected_{emp.id}"):
                    db.delete(emp)
                    db.commit()
                    st.success("Deleted!")
                    st.rerun()
        else:
            st.info("No rejected applications.")
        
        if rejected_employees:
            if st.button("Clear All Rejected Records", use_container_width=True):
                for emp in rejected_employees:
                    db.delete(emp)
                db.commit()
                st.success("All rejected records cleared!")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    db.close()

if __name__ == "__main__":
    show()