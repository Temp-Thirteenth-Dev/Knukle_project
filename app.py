import os
from flask import Flask, render_template, request, jsonify
import tempfile
from auth_system import KnuckleAuthSystem

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

auth_system = KnuckleAuthSystem()

@app.route('/')
def index():
    return render_template('index.html')

def save_temp_image(file):
    if not file:
        return None
    # Use generic temp file to avoid extension issues
    fd, path = tempfile.mkstemp(suffix='.bmp')
    with os.fdopen(fd, 'wb') as f:
        f.write(file.read())
    return path

@app.route('/api/register', methods=['POST'])
def register():
    user_id = request.form.get('user_id')
    file = request.files.get('image')
    
    if not user_id or not file:
        return jsonify({'success': False, 'message': 'User ID and Image are required!'})
        
    temp_path = save_temp_image(file)
    if not temp_path:
        return jsonify({'success': False, 'message': 'Invalid image file!'})

    success, message = auth_system.register_user(user_id, temp_path)
    os.remove(temp_path)
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/verify', methods=['POST'])
def verify():
    user_id = request.form.get('user_id')
    file = request.files.get('image')
    
    if not user_id or not file:
        return jsonify({'success': False, 'message': 'User ID and Image are required!'})
        
    temp_path = save_temp_image(file)
    if not temp_path:
        return jsonify({'success': False, 'message': 'Invalid image file!'})

    success, score, message = auth_system.verify_user(user_id, temp_path)
    os.remove(temp_path)
    
    return jsonify({'success': success, 'message': message, 'score': score})

@app.route('/api/visualize', methods=['POST'])
def visualize():
    user_id = request.form.get('user_id')
    file = request.files.get('image')
    
    if not user_id or not file:
        return jsonify({'success': False, 'message': 'User ID and Image are required for visualization!'})
        
    temp_path = save_temp_image(file)
    if not temp_path:
        return jsonify({'success': False, 'message': 'Invalid image file!'})

    success, img_str_or_msg, matches_count = auth_system.visualize_match_web(user_id, temp_path)
    os.remove(temp_path)
    
    if success:
        return jsonify({'success': True, 'image': img_str_or_msg, 'matches': matches_count})
    else:
        return jsonify({'success': False, 'message': img_str_or_msg})

if __name__ == '__main__':
    # Default Render port is usually 10000 or dynamically bound to PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
