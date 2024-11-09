from flask import Flask, render_template, request, jsonify, session
import embeddings
from functools import wraps
password = 'yes'
app = Flask(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    if request.form.get('password') == password:
        session['logged_in'] = True
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid password'}), 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return jsonify({'success': True})


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/chat')
def chat():
    return render_template('chat.html')
'''
@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('./Data/', filename)
        file.save(filepath)
        description = request.form.get('description', '')
        documents = load_docs(filepath)
        chunks = chunking(documents)
        add(chunks, description)
        os.remove(filepath)  # Remove the file after processing
        return jsonify({'success': True, 'filename': filename})
    return jsonify({'error': 'Invalid file type'})

@app.route('/delete', methods=['POST'])
@login_required
def delete_from_db():
    delete_type = request.form.get('delete_type')
    if delete_type == 'all':
        delete()
        return jsonify({'success': True, 'message': 'All data deleted'})
    elif delete_type == 'file':
        filename = request.form.get('filename')
        delete(f"{filename}.txt")
        return jsonify({'success': True, 'message': f'Data for {filename} deleted'})
    return jsonify({'error': 'Invalid delete type'})

@app.route('/get_files', methods=['GET'])
@login_required
def get_files():
    files = get_files_in_db()
    return jsonify({'files': files})
'''


@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form.get('question')
    response = query_rag(question)
    return jsonify({'response': response})