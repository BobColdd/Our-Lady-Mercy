"""
Computer Studies Quiz System
Flask application for administering a basic computer studies quiz
Author: Educational Content Creator
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

QUESTIONS_FILE = 'questions.json'
RESULTS_FILE = 'quiz_results.json'

# Hardcoded valid credentials for functional login: {student_id: student_name}
STUDENT_DATABASE = {
    "STD001": "John Doe",
    "STD002": "Jane Smith",
    "STD003": "Grace Wanjiku",
    "STD004": "David Ochieng"
}

# ==================== DEFAULT QUESTION BANKS ====================
DEFAULT_MCQ_QUESTIONS = [
    {
        "id": 1,
        "text": "What does CPU stand for?",
        "options": ["Central Processing Unit", "Computer Personal Unit", "Central Program Utility", "Core Processing Utility"],
        "correct": "A"
    },
    {
        "id": 2,
        "text": "Which of the following is an input device?",
        "options": ["Monitor", "Printer", "Keyboard", "Speaker"],
        "correct": "C"
    },
    {
        "id": 3,
        "text": "What is the purpose of RAM?",
        "options": ["Permanent storage of files", "Temporary storage for running programs", "Processing mathematical calculations", "Displaying graphics"],
        "correct": "B"
    },
    {
        "id": 4,
        "text": "In Microsoft Word, which shortcut is used to save a document?",
        "options": ["Ctrl + P", "Ctrl + S", "Ctrl + N", "Ctrl + O"],
        "correct": "B"
    },
    {
        "id": 5,
        "text": "In Excel, what does the SUM function do?",
        "options": ["Finds the average of numbers", "Adds up a range of numbers", "Counts the number of cells", "Finds the maximum value"],
        "correct": "B"
    }
]

DEFAULT_TYPING_QUESTIONS = [
    {
        "id": 16,
        "text": "Define what a computer is. Include its basic functions.",
        "keywords": ["electronic", "device", "process", "data", "storage", "output"]
    },
    {
        "id": 17,
        "text": "What are Microsoft Access queries? Explain their purpose in database management.",
        "keywords": ["question", "data", "retrieve", "filter", "criteria", "database"]
    }
]

MCQ_QUESTIONS = []
TYPING_QUESTIONS = []
QUIZ_RESULTS = []

# ==================== STORAGE MANAGERS ====================
def save_questions_to_file():
    """Save current question state to JSON file"""
    try:
        data = {
            "mcq_questions": MCQ_QUESTIONS,
            "typing_questions": TYPING_QUESTIONS
        }
        with open(QUESTIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving questions: {e}")

def load_questions_from_file():
    """Load question set from file or seed defaults"""
    global MCQ_QUESTIONS, TYPING_QUESTIONS
    if os.path.exists(QUESTIONS_FILE):
        try:
            with open(QUESTIONS_FILE, 'r') as f:
                data = json.load(f)
                MCQ_QUESTIONS = data.get("mcq_questions", [])
                TYPING_QUESTIONS = data.get("typing_questions", [])
        except Exception as e:
            print(f"Error loading questions: {e}")
            MCQ_QUESTIONS, TYPING_QUESTIONS = DEFAULT_MCQ_QUESTIONS, DEFAULT_TYPING_QUESTIONS
    else:
        MCQ_QUESTIONS = DEFAULT_MCQ_QUESTIONS
        TYPING_QUESTIONS = DEFAULT_TYPING_QUESTIONS
        save_questions_to_file()

def save_results_to_file():
    """Save quiz results to a JSON file for persistence"""
    try:
        with open(RESULTS_FILE, 'w') as f:
            json.dump(QUIZ_RESULTS, f, indent=2)
    except Exception as e:
        print(f"Error saving results: {e}")

def load_results_from_file():
    """Load quiz results from JSON file"""
    global QUIZ_RESULTS
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r') as f:
                QUIZ_RESULTS = json.load(f)
        except Exception as e:
            print(f"Error loading results: {e}")
            QUIZ_RESULTS = []

# Initialize data states
load_questions_from_file()
load_results_from_file()

# ==================== HELPER FUNCTIONS ====================
def grade_mcq(answers):
    """Grade multiple choice questions safely"""
    score = 0
    option_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    for question in MCQ_QUESTIONS:
        answer_key = f"mcq_{question['id']}"
        user_answer = answers.get(answer_key, "").strip()
        
        # Check if correct field holds the letter (e.g. "A") or exact text content
        target = question.get('correct', '')
        if user_answer == target:
            score += 1
        elif target in option_map and user_answer:
            idx = option_map[target]
            if idx < len(question['options']) and user_answer == question['options'][idx]:
                score += 1
    return score

# ==================== ROUTES ====================
@app.route('/')
def login():
    """Login page"""
    return render_template('login.html', school_name="Our Lady of Mercy Community Center")

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    """Validate credentials and handle user session initialization"""
    student_name = request.form.get('student_name', '').strip()
    student_id = request.form.get('student_id', '').strip()
    
    # Simple explicit validation match check
    if student_id in STUDENT_DATABASE and STUDENT_DATABASE[student_id].lower() == student_name.lower():
        session['student_name'] = STUDENT_DATABASE[student_id]
        session['student_id'] = student_id
        return redirect(url_for('quiz'))
    
    # Return error feedback or bounce to login page
    flash("Invalid Student Name or ID. Please check your credentials.", "error")
    return redirect(url_for('login'))

@app.route('/quiz')
def quiz():
    """Display active quiz interface"""
    if 'student_name' not in session:
        return redirect(url_for('login'))
    
    return render_template('quiz.html', 
                           mcq_questions=MCQ_QUESTIONS,
                           typing_questions=TYPING_QUESTIONS)

@app.route('/submit', methods=['POST'])
def submit():
    """Process submitted quiz parameters and record session results"""
    student_name = session.get('student_name', 'Anonymous')
    student_id = session.get('student_id', 'Unknown')
    
    mcq_score = grade_mcq(request.form)
    
    mcq_answers = {
        str(q['id']): request.form.get(f"mcq_{q['id']}", "Not answered")
        for q in MCQ_QUESTIONS
    }
    
    typing_answers = {
        str(q['id']): request.form.get(f"typing_{q['id']}", "")
        for q in TYPING_QUESTIONS
    }
    
    result = {
        'student_name': student_name,
        'student_id': student_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'mcq_score': mcq_score,
        'mcq_total': len(MCQ_QUESTIONS),
        'mcq_answers': mcq_answers,
        'typing_answers': typing_answers
    }
    
    QUIZ_RESULTS.append(result)
    save_results_to_file()
    session.clear()
    
    return render_template('completion.html', 
                           student_name=student_name,
                           message="✅ Your quiz has been submitted successfully!")

@app.route('/upload_questions', methods=['GET', 'POST'])
def upload_questions():
    """Endpoint for posting fresh question structure payloads via JSON file upload"""
    global MCQ_QUESTIONS, TYPING_QUESTIONS
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file context submitted", "error")
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash("No file selected", "error")
            return redirect(request.url)

        if file and file.filename.endswith('.json'):
            try:
                payload = json.load(file)
                if "mcq_questions" in payload and "typing_questions" in payload:
                    MCQ_QUESTIONS = payload["mcq_questions"]
                    TYPING_QUESTIONS = payload["typing_questions"]
                    save_questions_to_file()
                    flash("Question bank updated successfully!", "success")
                else:
                    flash("Invalid JSON schema structure. Keys 'mcq_questions' and 'typing_questions' are required.", "error")
            except Exception as e:
                flash(f"Failed parsing uploaded JSON: {str(e)}", "error")
        else:
            flash("Allowed file extensions: .json", "error")

        return redirect(url_for('upload_questions'))

    return render_template('upload_questions.html')

@app.route('/view_all_results')
def view_all_results():
    return render_template('all_results.html', results=QUIZ_RESULTS)

@app.route('/view_answers/<int:result_index>')
def view_answers(result_index):
    if result_index < 0 or result_index >= len(QUIZ_RESULTS):
        return redirect(url_for('view_all_results'))
    
    result = QUIZ_RESULTS[result_index]
    return render_template('view_answers.html', result=result, typing_questions=TYPING_QUESTIONS)

@app.route('/export_csv')
def export_csv():
    output = []
    headers = ['Timestamp', 'Student Name', 'Student ID', 'MCQ Score']
    for q in TYPING_QUESTIONS:
        headers.append(f"Q{q['id']}: {q['text'][:50]}...")
    output.append(headers)
    
    for result in QUIZ_RESULTS:
        row = [
            result['timestamp'],
            result['student_name'],
            result['student_id'],
            f"{result['mcq_score']}/{result['mcq_total']}"
        ]
        for q in TYPING_QUESTIONS:
            row.append(result['typing_answers'].get(str(q['id']), ''))
        output.append(row)
    
    def generate():
        for row in output:
            yield ','.join(f'"{str(cell).replace(chr(34), chr(34)+chr(34))}"' for cell in row) + '\n'
    
    return Response(generate(), mimetype='text/csv', 
                   headers={"Content-Disposition": "attachment;filename=quiz_answers.csv"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
