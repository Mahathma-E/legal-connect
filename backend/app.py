from flask import Flask, session, request, jsonify, send_from_directory, Response, stream_with_context
from flask_cors import CORS
from flask_mail import Mail
from pymongo import MongoClient
import json, os, uuid, bcrypt
from werkzeug.utils import secure_filename
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import re
import PyPDF2
import io
import email_utils
import firebase_config
import mongo_helpers  # Import MongoDB helpers

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
chat_history_col = db["chat_history"]
call_settings_col = db["call_settings"]  # Call feature settings
call_history_col = db["call_history"]    # Call records
call_requests_col = db["call_requests"]  # NEW: Call requests (pending/accepted/rejected)

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
mail = Mail(app)

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
    text = re.sub(r'(?<!\*)\*(?!\*)|\*{3,}', '', text)

    # Normalize list prefixes (numbers, hyphens, bullets) to '- '
    # This includes 1., 1), *, -, •
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

    # Join the lines back together
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
    """
    Register user with Firebase Authentication
    Frontend creates Firebase user, backend stores user data in MongoDB
    """
    data = request.json or {}

    firebase_uid = data.get('firebaseUid')
    email = data.get('email')
    name = data.get('name')
    
    if not firebase_uid or not email or not name:
        return jsonify({'error': 'Missing fields (firebaseUid, email, name required)'}), 400
    
    # Check if user already exists
    if mongo_helpers.get_user_by_email(email):
        return jsonify({'error': 'Email already exists'}), 409

    uid = str(uuid.uuid4())
    
    # prepare user data
    user_data = {
        'id': uid,
        'firebaseUid': firebase_uid,  # Link to Firebase user
        'name': name,
        'email': email,
        'role': data.get('role', 'public'),
        'avatar': data.get('avatar') or '/default-avatar.png',
        'bio': data.get('bio', ''),
        'bar_code': data.get('bar_code'),  # For lawyers
        'followers': [],
        'following': [],
        'isVerified': False,  # Admin verification for lawyers
        'createdAt': datetime.now().isoformat()
    }
    
    mongo_helpers.create_user(user_data)
    
    print(f"[FIREBASE] Registered user: {email} with Firebase UID: {firebase_uid}")
    
    return jsonify({
        'message': 'Registration successful! Please verify your email.',
        'user': {
            'id': uid,
            'name': name,
            'email': email,
            'role': user_data['role'],
            'avatar': user_data['avatar']
        }
    }), 201


@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """
    Login with Firebase Authentication
    """
    if request.method == 'OPTIONS':
        return '', 200

    try:
        try:
            data = request.get_json() or {}
            firebase_token = data.get('firebaseToken')
        except Exception as e:
            print(f"[AUTH ERROR] Failed to parse request data: {e}", flush=True)
            return jsonify({'error': 'Invalid request data'}), 400

        if not firebase_token:
            return jsonify({'error': 'Missing Firebase token'}), 400

        # Verify Firebase ID token
        try:
            decoded_token, error_msg = firebase_config.verify_firebase_token(firebase_token)
            if not decoded_token:
                print(f"[AUTH ERROR] Token verification error: {error_msg}", flush=True)
                return jsonify({'error': f'Invalid token: {error_msg}'}), 401
        except Exception as e:
            print(f"[AUTH ERROR] verify_firebase_token raised exception: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Authentication service error'}), 500

        email = decoded_token.get('email')
        email_verified = decoded_token.get('email_verified', False)

        print(f"[FIREBASE] Login attempt - email: {email}, verified: {email_verified}")

        # Check if email is verified
        # if not email_verified:
        #    return jsonify({
        #        'error': 'Please verify your email before logging in. Check your inbox for the verification link.',
        #        'emailNotVerified': True,
        #         'email': email
        #    }), 403

        # Get user from MongoDB
        try:
            user_entry = mongo_helpers.get_user_by_email(email)
        except Exception as e:
            print(f"[DB ERROR] MongoDB lookup failed: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Database error'}), 500

        if not user_entry:
            return jsonify({'error': 'User not found. Please register first.'}), 404

        print(f"[FIREBASE] Login successful for: {email}")

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user_entry['id'],
                'email': user_entry['email'],
                'name': user_entry.get('name'),
                'role': user_entry.get('role', 'public'),
                'avatar': user_entry.get('avatar', '/default-avatar.png')
            }
        }), 200
        
    except Exception as e:
        print(f"[CRITICAL ERROR] Message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error'}), 500

# ---------- Email Verification ----------
@app.route('/api/auth/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user's email address using the verification token"""
    
    # Find user by verification token in MongoDB
    user_entry = users_col.find_one({"emailVerificationToken": token})
    
    if not user_entry:
        return jsonify({'error': 'Invalid verification link'}), 400
    
    # Check if token has expired
    if email_utils.is_token_expired(user_entry.get('emailVerificationExpiry')):
        return jsonify({'error': 'Verification link has expired. Please request a new one.'}), 400
    
    # Verify the email
    users_col.update_one(
        {"_id": user_entry["_id"]},
        {"$set": {
            "emailVerified": True,
            "emailVerificationToken": None,
            "emailVerificationExpiry": None
        }}
    )
    
    return jsonify({
        'message': 'Email verified successfully! You can now log in.',
        'success': True
    }), 200

@app.route('/api/auth/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email to user"""
    data = request.json or {}
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    user_entry = mongo_helpers.get_user_by_email(email)
    
    if not user_entry:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if already verified
    if user_entry.get('emailVerified', False):
        return jsonify({'error': 'Email is already verified'}), 400
    
    # Generate new verification token
    verification_token = email_utils.generate_verification_token()
    token_expiry = email_utils.generate_token_expiry(hours=24)
    
    users_col.update_one(
        {"email": email},
        {"$set": {
            "emailVerificationToken": verification_token,
            "emailVerificationExpiry": token_expiry
        }}
    )
    
    # Send verification email
    try:
        email_sent = email_utils.send_verification_email(
            mail,
            email,
            user_entry.get('name'),
            verification_token
        )
        if not email_sent:
            return jsonify({'error': 'Failed to send verification email'}), 500
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return jsonify({'error': 'Failed to send verification email'}), 500
    
    return jsonify({
        'message': 'Verification email sent successfully. Please check your inbox.',
        'success': True
    }), 200

# ---------- Password Reset ----------
@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email to user"""
    data = request.json or {}
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    user_entry = mongo_helpers.get_user_by_email(email)
    
    if not user_entry:
        # Don't reveal if email exists or not (security best practice)
        return jsonify({
            'message': 'If an account with that email exists, a password reset link has been sent.',
            'success': True
        }), 200
    
    # Generate password reset token
    reset_token = email_utils.generate_verification_token()
    token_expiry = email_utils.generate_token_expiry(hours=24)
    
    users_col.update_one(
        {"email": email},
        {"$set": {
            "passwordResetToken": reset_token,
            "passwordResetExpiry": token_expiry
        }}
    )
    
    # Send password reset email
    try:
        email_sent = email_utils.send_password_reset_email(
            mail,
            email,
            user_entry.get('name'),
            reset_token
        )
        if not email_sent:
            print(f"Failed to send password reset email to {email}")
    except Exception as e:
        print(f"Error sending password reset email: {e}")
    
    return jsonify({
        'message': 'If an account with that email exists, a password reset link has been sent.',
        'success': True
    }), 200

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset user's password using the reset token"""
    data = request.json or {}
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and new password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    # Find user by reset token in MongoDB
    user_entry = users_col.find_one({"passwordResetToken": token})
    
    if not user_entry:
        return jsonify({'error': 'Invalid or expired reset link'}), 400
    
    # Check if token has expired
    if email_utils.is_token_expired(user_entry.get('passwordResetExpiry')):
        return jsonify({'error': 'Reset link has expired. Please request a new one.'}), 400
    
    # Hash the new password
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update password and remove reset token
    users_col.update_one(
        {"_id": user_entry["_id"]},
        {"$set": {
            "password": hashed,
            "passwordResetToken": None,
            "passwordResetExpiry": None
        }}
    )
    
    return jsonify({
        'message': 'Password reset successfully! You can now log in with your new password.',
        'success': True
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
    prompt = f"""You are an advanced Legal AI Assistant specializing in Indian Constitutional Law.
Your goal is to provide comprehensive, well-structured, and easy-to-read legal advice.

CRITICAL INTERACTION RULES:
1. SCOPE: Answer ONLY using the Constitution of India.
2. CITATIONS:
   - ALWAYS cite relevant **Case Laws & Precedents** if applicable.
   - Provide the **Case Name**, **Year**, and a **Brief Summary** of the verdict.
   - If no direct case law exists, mention similar hypothetical scenarios.
3. FORMATTING:
   - Use **## Headings** for main topics.
   - Use **### Subheadings** for sections.
   - Use **Bold** (**text**) for key legal terms and emphasis.
   - Use **Bullet points** for lists (normalized to '- ').
   - Use **> Blockquotes** for summarizing laws or acts.

**Context Document:** {document if document else "No specific document provided."}

**User Question:** {message}

Please provide a structured response following the above rules."""   

    # Stream response
    def generate():
        full_response = ""
        try:
            # Use Gemini with streaming enabled
            response_stream = model.generate_content(prompt, stream=True)
            
            for chunk in response_stream:
                if chunk.text:
                    # Clean/Format chunk if needed (streaming formatting is tricky, 
                    # so we might do lightweight cleaning or client-side)
                    # For simplicity, we stream raw text and let client handle markdown.
                    # Use a delimiter if needed, or just raw text.
                    # We'll stream raw text chunks.
                    text_chunk = chunk.text
                    full_response += text_chunk
                    yield text_chunk
            
            # After streaming is done, save to MongoDB
            # We apply the final formatting to the saved entry for consistency
            final_reply = _format_chatbot_reply(full_response)
            
            chat_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "bot_response": final_reply,
                "document_context": document if document else None
            }
            # Need to run DB operation in context or safe manner
            # Since we are in a generator, Flask app context might be tricky if not handled,
            # but usually fine within the request context.
            try:
                chat_history_col.insert_one(chat_entry)
            except Exception as db_e:
                print(f"Error saving chat history: {db_e}")

        except Exception as e:
            print(f"Error generating content from Gemini: {e}")
            yield f"\n\n[Error: {str(e)}]"

    return Response(stream_with_context(generate()), mimetype='text/plain')

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

# ---------- Users ----------
# Search users by name or email
@app.route('/users/search', methods=['GET'])
def search_users():
    """Search users by name or email"""
    try:
        query = request.args.get('q', '').strip().lower()
        
        if not query or len(query) < 2:
            return jsonify([])
            
        # MongoDB regex search
        regex_query = {"$regex": query, "$options": "i"}
        users_found = list(users_col.find({
            "$or": [
                {"name": regex_query},
                {"email": regex_query}
            ]
        }, {'_id': 0}).limit(10))
        
        results = []
        for user_data in users_found:
             results.append({
                'id': user_data.get('id'),
                'name': user_data.get('name'),
                'email': user_data.get('email'),
                'role': user_data.get('role'),
                'avatar': user_data.get('avatar'),
                'isVerified': user_data.get('isVerified', False)
            })
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error searching users: {e}")
        return jsonify([])

# ---------- Profile ----------
@app.route('/profile/<user_id>', methods=['GET','POST'])
def profile(user_id):
    # Find user
    u = mongo_helpers.get_user_by_id(user_id)
    
    if not u:
        return jsonify({'error': 'User not found'}), 404

    if request.method == 'GET':
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
    update_data = {}
    
    for k in ('name','bio','avatar'):
        if k in data:
            update_data[k] = data[k]
    
    if update_data:
        mongo_helpers.update_user(user_id, update_data)
        # Update local object to return
        u.update(update_data)
        
    return jsonify({'message':'updated','user': u})

@app.route('/profile/<user_id>/delete', methods=['DELETE'])
def delete_account(user_id):
    data = request.json or {}
    
    # Find user
    user = mongo_helpers.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify password for security
    password = data.get('password')
    if not password:
        return jsonify({'error': 'Password required for account deletion'}), 400
    
    try:
        # Check password (hashed)
        # Note: In a real migration, make sure legacy passwords are handled
        if 'password' in user:
            if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                # Fallback for plain text legacy (if any)
                if user['password'] != password:
                     return jsonify({'error': 'Invalid password'}), 401
    except Exception:
         # Fallback for legacy
         if user.get('password') != password:
            return jsonify({'error': 'Invalid password'}), 401
    
    # Delete user's posts
    posts_col.delete_many({"userId": user_id})
    
    # Remove user from conversations (optional: or just mark as deleted user)
    # Ideally, we pull the user from the 'users' array in conversations
    conversations_col.update_many(
        {"users": user_id},
        {"$pull": {"users": user_id}}
    )
    
    # Remove user from notifications
    notifications_col.delete_many({"userId": user_id})
    notifications_col.delete_many({"from": user_id}) # Remove optional 'from' notifications
    
    # Remove user from followers/following lists of OTHER users
    # Remove user_id from everyone's following list (people following THIS user)
    users_col.update_many(
        {"following": user_id},
        {"$pull": {"following": user_id}}
    )
    # Remove user_id from everyone's followers list (people THIS user follows)
    users_col.update_many(
         {"followers": user_id},
        {"$pull": {"followers": user_id}}
    )

    # Delete the user
    mongo_helpers.delete_user(user_id)
    
    return jsonify({'message': 'Account deleted successfully'})

@app.route('/users/<user_id>/follow', methods=['POST'])
def follow(user_id):
    data = request.json or {}
    follower_id = data.get('from')
    
    if not follower_id:
        return jsonify({'error': 'Missing follower'}), 400
    
    target_user = mongo_helpers.get_user_by_id(user_id)
    follower_user = mongo_helpers.get_user_by_id(follower_id)
    
    if not target_user or not follower_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Add user_id to follower_user's 'following' list
    if user_id not in follower_user.get('following', []):
        users_col.update_one(
            {"id": follower_id},
            {"$push": {"following": user_id}}
        )

    # Add follower_id to target_user's 'followers' list
    if follower_id not in target_user.get('followers', []):
        users_col.update_one(
            {"id": user_id},
            {"$push": {"followers": follower_id}}
        )
        
    return jsonify({'message':'followed'})

@app.route('/users/<user_id>/unfollow', methods=['POST'])
def unfollow(user_id):
    data = request.json or {}
    follower_id = data.get('from')
    
    if not follower_id:
        return jsonify({'error': 'Missing follower'}), 400
        
    target_user = mongo_helpers.get_user_by_id(user_id)
    follower_user = mongo_helpers.get_user_by_id(follower_id)
    
    if not target_user or not follower_user:
        return jsonify({'error': 'User not found'}), 404
        
    # Remove user_id from follower_user's 'following' list
    users_col.update_one(
        {"id": follower_id},
        {"$pull": {"following": user_id}}
    )

    # Remove follower_id from target_user's 'followers' list
    users_col.update_one(
        {"id": user_id},
        {"$pull": {"followers": follower_id}}
    )
        
    return jsonify({'message':'unfollowed'})

# ---------- Posts (public feed) ----------
@app.route('/users', methods=['GET'])
def get_users():
    users_list = mongo_helpers.get_all_users()
    # Sanitize data
    sanitized = []
    for u in users_list:
        sanitized.append({
            'id': u['id'],
            'name': u['name'],
            'email': u.get('email', ''),
            'role': u.get('role', 'public'),
            'avatar': u.get('avatar', '/default-avatar.png'),
            'isVerified': u.get('isVerified', False)
        })
    return jsonify(sanitized)

@app.route('/posts', methods=['GET','POST'])
def posts():
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
        mongo_helpers.create_post(post)
        return jsonify(post), 201
    
    # For GET requests, include user information
    # Get all posts from MongoDB
    posts_data = mongo_helpers.get_all_posts()
    
    # Get all users to map IDs to Names/Avatars
    all_users = mongo_helpers.get_all_users()
    users_map = {u['id']: u for u in all_users}
    
    posts_with_users = []
    
    # Get current user's following list if provided
    current_user_id = request.args.get('userId')
    current_user_following = []
    if current_user_id and current_user_id in users_map:
        current_user_following = users_map[current_user_id].get('following', [])
    
    for post in posts_data:
        post_copy = post.copy()
        
        # Enrich with user info
        user = users_map.get(post['userId'])
        if user:
            post_copy['user'] = {
                'id': user['id'],
                'name': user.get('name', 'Unknown User'),
                'avatar': user.get('avatar', '/default-avatar.png'),
                'role': user.get('role', 'public'),
                'isVerified': user.get('isVerified', False)
            }
        else:
             post_copy['user'] = {
                'id': post['userId'],
                'name': 'Unknown User',
                'avatar': '/default-avatar.png',
                'role': 'public'
            }
        
        # Mark if this post is from a followed user
        post_copy['isFromFollowed'] = post['userId'] in current_user_following
        
        # Enrich comments with user names and avatars
        if 'comments' in post_copy:
            for comment in post_copy['comments']:
                comment_user = users_map.get(comment['userId'])
                if comment_user:
                    comment['userName'] = comment_user.get('name', 'Unknown User')
                    comment['userAvatar'] = comment_user.get('avatar', '/default-avatar.png')
                    comment['userRole'] = comment_user.get('role', 'public')
                    comment['userVerified'] = comment_user.get('isVerified', False)
                else:
                    comment['userName'] = 'Unknown User'
                    comment['userAvatar'] = '/default-avatar.png'
        
        posts_with_users.append(post_copy)
    
    # Sort: followed users' posts first, then by timestamp (newest first)
    def sort_key(p):
        is_followed = p.get('isFromFollowed', False)
        ts_str = p.get('timestamp', '')
        ts_val = 0
        if ts_str:
            try:
                # Handle Z notation
                ts = ts_str.replace('Z', '+00:00')
                ts_val = datetime.fromisoformat(ts).timestamp()
            except ValueError:
                ts_val = 0
        return (not is_followed, -ts_val)

    posts_with_users.sort(key=sort_key)
    return jsonify(posts_with_users)

@app.route('/posts/<post_id>/like', methods=['POST'])
def like_post(post_id):
    data = request.json or {}
    uid = data.get('userId')
    
    result = mongo_helpers.add_like_to_post(post_id, uid)
    
    if not result:
        return jsonify({'error':'Post not found'}), 404
        
    # Get updated post to return like count
    post = mongo_helpers.get_post_by_id(post_id)
    likes_count = len(post.get('likes', []))
    is_liked = uid in post.get('likes', [])
    
    return jsonify({'likes': likes_count, 'liked': is_liked})

@app.route('/posts/<post_id>/comment', methods=['POST'])
def comment_post(post_id):
    data = request.json or {}
    
    post = mongo_helpers.get_post_by_id(post_id)
    if not post: 
        return jsonify({'error':'Post not found'}), 404
        
    cid = str(uuid.uuid4())
    comment_data = {
        'id': cid,
        'userId': data['userId'],
        'content': data.get('content',''),
        'timestamp': data.get('timestamp') or datetime.utcnow().isoformat()+'Z',
        'parentId': data.get('parentId') # None if top-level
    }
    
    mongo_helpers.add_comment_to_post(post_id, comment_data)
    
    # Create notification for post owner (if not self and top-level)
    owner_id = post['userId']
    if owner_id != data['userId']:
        mongo_helpers.add_notification(owner_id, {
            'type': 'comment',
            'from': data['userId'],
            'postId': post_id,
            'timestamp': datetime.now().isoformat()
        })
        
    # If reply, notify parent comment author
    if data.get('parentId'):
        parent_comment = next((c for c in post.get('comments',[]) if c.get('id') == data['parentId']), None)
        if parent_comment and parent_comment['userId'] != data['userId']:
             mongo_helpers.add_notification(parent_comment['userId'], {
                'type': 'reply',
                'from': data['userId'],
                'postId': post_id,
                'timestamp': datetime.now().isoformat()
            })

    return jsonify({'message':'Commented', 'comment': comment_data})

@app.route('/posts/<post_id>/comments/<comment_id>', methods=['DELETE'])
def delete_comment(post_id, comment_id):
    data = request.json or {}
    post = mongo_helpers.get_post_by_id(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    comments = post.get('comments', [])
    comment = next((c for c in comments if c.get('id') == comment_id), None)
    
    if not comment:
         return jsonify({'error': 'Comment not found'}), 404
    
    # Allow deletion if Owner of Comment OR Owner of Post OR Admin
    requester_id = data.get('userId')
    requester = mongo_helpers.get_user_by_id(requester_id)
    
    is_admin = requester and requester.get('role') == 'admin'
    is_post_owner = post.get('userId') == requester_id
    is_comment_owner = comment.get('userId') == requester_id
    
    if not (is_comment_owner or is_post_owner or is_admin):
        return jsonify({'error': 'Forbidden'}), 403
    
    mongo_helpers.delete_comment_from_post(post_id, comment_id)
    return jsonify({'message': 'Comment deleted'})

@app.route('/posts/<post_id>', methods=['PUT','PATCH'])
def update_post(post_id):
    data = request.json or {}
    post = mongo_helpers.get_post_by_id(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    if data.get('userId') != post.get('userId'):
        return jsonify({'error': 'Forbidden'}), 403

    # Update mutable fields
    update_data = {}
    if 'content' in data:
        update_data['content'] = data.get('content','')
    if 'media' in data and isinstance(data.get('media'), list):
        update_data['media'] = data.get('media')
    # Track update time
    update_data['updatedAt'] = datetime.utcnow().isoformat()+'Z'

    mongo_helpers.update_post(post_id, update_data)
    
    # Return updated post
    updated_post = mongo_helpers.get_post_by_id(post_id)
    return jsonify({'message':'Updated','post': updated_post})

@app.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    data = request.json or {}
    post = mongo_helpers.get_post_by_id(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
        
    requester_id = data.get('userId')
    requester = mongo_helpers.get_user_by_id(requester_id)
    
    if not requester:
         return jsonify({'error': 'User not found'}), 404

    # Allow if owner OR admin
    if requester_id != post.get('userId') and requester.get('role') != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    mongo_helpers.delete_post(post_id)
    return jsonify({'message': 'Deleted'})

@app.route('/posts/<post_id>/report', methods=['POST'])
def report_post(post_id):
    data = request.json or {}
    report_data = {
        'postId': post_id,
        'by': data.get('userId'),
        'reason': data.get('reason',''),
        'timestamp': data.get('timestamp') or datetime.utcnow().isoformat()+'Z'
    }
    mongo_helpers.create_report(report_data)
    return jsonify({'message':'Reported'})

# ---------- Notifications ----------
@app.route('/notifications/<user_id>', methods=['GET'])
def get_notifications(user_id):
    try:
        user_notifs = mongo_helpers.get_notifications_for_user(user_id)
        
        # We need user details to enrich "fromName"
        # Ideally this should be an aggregation, but for now we loop
        enriched = []
        for n in user_notifs:
            n_copy = n.copy()
            if 'from' in n:
                from_user = mongo_helpers.get_user_by_id(n['from'])
                n_copy['fromName'] = from_user.get('name') if from_user else n['from']
            enriched.append(n_copy)
        
        return jsonify(enriched)
    except Exception as e:
        print(f"Error loading notifications: {e}")
        return jsonify([])

@app.route('/notifications/<user_id>', methods=['DELETE'])
def clear_notifications(user_id):
    try:
        mongo_helpers.clear_notifications_for_user(user_id)
        return jsonify({'message': 'Cleared'})
    except Exception as e:
        print(f"Error clearing notifications: {e}")
        return jsonify({'message': 'Error clearing notifications'}), 500

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
    if request.method == 'POST':
        data = request.json or {}
        users_pair = set(data.get('users', []))
        
        if len(users_pair) != 2:
             return jsonify({'error': 'Conversation requires exactly 2 users'}), 400

        # FIX: Use data['users'] directly to ensure order (Requester is index 0)
        # Verify that the list contains unique IDs manually if needed, but set check above handles count
        user_ids = data.get('users', [])
        if len(user_ids) != 2: # Backup check
             return jsonify({'error': 'Invalid users list'}), 400
             
        requester_id = user_ids[0]
        target_id = user_ids[1]

        # Check if both users exist
        requester = mongo_helpers.get_user_by_id(requester_id)
        target = mongo_helpers.get_user_by_id(target_id)

        if not requester:
            return jsonify({'error': 'Requester not found'}), 404
        if not target:
            return jsonify({'error': 'Target user not found'}), 404
        
        # Check if requester follows target (OR if requester is admin)
        if target_id not in requester.get('following', []) and requester.get('role') != 'admin':
            return jsonify({'error': 'You must follow this user to send a DM'}), 403
        
        # Check if conversation already exists
        # We need to find a convo with exactly these 2 users
        # MongoDB query for arrays is tricky for "exact set", but we can query where both exist
        existing_convs = list(mongo_helpers.conversations_col.find({
            "users": {"$all": user_ids},
            "$where": "this.users.length == 2"
        }))
        
        if existing_convs:
            # Return existing (serialize mongo id if needed, but 'id' field should be present)
            existing = existing_convs[0]
            if '_id' in existing: del existing['_id']
            return jsonify(existing), 200

        cid = str(uuid.uuid4())
        conv = {'id': cid, 'users': user_ids, 'status': 'accepted', 'messages': []}
        mongo_helpers.create_conversation(conv)
        
        mongo_helpers.add_notification(target_id, {'type':'dm-request','from': requester_id, 'convId': cid})

        return jsonify(conv), 201

    uid = request.args.get('userId')
    if uid:
        convs = mongo_helpers.get_conversations_for_user(uid)
        return jsonify(convs)
    
    # Admin viewing all? Or just empty list
    return jsonify([])

@app.route('/conversations/<conv_id>', methods=['GET'])
def get_conversation(conv_id):
    conv = mongo_helpers.get_conversation_by_id(conv_id)
    if not conv: 
        return jsonify({'error':'Conversation not found'}), 404
    
    # Also add participant user info to the conversation
    conv_users = []
    for user_id in conv['users']:
        found_user = mongo_helpers.get_user_by_id(user_id)
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
    conv = mongo_helpers.get_conversation_by_id(conv_id)
    if not conv: 
        return jsonify({'error':'Conversation not found'}), 404
        
    mongo_helpers.update_conversation(conv_id, {'status': 'accepted'})
    return jsonify({'message':'Accepted'})

@app.route('/conversations/<conv_id>/message', methods=['POST'])
def message(conv_id):
    data = request.json or {}
    conv = mongo_helpers.get_conversation_by_id(conv_id)
    
    if not conv: 
        return jsonify({'error':'Conversation not found'}), 404
    if conv.get('status') != 'accepted':
        return jsonify({'error':'Not allowed'}), 403
    msg = {
        'from': data['from'],
        'content': data.get('content',''),
        'timestamp': data.get('timestamp') or datetime.utcnow().isoformat()+'Z'
    }
    mongo_helpers.add_message_to_conversation(conv_id, msg)
    
    recipient = next((uid for uid in conv['users'] if uid != data['from']), None)
    if recipient:
        mongo_helpers.add_notification(recipient, {'type':'message', 'from': data['from'], 'convId': conv_id})
        
    return jsonify({'message':'Sent','msg': msg})

# ---------- Admin ----------
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-Id')
        if not user_id:
            return jsonify({'error': 'Unauthorized: Missing User ID'}), 401
        
        user_entry = mongo_helpers.get_user_by_id(user_id)
        
        if not user_entry:
            return jsonify({'error': 'Unauthorized: User not found'}), 401
            
        if user_entry.get('role') != 'admin':
            return jsonify({'error': 'Forbidden: Admins only'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_get_users():
    users_list = mongo_helpers.get_all_users()
    # Return list of all users, excluding passwords
    u_list = []
    for u in users_list:
        print_u = u.copy()
        print_u.pop('password', None)
        u_list.append(print_u)
    return jsonify(u_list)

@app.route('/admin/users/<uid>', methods=['DELETE'])
@admin_required
def admin_delete_user(uid):
    user = mongo_helpers.get_user_by_id(uid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    mongo_helpers.delete_user(uid)
    return jsonify({'message': 'User deleted'})

@app.route('/admin/users/<uid>/verify', methods=['POST'])
@admin_required
def admin_verify_user(uid):
    user = mongo_helpers.get_user_by_id(uid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Toggle verification
    current = user.get('isVerified', False)
    mongo_helpers.update_user(uid, {'isVerified': not current})
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
        
    user = mongo_helpers.get_user_by_id(req['userId'])
    if user:
        mongo_helpers.update_user(user['id'], {'isVerified': True})
    
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

# ---------- Paid Calling Feature ----------

# Helper function: Check mutual follow
def check_mutual_follow(user1_id, user2_id):
    """Check if two users follow each other"""
    try:
        user1 = mongo_helpers.get_user_by_id(user1_id)
        user2 = mongo_helpers.get_user_by_id(user2_id)
        
        if not user1 or not user2:
            return False
        
        # Check mutual follow
        user1_follows_user2 = user2_id in user1.get('following', [])
        user2_follows_user1 = user1_id in user2.get('following', [])
        
        return user1_follows_user2 and user2_follows_user1
    except Exception as e:
        print(f"Error checking mutual follow: {e}")
        return False

# Old call endpoints removed - replaced with Call Request & Accept feature below

# 5. Admin - Get call settings
@app.route('/api/admin/call-settings', methods=['GET'])
def get_call_settings():
    """Get current call settings (Admin only)"""
    try:
        settings = call_settings_col.find_one({}, {'_id': 0})
        
        if not settings:
            return jsonify({'error': 'Settings not found'}), 404
        
        # Convert datetime to ISO format
        if 'updated_at' in settings:
            settings['updated_at'] = settings['updated_at'].isoformat()
        
        return jsonify(settings)
        
    except Exception as e:
        print(f"Error getting settings: {e}")
        return jsonify({'error': str(e)}), 500

# 6. Admin - Update call settings
@app.route('/api/admin/call-settings', methods=['PUT'])
def update_call_settings():
    """Update call settings (Admin only)"""
    try:
        data = request.json
        admin_id = data.get('admin_id')  # In production, get from session/token
        
        update_data = {}
        
        if 'call_price' in data:
            update_data['call_price'] = int(data['call_price'])
        
        if 'call_duration' in data:
            update_data['call_duration'] = int(data['call_duration'])
        
        if 'feature_enabled' in data:
            update_data['feature_enabled'] = bool(data['feature_enabled'])
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        update_data['updated_at'] = datetime.now()
        update_data['updated_by'] = admin_id or 'admin'
        
        # Update settings
        result = call_settings_col.update_one(
            {},
            {"$set": update_data},
            upsert=True
        )
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully',
            'updated_fields': list(update_data.keys())
        })
        
    except Exception as e:
        print(f"Error updating settings: {e}")
        return jsonify({'error': str(e)}), 500

# 7. Admin - Get all call history
@app.route('/api/admin/call-history', methods=['GET'])
def admin_call_history():
    """Get all call history with filters (Admin only)"""
    try:
        # Get query parameters
        limit = request.args.get('limit', 100, type=int)
        status = request.args.get('status')  # completed, active, cancelled
        
        # Build query
        query = {}
        if status:
            query['status'] = status
        
        # Fetch calls
        calls = list(call_history_col.find(
            query,
            {'_id': 0}
        ).sort("started_at", -1).limit(limit))
        
        # Convert datetime to ISO format
        for call in calls:
            if 'started_at' in call:
                call['started_at'] = call['started_at'].isoformat()
            if 'ended_at' in call and call['ended_at']:
                call['ended_at'] = call['ended_at'].isoformat()
        
        # Calculate statistics
        total_calls = call_history_col.count_documents({})
        total_revenue = sum(call.get('amount', 0) for call in calls)
        
        return jsonify({
            'success': True,
            'total_calls': total_calls,
            'total_revenue': total_revenue,
            'count': len(calls),
            'history': calls
        })
        
    except Exception as e:
        print(f"Error getting admin call history: {e}")
        return jsonify({'error': str(e)}), 500

# ---------- Mock Payment (For Demo) ----------
@app.route('/api/payment/mock', methods=['POST'])
def mock_payment():
    """Mock payment endpoint - always succeeds for demo purposes"""
    try:
        data = request.json
        user_id = data.get('user_id')
        amount = data.get('amount', 20)
        purpose = data.get('purpose', 'call_payment')
        
        # Generate mock transaction ID
        transaction_id = f"mock_txn_{uuid.uuid4()}"
        
        # Always return success
        return jsonify({
            'success': True,
            'message': 'Mock payment successful',
            'transaction_id': transaction_id,
            'amount': amount,
            'purpose': purpose,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error in mock payment: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Helper: Check mutual follow
# Removed duplicate check_mutual_follow function
# It was defined twice in the original file


# 1. Check Eligibility
@app.route('/api/call/check-eligibility', methods=['POST'])
def check_call_eligibility():
    """Check if user can send call request"""
    try:
        data = request.json
        caller_id = data.get('caller_id')
        receiver_id = data.get('receiver_id')
        
        if not caller_id or not receiver_id:
            return jsonify({'eligible': False, 'reason': 'Missing user IDs'}), 400
        
        # Check mutual follow
        mutual_follow = check_mutual_follow(caller_id, receiver_id)
        if not mutual_follow:
            return jsonify({
                'eligible': False,
                'reason': 'Both users must follow each other to enable calling',
                'mutual_follow': False
            })
        
        # Get call settings
        settings = call_settings_col.find_one()
        if not settings or not settings.get('feature_enabled', True):
            return jsonify({'eligible': False, 'reason': 'Calling feature is currently disabled'})
        
        call_price = settings.get('call_price', 20)
        call_duration = settings.get('call_duration', 10)
        
        # Check wallet
        if caller_wallet < call_price:
            return jsonify({
                'eligible': False,
                'reason': f'Insufficient balance. Required: ₹{call_price}, Available: ₹{caller_wallet}',
                'wallet_balance': caller_wallet,
                'call_price': call_price
            })
        
        return jsonify({
            'eligible': True,
            'mutual_follow': True,
            'wallet_balance': caller_wallet,
            'call_price': call_price,
            'call_duration': call_duration
        })
        
    except Exception as e:
        print(f"Error checking eligibility: {e}")
        return jsonify({'eligible': False, 'reason': 'Server error'}), 500

# 2. Create Call Request
@app.route('/api/call/request', methods=['POST'])
def create_call_request():
    """Create a new call request"""
    try:
        data = request.json
        caller_id = data.get('caller_id')
        receiver_id = data.get('receiver_id')
        
        # Check mutual follow
        if not check_mutual_follow(caller_id, receiver_id):
            return jsonify({'success': False, 'error': 'Mutual follow required'}), 400
        
        # Get settings
        settings = call_settings_col.find_one()
        call_price = settings.get('call_price', 20)
        call_duration = settings.get('call_duration', 10)
        
        # Check for existing pending request
        existing = call_requests_col.find_one({
            'caller_id': caller_id,
            'receiver_id': receiver_id,
            'status': 'pending'
        })
        
        if existing:
            return jsonify({'success': False, 'error': 'Pending request already exists'}), 400
        
        # Create request
        request_id = str(uuid.uuid4())
        call_request = {
            'request_id': request_id,
            'caller_id': caller_id,
            'receiver_id': receiver_id,
            'status': 'pending',
            'amount': call_price,
            'duration_minutes': call_duration,
            'created_at': datetime.utcnow(),
            'responded_at': None,
            'started_at': None,
            'ended_at': None,
            'actual_duration': None,
            'payment_status': 'pending'
        }
        
        call_requests_col.insert_one(call_request)
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'message': 'Call request sent',
            'status': 'pending'
        })
        
    except Exception as e:
        print(f"Error creating call request: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 3. Get Incoming Requests
@app.route('/api/call/incoming/<user_id>', methods=['GET'])
def get_incoming_requests(user_id):
    """Get pending incoming call requests"""
    try:
        requests = list(call_requests_col.find({
            'receiver_id': user_id,
            'status': 'pending'
        }, {'_id': 0}).sort('created_at', -1))
        
        # Add caller info
        users = load_json('users.json', {})
        for req in requests:
            for email, user_data in users.items():
                if user_data.get('id') == req['caller_id']:
                    req['caller_info'] = {
                        'name': user_data.get('name'),
                        'avatar': user_data.get('avatar'),
                        'role': user_data.get('role'),
                        'isVerified': user_data.get('isVerified', False)
                    }
                    break
        
        return jsonify({'success': True, 'requests': requests, 'count': len(requests)})
        
    except Exception as e:
        print(f"Error getting incoming requests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 4. Get Outgoing Requests
@app.route('/api/call/outgoing/<user_id>', methods=['GET'])
def get_outgoing_requests(user_id):
    """Get pending outgoing call requests"""
    try:
        requests = list(call_requests_col.find({
            'caller_id': user_id,
            'status': 'pending'
        }, {'_id': 0}).sort('created_at', -1))
        
        # Add receiver info
        users = load_json('users.json', {})
        for req in requests:
            for email, user_data in users.items():
                if user_data.get('id') == req['receiver_id']:
                    req['receiver_info'] = {
                        'name': user_data.get('name'),
                        'avatar': user_data.get('avatar'),
                        'role': user_data.get('role'),
                        'isVerified': user_data.get('isVerified', False)
                    }
                    break
        
        return jsonify({'success': True, 'requests': requests, 'count': len(requests)})
        
    except Exception as e:
        print(f"Error getting outgoing requests: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 5. Accept Call Request
@app.route('/api/call/accept/<request_id>', methods=['POST'])
def accept_call_request(request_id):
    """Accept incoming call request"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        call_request = call_requests_col.find_one({'request_id': request_id})
        
        if not call_request:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        if call_request['receiver_id'] != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        if call_request['status'] != 'pending':
            return jsonify({'success': False, 'error': f'Request is already {call_request["status"]}'}), 400
        
        # Update request to accepted (payment already handled via mock payment)
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=call_request['duration_minutes'])
        
        call_requests_col.update_one(
            {'request_id': request_id},
            {
                '$set': {
                    'status': 'accepted',
                    'responded_at': start_time,
                    'started_at': start_time,
                    'payment_status': 'completed'
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': 'Call accepted',
            'status': 'accepted',
            'call_session': {
                'request_id': request_id,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': call_request['duration_minutes']
            }
        })
        
    except Exception as e:
        print(f"Error accepting call: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# 6. Reject Call Request
@app.route('/api/call/reject/<request_id>', methods=['POST'])
def reject_call_request(request_id):
    """Reject incoming call request"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        call_request = call_requests_col.find_one({'request_id': request_id})
        
        if not call_request:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        if call_request['receiver_id'] != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        if call_request['status'] != 'pending':
            return jsonify({'success': False, 'error': f'Request is {call_request["status"]}'}), 400
        
        call_requests_col.update_one(
            {'request_id': request_id},
            {'$set': {'status': 'rejected', 'responded_at': datetime.utcnow()}}
        )
        
        return jsonify({'success': True, 'message': 'Call rejected'})
        
    except Exception as e:
        print(f"Error rejecting call: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 7. Cancel Call Request
@app.route('/api/call/cancel/<request_id>', methods=['POST'])
def cancel_call_request(request_id):
    """Cancel outgoing call request"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        call_request = call_requests_col.find_one({'request_id': request_id})
        
        if not call_request:
            return jsonify({'success': False, 'error': 'Request not found'}), 404
        
        if call_request['caller_id'] != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        if call_request['status'] != 'pending':
            return jsonify({'success': False, 'error': 'Cannot cancel'}), 400
        
        call_requests_col.update_one(
            {'request_id': request_id},
            {'$set': {'status': 'cancelled', 'responded_at': datetime.utcnow()}}
        )
        
        return jsonify({'success': True, 'message': 'Request cancelled'})
        
    except Exception as e:
        print(f"Error cancelling: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 8. End Call
@app.route('/api/call/end', methods=['POST'])
def end_call():
    """End active call session"""
    try:
        data = request.json
        request_id = data.get('request_id')
        
        call_request = call_requests_col.find_one({'request_id': request_id})
        
        if not call_request or call_request['status'] != 'accepted':
            return jsonify({'success': False, 'error': 'No active call'}), 400
        
        started_at = call_request['started_at']
        ended_at = datetime.utcnow()
        actual_duration = (ended_at - started_at).total_seconds() / 60
        
        call_requests_col.update_one(
            {'request_id': request_id},
            {
                '$set': {
                    'status': 'ended',
                    'ended_at': ended_at,
                    'actual_duration': round(actual_duration, 2)
                }
            }
        )
        
        # Save to history
        call_history_col.insert_one({
            'caller_id': call_request['caller_id'],
            'receiver_id': call_request['receiver_id'],
            'amount': call_request['amount'],
            'duration_minutes': call_request['duration_minutes'],
            'actual_duration': round(actual_duration, 2),
            'status': 'completed',
            'started_at': started_at,
            'ended_at': ended_at,
            'payment_status': call_request['payment_status']
        })
        
        return jsonify({
            'success': True,
            'actual_duration': round(actual_duration, 2),
            'ended_at': ended_at.isoformat()
        })
        
    except Exception as e:
        print(f"Error ending call: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 9. Get Active Call
@app.route('/api/call/active/<user_id>', methods=['GET'])
def get_active_call(user_id):
    """Get active call session"""
    try:
        active_call = call_requests_col.find_one({
            '$or': [{'caller_id': user_id}, {'receiver_id': user_id}],
            'status': 'accepted'
        }, {'_id': 0})
        
        if not active_call:
            return jsonify({'success': True, 'active_call': None})
        
        started_at = active_call['started_at']
        duration_minutes = active_call['duration_minutes']
        end_time = started_at + timedelta(minutes=duration_minutes)
        remaining_seconds = (end_time - datetime.utcnow()).total_seconds()
        
        if remaining_seconds <= 0:
            # Auto-end
            end_call()
            return jsonify({'success': True, 'active_call': None, 'auto_ended': True})
        
        # Add other user info
        users = load_json('users.json', {})
        other_user_id = active_call['receiver_id'] if active_call['caller_id'] == user_id else active_call['caller_id']
        
        for email, user_data in users.items():
            if user_data.get('id') == other_user_id:
                active_call['other_user'] = {
                    'name': user_data.get('name'),
                    'avatar': user_data.get('avatar'),
                    'role': user_data.get('role')
                }
                break
        
        active_call['remaining_seconds'] = int(remaining_seconds)
        active_call['end_time'] = end_time.isoformat()
        
        return jsonify({'success': True, 'active_call': active_call})
        
    except Exception as e:
        print(f"Error getting active call: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 10. Get Call History (Keep existing)
@app.route('/api/call/history/<user_id>', methods=['GET'])
def get_call_history(user_id):
    """Get call history for user"""
    try:
        limit = int(request.args.get('limit', 50))
        
        history = list(call_history_col.find({
            '$or': [{'caller_id': user_id}, {'receiver_id': user_id}]
        }, {'_id': 0}).sort('started_at', -1).limit(limit))
        
        return jsonify({'success': True, 'history': history, 'count': len(history)})
        
    except Exception as e:
        print(f"Error getting call history: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



