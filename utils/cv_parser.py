import os
import pdfplumber
import docx2txt
import tempfile
import re

def extract_text_from_pdf(pdf_file):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(pdf_file.getbuffer())
        tmp_path = tmp.name
    
    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    finally:
        os.unlink(tmp_path)
    return text

def extract_text_from_docx(docx_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
        tmp.write(docx_file.getbuffer())
        tmp_path = tmp.name
    
    try:
        text = docx2txt.process(tmp_path)
    finally:
        os.unlink(tmp_path)
    return text

def parse_cv(uploaded_file):
    file_ext = uploaded_file.name.split('.')[-1].lower()
    
    if file_ext == 'pdf':
        text = extract_text_from_pdf(uploaded_file)
    elif file_ext == 'docx':
        text = extract_text_from_docx(uploaded_file)
    else:
        return {"error": "Please upload PDF or DOCX"}
    
    if not text or len(text.strip()) < 50:
        return {"error": "Could not extract enough text from file."}
    
    data = {
        "first_name": "",
        "last_name": "",
        "email": "",
        "phone": "",
        "address": "",
        "city": "",
        "linkedin": "",
        "github": "",
        "dob": "",
        "education": {
            "matric": "",
            "inter": "",
            "bachelor": "",
            "master": "",
            "phd": ""
        },
        "skills": [],
        "summary": "",
        "experience": [],
        "companies": [],
        "total_experience": "",
        "languages": []
    }
    
    lines = text.split('\n')
    text_lower = text.lower()
    
    # ============================================================
    # EMAIL
    # ============================================================
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        data["email"] = email_match.group(0)
    
    # ============================================================
    # PHONE
    # ============================================================
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
    
    # ============================================================
    # LINKEDIN
    # ============================================================
    linkedin_match = re.search(r'linkedin\.com/in/[A-Za-z0-9\-_]+', text_lower)
    if linkedin_match:
        data["linkedin"] = "linkedin.com/in/" + linkedin_match.group(0).split('/')[-1]
    
    # ============================================================
    # GITHUB
    # ============================================================
    github_match = re.search(r'github\.com/[A-Za-z0-9\-_]+', text_lower)
    if github_match:
        data["github"] = "github.com/" + github_match.group(0).split('/')[-1]
    
    # ============================================================
    # NAME
    # ============================================================
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
    
    # ============================================================
    # CITY
    # ============================================================
    city_match = re.search(r'(?:based in|location|city)[:\s]+([A-Za-z\s,]+)', text_lower)
    if city_match:
        data["city"] = city_match.group(1).strip().title()
    
    # ============================================================
    # ADDRESS
    # ============================================================
    address_patterns = [
        r'(?:address|current address|home address)[:\s]+([^\n]+)',
        r'([A-Za-z0-9\s,]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Sector|House|H#|Flat|Apartment|Apt)[^\n]+)'
    ]
    
    for pattern in address_patterns:
        address_match = re.search(pattern, text, re.IGNORECASE)
        if address_match:
            addr = address_match.group(1).strip()
            if len(addr) > 5 and len(addr) < 100:
                data["address"] = addr
                break
    
    # ============================================================
    # 🔥 EDUCATION - IMPROVED
    # ============================================================
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
        "bachelor": ['bs', 'bsc', 'ba', 'bcs', 'b.tech', 'b.com', 'bba', 'bachelor', 'undergraduate', 'b.e', 'b.s', 'bscs', 'bcs'],
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
            if 'bs' in edu_lower or 'bsc' in edu_lower or 'bachelor' in edu_lower:
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
    
    # ============================================================
    # 🔥 SKILLS - IMPROVED
    # ============================================================
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
        'SEO', 'Content Writing', 'Plugin Management', 'Networking', 'Cisco', 'Packet Tracer'
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
    
    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        
        if ',' in line_clean and len(line_clean) < 200:
            parts = [p.strip() for p in line_clean.split(',')]
            for part in parts:
                if len(part) > 2 and len(part) < 30:
                    for skill in all_skills:
                        if skill.lower() in part.lower():
                            if skill not in skills_found:
                                skills_found.append(skill)
    
    data["skills"] = list(set(skills_found))
    
    # ============================================================
    # EXPERIENCE
    # ============================================================
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
    
    # ============================================================
    # LANGUAGES
    # ============================================================
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