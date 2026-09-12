  # Resume–JD Matcher (ATS-style Assistant)

A Python + Streamlit web app that compares your resume with a job description and provides:
- Resume–JD match score (0–100) using sentence embeddings  
- Detected skills in resume and JD  
- Missing / gap skills  
- Tailored suggestions based on career level (fresher / early / experienced) and target role  
- Basic profile strength indicator

## Tech Stack

- Python  
- Streamlit  
- sentence-transformers  
- scikit-learn  
- pdfplumber  

## Features

- Upload resume (PDF) and paste job description  
- Select career level and target role  
- Get:
  - Match score  
  - Skills detected in resume & JD  
  - Suggested skills to add  
  - Tailored suggestions for freshers and experienced candidates  
  - Profile strength heuristic  

## How to Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/resume-jd-matcher.git
   cd resume-jd-matcher
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

Open `http://localhost:8501` in your browser.

## Future Enhancements

- Multi-resume ranking for a single JD  
- ATS friendliness checks (sections, length, keywords)  
- Deployment on Streamlit Cloud / Hugging Face Spaces  
- Improved skill extraction with phrase matching

## Author

Your Name  
[LinkedIn](https://www.linkedin.com/in/srinivas-kalyan7432) | [GitHub](https://github.com/kilarisrinivaskalyan7432)
