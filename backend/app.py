from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import json, os, uuid, bcrypt
from werkzeug.utils import secure_filename
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import re
import PyPDF2
import io

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(DATA_DIR, '.env'))

# Initialize Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# MongoDB connection
client = MongoClient("mongodb://127.0.0.1:27017/")
db = client["legalconnect"]

# Collections
constitution_col = db["constitution_parts"]
users_col = db["users"]
posts_col = db["posts"]
chat_history_col = db["chat_history"]  # New collection for chat history

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['UPLOAD_FOLDER'] = os.path.join(DATA_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = os.path.join(DATA_DIR, 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm', 'pdf', 'txt', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'txt'}
ALLOWED_AVATAR_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# ---------- helpers ----------
def _p(path): 
    return os.path.join(DATA_DIR, path)

def load_json(name, default=None):
    path = _p(name)
    if not os.path.exists(path):
        return default if default is not None else ({} if name not in ('posts.json','conversations.json') else [])
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return default if default is not None else ([] if name in ('posts.json','conversations.json') else {})

def save_json(name, data):
    with open(_p(name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def allowed_file(filename, avatars=False):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in (ALLOWED_AVATAR_EXTENSIONS if avatars else ALLOWED_EXTENSIONS)

def parse_document_content(file):
    """Extract text content from PDF or TXT files"""
    try:
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            # Parse PDF
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        elif filename.endswith('.txt'):
            # Parse TXT
            content = file.read()
            return content.decode('utf-8').strip()
        else:
            return None
    except Exception as e:
        print(f"Error parsing document: {e}")
        return None

def allowed_document_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in ALLOWED_DOCUMENT_EXTENSIONS

def _format_chatbot_reply(text):
    # Aggressively remove all single and multiple asterisks that are not part of **bold** syntax
    # This regex is designed to be very aggressive. It targets:
    # 1. Isolated single asterisks: `(?<!\*)\*(?!\*)` (not preceded or followed by another asterisk)
    # 2. Three or more asterisks: `\*{3,}`
    # It tries to leave `**text**` intact for bolding.
    text = re.sub(r'(?<!\*)\*(?!\*)|\*{3,}', '', text)

    # Replace common list-like prefixes (numbers, hyphens with various spacing, bullet characters) with a standard Markdown bullet point '- '
    # This also normalizes multiple hyphens to a single one.
    text = re.sub(r'^\s*(?:\d+\.\s*|\d+\)\s*|\*\s*|\-+\s*|[•]\s*)', '- ', text, flags=re.MULTILINE)

    lines = text.split('\n')
    formatted_lines = []

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue

        # If the line already starts with a bullet, ensure it's clean
        if stripped_line.startswith('-'):
            formatted_lines.append('- ' + stripped_line[1:].lstrip().replace('** ', '**')) # Clean up extra space after **
        else:
            # If it doesn't start with a bullet but contains text, assume it's a new point
            # This is a heuristic that might need further adjustment.
            formatted_lines.append('- ' + stripped_line.replace('** ', '**')) # Add a bullet and clean up bolding spacing

    # Join the lines back together, ensuring each is on a new line.
    return '\n'.join(formatted_lines)

# Optional: serve a simple manifest to silence 404 spam in logs
@app.route('/manifest.json')
def manifest_json():
    return jsonify({
        "name": "App",
        "short_name": "App",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#000000",
        "theme_color": "#000000",
        "icons": []
    })

# MongoDB connection test route
@app.route('/api/test-db', methods=['GET'])
def test_db():
    try:
        db.list_collection_names()
        return jsonify({"status": "MongoDB connected successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Auth ----------
@app.route('/register', methods=['POST'])
def register():
    users = load_json('users.json', {})
    data = request.json or {}

    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'error': 'Missing fields'}), 400
    if data['email'] in users:
        return jsonify({'error': 'Email already exists'}), 409

    uid = str(uuid.uuid4())
    hashed = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users[data['email']] = {
        'id': uid,
        'name': data['name'],
        'email': data['email'],
        'password': hashed,
        'role': data.get('role','public'),
        'avatar': data.get('avatar') or '/default-avatar.png',
        'bio': data.get('bio',''),
        # if you use bar code for lawyers, you can store it here:
        'bar_code': data.get('bar_code'),
        'followers': [],
        'following': [],
        'isVerified': False # Default false, admin can verify lawyers
    }
    save_json('users.json', users)
    return jsonify({
        'id': uid,
        'name': data['name'],
        'email': data['email'],
        'role': users[data['email']]['role'],
        'avatar': users[data['email']]['avatar'],
        'isVerified': users[data['email']]['isVerified']
    })

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # CORS preflight
        return '', 200

    data = request.get_json() or {}
    email_or_bar = data.get('emailOrBar')
    password = data.get('password')

    print(f"Login attempt - emailOrBar: {email_or_bar}, password length: {len(password) if password else 0}")

    if not email_or_bar or not password:
        return jsonify({'error': 'Missing credentials'}), 400

    users = load_json('users.json', {})
    user_entry = None

    # users.json structure: { "<email>": { userObj } }
    for email, u in users.items():
        if u.get('email') == email_or_bar or u.get('bar_code') == email_or_bar:
            user_entry = u
            print(f"Found user: {u.get('email')} with role: {u.get('role')}")
            break

    if not user_entry:
        print(f"User not found for: {email_or_bar}")
        return jsonify({'error': 'User not found'}), 401

    # bcrypt check against stored hash
    try:
        if not bcrypt.checkpw(password.encode('utf-8'), user_entry['password'].encode('utf-8')):
            print(f"Password check failed for user: {user_entry.get('email')}")
            return jsonify({'error': 'Invalid password'}), 401
        print(f"Password check successful for user: {user_entry.get('email')}")
    except Exception as e:
        print(f"Exception during password check: {e}")
        # In case some legacy accounts were stored in plain text by mistake
        if user_entry['password'] != password:
            print(f"Plain text password check failed for user: {user_entry.get('email')}")
            return jsonify({'error': 'Invalid password'}), 401

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user_entry['id'],
            'email': user_entry['email'],
            'name': user_entry.get('name'),
            'role': user_entry.get('role','public'),
            'avatar': user_entry.get('avatar','/default-avatar.png')
        }
    }), 200

# ---------- Uploads ----------
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    if file and allowed_file(file.filename):
        filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return jsonify({'url': f"/uploads/{filename}"})
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' not in request.files:
        return jsonify({'error': 'No avatar provided'}), 400
    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    if file and allowed_file(file.filename, avatars=True):
        filename = f"avatar_{uuid.uuid4()}_{secure_filename(file.filename)}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        return jsonify({'url': f"/uploads/{filename}"})
    return jsonify({'error': 'Invalid avatar file (PNG/JPG/JPEG/GIF only)'}), 400

@app.route('/upload-document', methods=['POST'])
def upload_document():
    if 'document' not in request.files:
        return jsonify({'error': 'No document provided'}), 400
    file = request.files['document']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    if not allowed_document_file(file.filename):
        return jsonify({'error': 'Invalid document file (PDF/TXT only)'}), 400
    
    try:
        # Parse the document content
        content = parse_document_content(file)
        if content is None:
            return jsonify({'error': 'Failed to parse document content'}), 400
        
        # Save the file
        filename = f"doc_{uuid.uuid4()}_{secure_filename(file.filename)}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.seek(0)  # Reset file pointer after reading
        file.save(path)
        
        return jsonify({
            'url': f"/uploads/{filename}",
            'content': content,
            'filename': file.filename,
            'message': 'Document uploaded and parsed successfully'
        })
    except Exception as e:
        return jsonify({'error': f'Error processing document: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- Chatbot ----------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    message = data.get('message', '').strip()
    document = data.get('document', '')
    
    # Check if message is a greeting
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 
                 'greetings', 'namaste', 'hola', 'howdy']
    
    message_lower = message.lower()
    
    # Handle greetings
    if any(greeting == message_lower or message_lower.startswith(greeting + ' ') 
           for greeting in greetings):
        return jsonify({
            'reply': "Hello! 👋\n\nI'm your Constitutional Law Assistant. I can help you with questions about the **Constitution of India**.\n\nFeel free to ask me about:\n- Specific articles (e.g., \"What is Article 21?\")\n- Fundamental Rights\n- Directive Principles\n- Constitutional amendments\n- Any other constitutional provisions\n\nHow can I assist you today?"
        })
    
    # For constitutional questions, use Gemini API with Constitutional Law guidelines
    prompt = f"""You are a professional Constitutional Law Assistant for India.

CRITICAL RULES:

1. SCOPE - Answer ONLY using the Constitution of India:
   - Answer ONLY using the Constitution of India
   - Do NOT use IPC, CrPC, or other laws
   - Do NOT mention punishments or criminal procedures
   - Do NOT use foreign laws or personal opinions
   - Do NOT give punishments or non-constitutional laws
   - If not in Constitution, say: "This question is not directly covered under the Constitution of India."

2. RESPONSE STRUCTURE (Follow this format with proper spacing):

SHORT ANSWER:
[1-2 lines direct answer]

CONSTITUTIONAL REFERENCE:
[Mention specific Article number(s) from Constitution]

EXPLANATION:
[Explain in simple, conversational language]

(Add blank lines between each section for better readability)

3. LANGUAGE STYLE:
   - Use simple, conversational English
   - Be friendly and approachable (like Gemini)
   - Do NOT add unnecessary legal jargon
   - Do NOT include long lists or textbook-style explanations
   - Provide examples when helpful
   - Keep answers concise (2-4 short paragraphs max)
   - Use light, professional emojis sparingly (⚖️ 📜 ✅ ❗ 👋)
   - Do NOT overuse emojis
   - Maintain a friendly, human tone

4. FORMATTING:
   - Highlight sub-titles clearly using simple headings
   - Do NOT use *, **, or excessive markdown symbols
   - Bold ONLY key constitutional terms, article numbers, and main ideas
   - Do NOT bold entire sentences or paragraphs
   - Use bullet points for lists (keep them short)
   - Keep paragraphs short and readable

**Context Document:** {document if document else "No specific document provided."}

**User Question:** {message}

Remember: Base your answer strictly on the Constitution of India. Be helpful, accurate, structured, and concise. Avoid jargon and long explanations. Use clean formatting with minimal symbols."""   

    try:
        # Use Gemini for user-friendly responses
        response = model.generate_content(prompt)
        reply = response.text
        reply = _format_chatbot_reply(reply)
        
        # Save chat history to MongoDB
        chat_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_message": message,
            "bot_response": reply,
            "document_context": document if document else None
        }
        chat_history_col.insert_one(chat_entry)
        
    except Exception as e:
        print(f"Error generating content from Gemini: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        reply = "I'm sorry, I'm unable to respond at the moment. Please try again later."
    
    return jsonify({'reply': reply})

# Get chat history
@app.route('/chat/history', methods=['GET'])
def get_chat_history():
    try:
        # Get optional limit parameter (default: 50 most recent)
        limit = request.args.get('limit', 50, type=int)
        
        # Retrieve chat history sorted by most recent first
        history = list(chat_history_col.find(
            {},
            {'_id': 0}  # Exclude MongoDB _id field
        ).sort("timestamp", -1).limit(limit))
        
        return jsonify({
            'success': True,
            'count': len(history),
            'history': history
        })
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ---------- Profile ----------
@app.route('/profile/<user_id>', methods=['GET','POST'])
def profile(user_id):
    users = load_json('users.json', {})
    email_key = next((k for k,v in users.items() if v.get('id') == user_id), None)
    if not email_key:
        return jsonify({'error': 'User not found'}), 404

    if request.method == 'GET':
        u = users[email_key]
        return jsonify({
            'id': u['id'],
            'name': u['name'],
            'email': u['email'],
            'role': u.get('role','public'),
            'avatar': u.get('avatar','/default-avatar.png'),
            'isVerified': u.get('isVerified', False),
            'bio': u.get('bio',''),
            'followers': u.get('followers',[]),
            'following': u.get('following',[])
        })

    data = request.json or {}
    u = users[email_key]
    for k in ('name','bio','avatar'):
        if k in data:
            u[k] = data[k]
    users[email_key] = u
    save_json('users.json', users)
    return jsonify({'message':'updated','user': u})

@app.route('/profile/<user_id>/delete', methods=['DELETE'])
def delete_account(user_id):
    users = load_json('users.json', {})
    data = request.json or {}
    
    # Find user by ID
    email_key = next((k for k,v in users.items() if v.get('id') == user_id), None)
    if not email_key:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify password for security
    password = data.get('password')
    if not password:
        return jsonify({'error': 'Password required for account deletion'}), 400
    
    user = users[email_key]
    try:
        if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': 'Invalid password'}), 401
    except Exception:
        # Handle legacy accounts with plain text passwords
        if user['password'] != password:
            return jsonify({'error': 'Invalid password'}), 401
    
    # Delete user's posts
    posts_data = load_json('posts.json', [])
    posts_data = [post for post in posts_data if post.get('userId') != user_id]
    save_json('posts.json', posts_data)
    
    # Remove user from conversations
    conversations = load_json('conversations.json', [])
    conversations = [conv for conv in conversations if user_id not in conv.get('users', [])]
    save_json('conversations.json', conversations)
    
    # Remove user from notifications
    notifications = load_json('notifications.json', {})
    # Remove notifications for this user
    if user_id in notifications:
        del notifications[user_id]
    # Remove notifications from this user to others
    for other_user_id, user_notifs in notifications.items():
        notifications[other_user_id] = [notif for notif in user_notifs if notif.get('from') != user_id]
    save_json('notifications.json', notifications)
    
    # Remove user from followers/following lists
    for email, other_user in users.items():
        if other_user.get('id') != user_id:
            if 'followers' in other_user and user_id in other_user['followers']:
                other_user['followers'].remove(user_id)
            if 'following' in other_user and user_id in other_user['following']:
                other_user['following'].remove(user_id)
    
    # Delete the user
    del users[email_key]
    save_json('users.json', users)
    
    return jsonify({'message': 'Account deleted successfully'})

@app.route('/users/<user_id>/follow', methods=['POST'])
def follow(user_id):
    users = load_json('users.json', {})
    data = request.json or {}
    follower = data.get('from')
    if not follower:
        return jsonify({'error': 'Missing follower'}), 400
    f_email = next((k for k,v in users.items() if v.get('id') == follower), None)
    t_email = next((k for k,v in users.items() if v.get('id') == user_id), None)
    if not f_email or not t_email:
        return jsonify({'error': 'User not found'}), 404
    fu = users[f_email]; tu = users[t_email]
    if user_id not in fu.get('following', []):
        fu.setdefault('following', []).append(user_id)
    if follower not in tu.get('followers', []):
        tu.setdefault('followers', []).append(follower)
    users[f_email] = fu; users[t_email] = tu
    save_json('users.json', users)
    return jsonify({'message':'followed'})

@app.route('/users/<user_id>/unfollow', methods=['POST'])
def unfollow(user_id):
    users = load_json('users.json', {})
    data = request.json or {}
    follower = data.get('from')
    if not follower:
        return jsonify({'error': 'Missing follower'}), 400
    f_email = next((k for k,v in users.items() if v.get('id') == follower), None)
    t_email = next((k for k,v in users.items() if v.get('id') == user_id), None)
    if not f_email or not t_email:
        return jsonify({'error': 'User not found'}), 404
    fu = users[f_email]; tu = users[t_email]
    if user_id in fu.get('following', []):
        fu['following'].remove(user_id)
    if follower in tu.get('followers', []):
        tu['followers'].remove(follower)
    users[f_email] = fu; users[t_email] = tu
    save_json('users.json', users)
    return jsonify({'message':'unfollowed'})

# ---------- Posts (public feed) ----------
@app.route('/users', methods=['GET'])
def get_users():
    users = load_json('users.json', {})
    users_list = []
    for email, user_data in users.items():
        users_list.append({
            'id': user_data['id'],
            'name': user_data['name'],
            'email': user_data.get('email', ''), # Use .get() to avoid KeyError
            'role': user_data.get('role', 'public'),
            'avatar': user_data.get('avatar', '/default-avatar.png'),
            'isVerified': user_data.get('isVerified', False)
        })
    return jsonify(users_list)

@app.route('/posts', methods=['GET','POST'])
def posts():
    posts_data = load_json('posts.json', [])
    if request.method == 'POST':
        data = request.json or {}
        pid = str(uuid.uuid4())
        post = {
            'id': pid,
            'userId': data['userId'],
            'content': data.get('content',''),
            'media': data.get('media', []),
            'likes': [],
            'comments': [],
            'timestamp': data.get('timestamp') or datetime.utcnow().isoformat()+'Z'
        }
        posts_data.append(post)
        posts_data.sort(key=lambda p: p.get('timestamp',''), reverse=True)
        save_json('posts.json', posts_data)
        return jsonify(post), 201
    
    # For GET requests, include user information
    users = load_json('users.json', {})
    posts_with_users = []
    
    # Get current user's following list if provided
    current_user_id = request.args.get('userId')
    current_user_following = []
    if current_user_id:
        for email, user in users.items():
            if user.get('id') == current_user_id:
                current_user_following = user.get('following', [])
                break
    
    for post in posts_data:
        post_copy = post.copy()
        # Find user by ID
        user_info = None
        for email, user in users.items():
            if user.get('id') == post['userId']:
                user_info = {
                    'id': user['id'],
                    'name': user.get('name', 'Unknown User'),
                    'avatar': user.get('avatar', '/default-avatar.png'),
                    'role': user.get('role', 'public'),
                    'isVerified': user.get('isVerified', False)
                }
                break
        
        if user_info:
            post_copy['user'] = user_info
        else:
            post_copy['user'] = {
                'id': post['userId'],
                'name': 'Unknown User',
                'avatar': '/default-avatar.png',
                'role': 'public'
            }
        
        # Mark if this post is from a followed user
        post_copy['isFromFollowed'] = post['userId'] in current_user_following
        
        # Also add user info to comments
        if 'comments' in post_copy:
            for comment in post_copy['comments']:
                comment_user_info = None
                for email, user in users.items():
                    if user.get('id') == comment['userId']:
                        comment_user_info = user.get('name', 'Unknown User')
                        break
                comment['userName'] = comment_user_info or 'Unknown User'
        
        posts_with_users.append(post_copy)
    
    # Sort: followed users' posts first, then by timestamp
    # Sort: followed users' posts first, then by timestamp (newest first)
    def sort_key(p):
        is_followed = p.get('isFromFollowed', False)
        ts_str = p.get('timestamp', '')
        ts_val = 0
        if ts_str:
            try:
                # Handle Z notation for python < 3.11 if needed, though fromisoformat usually needs +00:00
                ts = ts_str.replace('Z', '+00:00')
                ts_val = datetime.fromisoformat(ts).timestamp()
            except ValueError:
                ts_val = 0
        return (not is_followed, -ts_val)

    posts_with_users.sort(key=sort_key)
    return jsonify(posts_with_users)

@app.route('/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    posts_data = load_json('posts.json', [])
    data = request.json or {}
    uid = data.get('userId')
    post = next((p for p in posts_data if p['id'] == post_id), None)
    if not post: 
        return jsonify({'error':'Post not found'}), 404
    if uid in post['likes']:
        post['likes'].remove(uid)
    else:
        post['likes'].append(uid)
    save_json('posts.json', posts_data)
    return jsonify({'likes': len(post['likes']), 'liked': uid in post['likes']})

@app.route('/posts/<post_id>/comment', methods=['POST'])
def comment_post(post_id):
    posts_data = load_json('posts.json', [])
    data = request.json or {}
    post = next((p for p in posts_data if p['id'] == post_id), None)
    if not post: 
        return jsonify({'error':'Post not found'}), 404
    post['comments'].append({
        'userId': data['userId'],
        'content': data.get('content',''),
        'timestamp': data.get('timestamp') or datetime.utcnow().isoformat()+'Z'
    })
    save_json('posts.json', posts_data)
    notifs = load_json('notifications.json', {})
    owner = post['userId']
    notifs.setdefault(owner, []).append({'type':'comment','from': data['userId'],'postId': post_id})
    save_json('notifications.json', notifs)
    return jsonify({'message':'Commented'})

@app.route('/posts/<post_id>/comments/<comment_index>', methods=['DELETE'])
def delete_comment(post_id, comment_index):
    posts_data = load_json('posts.json', [])
    data = request.json or {}
    post = next((p for p in posts_data if p['id'] == post_id), None)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    try:
        comment_index = int(comment_index)
        if comment_index < 0 or comment_index >= len(post.get('comments', [])):
            return jsonify({'error': 'Comment not found'}), 404
    except ValueError:
        return jsonify({'error': 'Invalid comment index'}), 400
    
    comment = post['comments'][comment_index]
    if data.get('userId') != comment.get('userId'):
        return jsonify({'error': 'Forbidden'}), 403
    
    post['comments'].pop(comment_index)
    save_json('posts.json', posts_data)
    return jsonify({'message': 'Comment deleted'})

@app.route('/posts/<post_id>', methods=['PUT','PATCH'])
def update_post(post_id):
    posts_data = load_json('posts.json', [])
    data = request.json or {}
    post = next((p for p in posts_data if p['id'] == post_id), None)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    if data.get('userId') != post.get('userId'):
        return jsonify({'error': 'Forbidden'}), 403

    # Update mutable fields
    if 'content' in data:
        post['content'] = data.get('content','')
    if 'media' in data and isinstance(data.get('media'), list):
        post['media'] = data.get('media')
    # Track update time
    post['updatedAt'] = datetime.utcnow().isoformat()+'Z'

    save_json('posts.json', posts_data)
    return jsonify({'message':'Updated','post': post})

@app.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    posts_data = load_json('posts.json', [])
    data = request.json or {}
    post = next((p for p in posts_data if p['id'] == post_id), None)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    if data.get('userId') != post.get('userId'):
        return jsonify({'error': 'Forbidden'}), 403

    posts_data = [p for p in posts_data if p['id'] != post_id]
    save_json('posts.json', posts_data)
    return jsonify({'message': 'Deleted'})

@app.route('/posts/<post_id>/report', methods=['POST'])
def report_post(post_id):
    reports = load_json('reports.json', [])
    data = request.json or {}
    reports.append({
        'postId': post_id,
        'by': data.get('userId'),
        'reason': data.get('reason',''),
        'timestamp': data.get('timestamp') or datetime.utcnow().isoformat()+'Z'
    })
    save_json('reports.json', reports)
    return jsonify({'message':'Reported'})

# ---------- Notifications ----------
@app.route('/notifications/<user_id>', methods=['GET'])
def notifications(user_id):
    notifs = load_json('notifications.json', {})
    user_notifs = notifs.get(user_id, [])
    
    users = load_json('users.json', {})
    def get_name(uid):
        # Optimization: Create a lookup map if performance becomes an issue
        for u in users.values():
            if u['id'] == uid:
                return u['name']
        return uid

    enriched = []
    for n in user_notifs:
        n_copy = n.copy()
        n_copy['fromName'] = get_name(n.get('from'))
        enriched.append(n_copy)
        
    return jsonify(enriched)

@app.route('/notifications/<uid>', methods=['DELETE'])
def clear_notifications(uid):
    notifs = load_json('notifications.json', {})
    if uid in notifs:
        notifs[uid] = [] # Clear the list
        save_json('notifications.json', notifs)
    return jsonify({'message': 'Notifications cleared'})

# ---------- Conversations / DMs ----------
@app.route('/constitution', methods=['GET'])
def get_constitution():
    """Fetch all constitution parts from MongoDB"""
    try:
        parts = list(constitution_col.find({}, {'_id': 0}))
        return jsonify({"parts": parts})
    except Exception as e:
        print(f"Error fetching constitution: {e}")
        # Fallback to JSON file if MongoDB fails
        data = load_json('constitution.json', {"parts": []})
        return jsonify(data)

@app.route('/api/constitution/article/<article_id>', methods=['GET'])
def get_article_by_id(article_id):
    """Fetch a specific article by its ID from MongoDB"""
    try:
        # Query MongoDB for the part containing this article
        part = constitution_col.find_one(
            {"articles.id": article_id},
            {'_id': 0}
        )
        
        if not part:
            return jsonify({'error': f'Article {article_id} not found'}), 404
        
        # Find the specific article within the part
        article_data = None
        for article in part.get('articles', []):
            if article.get('id') == article_id:
                article_data = article
                break
        
        if not article_data:
            return jsonify({'error': f'Article {article_id} not found'}), 404
        
        # Return article with part information
        return jsonify({
            'article': article_data,
            'partTitle': part.get('title', ''),
            'partId': part.get('id', '')
        })
        
    except Exception as e:
        print(f"Error fetching article {article_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/conversations', methods=['GET','POST'])
def conversations():
    convs = load_json('conversations.json', [])
    if request.method == 'POST':
        data = request.json or {}
        users_pair = set(data.get('users', []))
        
        # Check if both users exist and if the requester follows the target user
        users = load_json('users.json', {})
        requester_id = data['users'][0]
        target_id = data['users'][1]
        
        # Find requester
        requester = next((u for k, u in users.items() if u.get('id') == requester_id), None)
        if not requester:
            return jsonify({'error': 'Requester not found'}), 404
        
        # Find target
        target = next((u for k, u in users.items() if u.get('id') == target_id), None)
        if not target:
            return jsonify({'error': 'Target user not found'}), 404
        
        # Check if requester follows target
        if target_id not in requester.get('following', []):
            return jsonify({'error': 'You must follow this user to send a DM'}), 403
        
        for c in convs:
            if set(c.get('users', [])) == users_pair:
                return jsonify(c), 200
        cid = str(uuid.uuid4())
        conv = {'id': cid, 'users': data['users'], 'status': 'accepted', 'messages': []}
        convs.append(conv)
        save_json('conversations.json', convs)
        target = data['users'][1]
        notifs = load_json('notifications.json', {})
        notifs.setdefault(target, []).append({'type':'dm-request','from': data['users'][0], 'convId': cid})
        save_json('notifications.json', notifs)
        return jsonify(conv), 201

    uid = request.args.get('userId')
    if uid:
        return jsonify([c for c in convs if uid in c.get('users', [])])
    return jsonify(convs)

@app.route('/conversations/<conv_id>', methods=['GET'])
def get_conversation(conv_id):
    convs = load_json('conversations.json', [])
    conv = next((c for c in convs if c['id'] == conv_id), None)
    if not conv: 
        return jsonify({'error':'Conversation not found'}), 404
    # Also add participant user info to the conversation
    users_data = load_json('users.json', {})
    conv_users = []
    for user_id in conv['users']:
        # Find the user by ID from the users_data (which is a dictionary with email as key)
        found_user = next((u for k, u in users_data.items() if u['id'] == user_id), None)
        if found_user:
            conv_users.append({
                'id': found_user['id'],
                'name': found_user['name'],
                'avatar': found_user.get('avatar', '/default-avatar.png'),
                'role': found_user.get('role', 'public'),
                'isVerified': found_user.get('isVerified', False)
            })
    conv['participants'] = conv_users
    return jsonify(conv)

@app.route('/conversations/<conv_id>/accept', methods=['POST'])
def accept_conversation(conv_id):
    convs = load_json('conversations.json', [])
    conv = next((c for c in convs if c['id'] == conv_id), None)
    if not conv: 
        return jsonify({'error':'Conversation not found'}), 404
    conv['status'] = 'accepted'
    save_json('conversations.json', convs)
    return jsonify({'message':'Accepted'})

@app.route('/conversations/<conv_id>/message', methods=['POST'])
def message(conv_id):
    convs = load_json('conversations.json', [])
    data = request.json or {}
    conv = next((c for c in convs if c['id'] == conv_id), None)
    if not conv: 
        return jsonify({'error':'Conversation not found'}), 404
    if conv.get('status') != 'accepted':
        return jsonify({'error':'Not allowed'}), 403
    msg = {
        'from': data['from'],
        'content': data.get('content',''),
        'timestamp': data.get('timestamp') or datetime.utcnow().isoformat()+'Z'
    }
    conv.setdefault('messages', []).append(msg)
    save_json('conversations.json', convs)
    recipient = next(uid for uid in conv['users'] if uid != data['from'])
    notifs = load_json('notifications.json', {})
    notifs.setdefault(recipient, []).append({'type':'message', 'from': data['from'], 'convId': conv_id})
    save_json('notifications.json', notifs)
    return jsonify({'message':'Sent','msg': msg})

# ---------- Admin ----------
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({'error': 'Unauthorized: Missing User ID'}), 401
        
        users = load_json('users.json', {})
        # Find user by ID
        user_entry = next((u for u in users.values() if u['id'] == user_id), None)
        
        if not user_entry:
            return jsonify({'error': 'Unauthorized: User not found'}), 401
            
        if user_entry.get('role') != 'admin':
            return jsonify({'error': 'Forbidden: Admins only'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    users = load_json('users.json', {})
    # Return list of all users, excluding passwords
    u_list = []
    for u in users.values():
        print_u = u.copy()
        print_u.pop('password', None)
        u_list.append(print_u)
    return jsonify(u_list)

@app.route('/admin/users/<uid>', methods=['DELETE'])
@admin_required
def admin_delete_user(uid):
    users = load_json('users.json', {})
    key_to_delete = next((k for k, v in users.items() if v['id'] == uid), None)
    if not key_to_delete:
        return jsonify({'error': 'User not found'}), 404
    
    del users[key_to_delete]
    save_json('users.json', users)
    return jsonify({'message': 'User deleted'})

@app.route('/admin/users/<uid>/verify', methods=['POST'])
@admin_required
def admin_verify_user(uid):
    users = load_json('users.json', {})
    key = next((k for k, v in users.items() if v['id'] == uid), None)
    if not key:
        return jsonify({'error': 'User not found'}), 404
    
    # Toggle verification
    current = users[key].get('isVerified', False)
    users[key]['isVerified'] = not current
    save_json('users.json', users)
    return jsonify({'message': 'Status updated', 'isVerified': not current})

# ---------- Verification Requests ----------
@app.route('/verification-request', methods=['POST'])
def verification_request():
    reqs = load_json('verification_requests.json', [])
    
    uid = request.form.get('userId')
    if any(r['userId'] == uid and r['status'] == 'pending' for r in reqs):
        return jsonify({'error': 'You already have a pending confirmation request.'}), 400
        
    name = request.form.get('name')
    email = request.form.get('email')
    bar_code = request.form.get('barCode')
    
    file = request.files.get('document')
    file_url = ''
    if file and file.filename:
        filename = secure_filename(f"verify_{uid}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_url = f"/uploads/{filename}"
    
    new_req = {
        'id': str(uuid.uuid4()),
        'userId': uid,
        'name': name,
        'email': email,
        'barCode': bar_code,
        'documentUrl': file_url,
        'status': 'pending',
        'timestamp': datetime.utcnow().isoformat()
    }
    
    reqs.append(new_req)
    save_json('verification_requests.json', reqs)
    return jsonify({'message': 'Request submitted successfully'}), 201

@app.route('/users/<uid>/verification-status', methods=['GET'])
def get_verification_status(uid):
    reqs = load_json('verification_requests.json', [])
    pending = next((r for r in reqs if r['userId'] == uid and r['status'] == 'pending'), None)
    if pending:
        return jsonify({'status': 'pending'})
    return jsonify({'status': 'none'})

@app.route('/admin/verification-requests', methods=['GET'])
@admin_required
def admin_get_requests():
    reqs = load_json('verification_requests.json', [])
    pending = [r for r in reqs if r['status'] == 'pending']
    return jsonify(pending)

@app.route('/admin/verification-requests/<rid>/approve', methods=['POST'])
@admin_required
def admin_approve_request(rid):
    reqs = load_json('verification_requests.json', [])
    req = next((r for r in reqs if r['id'] == rid), None)
    if not req:
        return jsonify({'error': 'Request not found'}), 404
        
    users = load_json('users.json', {})
    ukey = next((k for k, v in users.items() if v['id'] == req['userId']), None)
    if ukey:
        users[ukey]['isVerified'] = True
        save_json('users.json', users)
    
    req['status'] = 'approved'
    save_json('verification_requests.json', reqs)
    return jsonify({'message': 'Approved'})

@app.route('/admin/verification-requests/<rid>/reject', methods=['POST'])
@admin_required
def admin_reject_request(rid):
    reqs = load_json('verification_requests.json', [])
    req = next((r for r in reqs if r['id'] == rid), None)
    if not req:
        return jsonify({'error': 'Request not found'}), 404
        
    req['status'] = 'rejected'
    save_json('verification_requests.json', reqs)
    return jsonify({'message': 'Rejected'})

if __name__ == '__main__':
    # Run on all interfaces so your frontend can hit it consistently
    app.run(host='0.0.0.0', port=5000, debug=True)

