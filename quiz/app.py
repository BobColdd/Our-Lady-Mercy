"""
Computer Studies Quiz System
Flask application for administering a basic computer studies quiz
Author: Educational Content Creator
"""

from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# ==================== QUESTION BANK ====================
# 15 Multiple Choice Questions
MCQ_QUESTIONS = [
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
    },
    {
        "id": 6,
        "text": "What is the default installation directory for 64-bit programs on Windows?",
        "options": ["C:\\Program Files", "C:\\Program Files (x86)", "C:\\Windows\\System32", "C:\\Program Data"],
        "correct": "A"
    },
    {
        "id": 7,
        "text": "32-bit software can run on:",
        "options": ["32-bit Windows only", "64-bit Windows only", "Both 32-bit and 64-bit Windows", "Neither"],
        "correct": "C"
    },
    {
        "id": 8,
        "text": "What does the PATH environment variable do?",
        "options": ["Shows the current drive letter", "Tells Windows where to find executable files", "Stores the computer name", "Saves user passwords"],
        "correct": "B"
    },
    {
        "id": 9,
        "text": "Which type of environment variable affects only the current user?",
        "options": ["System variables", "Global variables", "User variables", "Local variables"],
        "correct": "C"
    },
    {
        "id": 10,
        "text": "What does IP address stand for?",
        "options": ["Internet Protocol Address", "Internal Processing Address", "Internet Provider Address", "Input Protocol Address"],
        "correct": "A"
    },
    {
        "id": 11,
        "text": "What does CC stand for in email?",
        "options": ["Copy Correct", "Carbon Copy", "Computer Copy", "Confidential Copy"],
        "correct": "B"
    },
    {
        "id": 12,
        "text": "Which command lists files and directories in Windows Command Prompt?",
        "options": ["list", "ls", "dir", "show"],
        "correct": "C"
    },
    {
        "id": 13,
        "text": "What command changes the current directory in Command Prompt?",
        "options": ["cd", "chdir", "move", "Both A and B"],
        "correct": "D"
    },
    {
        "id": 14,
        "text": "What is the first step when installing an operating system from a USB drive?",
        "options": ["Format the hard drive", "Change boot order in BIOS", "Install drivers", "Create a user account"],
        "correct": "B"
    },
    {
        "id": 15,
        "text": "What does Wi-Fi stand for?",
        "options": ["Wireless Fidelity", "Wired Fiber", "Wireless Finder", "Wide Frequency"],
        "correct": "A"
    }
]

# 20 Typing (Short Answer) Questions
TYPING_QUESTIONS = [
    {
        "id": 16,
        "text": "Define what a computer is. Include its basic functions.",
        "keywords": ["electronic", "device", "process", "data", "storage", "output"]
    },
    {
        "id": 17,
        "text": "What are Microsoft Access queries? Explain their purpose in database management.",
        "keywords": ["question", "data", "retrieve", "filter", "criteria", "database"]
    },
    {
        "id": 18,
        "text": "Name two ways to make text bold in Microsoft Word.",
        "keywords": ["Ctrl+B", "bold button", "format", "font style"]
    },
    {
        "id": 19,
        "text": "Write an Excel formula to calculate the average of numbers in cells A1 through A10.",
        "keywords": ["=AVERAGE(A1:A10)", "average", "formula"]
    },
    {
        "id": 20,
        "text": "What is the difference between 32-bit and 64-bit software?",
        "keywords": ["memory", "processing", "compatibility", "performance"]
    },
    {
        "id": 21,
        "text": "Why would you add a directory to the PATH environment variable?",
        "keywords": ["run", "execute", "command", "anywhere", "terminal"]
    },
    {
        "id": 22,
        "text": "What is the difference between a LAN and a WAN?",
        "keywords": ["local", "wide", "area", "network", "geographic"]
    },
    {
        "id": 23,
        "text": "List two rules of good email etiquette when writing to a teacher or supervisor.",
        "keywords": ["subject line", "greeting", "professional", "clear", "signature"]
    },
    {
        "id": 24,
        "text": "Write the command to create a new directory called 'Projects' in Command Prompt.",
        "keywords": ["mkdir Projects", "md Projects", "mkdir", "make directory"]
    },
    {
        "id": 25,
        "text": "What is disk partitioning during OS installation?",
        "keywords": ["divide", "sections", "drive", "separate", "volumes"]
    },
    {
        "id": 26,
        "text": "What is a web browser? Give two examples.",
        "keywords": ["software", "website", "Chrome", "Firefox", "Safari", "Edge"]
    },
    {
        "id": 27,
        "text": "Explain the difference between CC and BCC in email.",
        "keywords": ["carbon copy", "blind carbon copy", "recipients", "visible", "hidden"]
    },
    {
        "id": 28,
        "text": "What is the function of a router in a network?",
        "keywords": ["connect", "networks", "direct", "traffic", "internet"]
    },
    {
        "id": 29,
        "text": "Name three common Microsoft PowerPoint views.",
        "keywords": ["normal", "slide sorter", "reading", "outline", "notes page"]
    },
    {
        "id": 30,
        "text": "What is the difference between Save and Save As in Microsoft Office?",
        "keywords": ["existing file", "new file", "location", "name", "overwrite"]
    },
    {
        "id": 31,
        "text": "Explain what an IP address is and why it's important.",
        "keywords": ["identifier", "device", "network", "communication", "unique"]
    },
    {
        "id": 32,
        "text": "What is the purpose of the 'ping' command in Command Prompt?",
        "keywords": ["test", "connectivity", "network", "response", "reachability"]
    },
    {
        "id": 33,
        "text": "List two examples of system software and two examples of application software.",
        "keywords": ["windows", "linux", "word", "excel", "operating system"]
    },
    {
        "id": 34,
        "text": "What happens if you install a 32-bit program on a 64-bit Windows computer?",
        "keywords": ["compatibility mode", "program files x86", "works", "emulation"]
    },
    {
        "id": 35,
        "text": "Why should you use BCC when sending emails to multiple recipients who don't know each other?",
        "keywords": ["privacy", "hide", "addresses", "respect", "spam"]
    }
]

# ==================== STORAGE ====================
# In-memory storage for quiz results
QUIZ_RESULTS = []
RESULTS_FILE = 'quiz_results.json'

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

# Load existing results when app starts
load_results_from_file()

# ==================== HELPER FUNCTIONS ====================
def grade_mcq(answers):
    """Grade multiple choice questions"""
    score = 0
    for i, question in enumerate(MCQ_QUESTIONS):
        answer_key = f"mcq_{question['id']}"
        user_answer = answers.get(answer_key, "")
        if user_answer == question['correct']:
            score += 1
    return score

# ==================== ROUTES ====================
@app.route('/')
def login():
    """Login page - collects student information"""
    return render_template('login.html', school_name="St Francis Mercy Community Center")

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    """Store student info and redirect to quiz"""
    session['student_name'] = request.form.get('student_name', 'Anonymous')
    session['student_id'] = request.form.get('student_id', 'Unknown')
    return redirect(url_for('quiz'))

@app.route('/quiz')
def quiz():
    """Display the quiz with all questions"""
    if 'student_name' not in session:
        return redirect(url_for('login'))
    
    return render_template('quiz.html', 
                         mcq_questions=MCQ_QUESTIONS,
                         typing_questions=TYPING_QUESTIONS)

@app.route('/submit', methods=['POST'])
def submit():
    """Process quiz submission, grade MCQs, and store results"""
    # Get student info from session
    student_name = session.get('student_name', 'Anonymous')
    student_id = session.get('student_id', 'Unknown')
    
    # Grade multiple choice questions
    mcq_score = grade_mcq(request.form)
    
    # Collect answers for storage
    mcq_answers = {}
    for question in MCQ_QUESTIONS:
        answer_key = f"mcq_{question['id']}"
        mcq_answers[question['id']] = request.form.get(answer_key, "Not answered")
    
    typing_answers = {}
    for question in TYPING_QUESTIONS:
        answer_key = f"typing_{question['id']}"
        typing_answers[question['id']] = request.form.get(answer_key, "")
    
    # Store results
    result = {
        'student_name': student_name,
        'student_id': student_id,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'mcq_score': mcq_score,
        'mcq_total': 15,
        'mcq_answers': mcq_answers,
        'typing_answers': typing_answers
    }
    
    QUIZ_RESULTS.append(result)
    save_results_to_file()  # Save to file for persistence
    
    # Clear session
    session.clear()
    
    # Show simple completion message
    return render_template('completion.html', 
                         student_name=student_name,
                         message="✅ Your quiz has been submitted successfully!")

@app.route('/view_all_results')
def view_all_results():
    """Admin page to view all quiz results"""
    return render_template('all_results.html', results=QUIZ_RESULTS)

@app.route('/view_answers/<int:result_index>')
def view_answers(result_index):
    """View detailed answers for a specific student submission"""
    if result_index < 0 or result_index >= len(QUIZ_RESULTS):
        return redirect(url_for('view_all_results'))
    
    result = QUIZ_RESULTS[result_index]
    return render_template('view_answers.html', result=result, 
                         typing_questions=TYPING_QUESTIONS)

@app.route('/export_csv')
def export_csv():
    """Export all results to CSV for easy grading"""
    import csv
    from flask import Response
    
    # Create CSV content
    output = []
    headers = ['Timestamp', 'Student Name', 'Student ID', 'MCQ Score']
    # Add headers for each typing question
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
        # Add typing answers in order
        for q in TYPING_QUESTIONS:
            row.append(result['typing_answers'].get(str(q['id']), ''))
        output.append(row)
    
    # Create CSV response
    def generate():
        for row in output:
            yield ','.join(f'"{str(cell).replace(chr(34), chr(34)+chr(34))}"' for cell in row) + '\n'
    
    return Response(generate(), mimetype='text/csv', 
                   headers={"Content-Disposition": "attachment;filename=quiz_answers.csv"})

# ==================== RUN APPLICATION ====================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
