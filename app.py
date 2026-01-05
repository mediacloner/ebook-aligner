import os
import zipfile
import shutil
import uuid
import threading
import time
import subprocess
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename # Added this import
from align_book import create_bilingual_epub
import logging

# Suppress Werkzeug logs (access logs) to avoid spamming /progress
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def clean_old_uploads(max_age_seconds=7200): # 2 hours
    print("Cleaning old uploads...")
    if not os.path.exists(UPLOAD_FOLDER): return
    now = time.time()
    for item in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, item)
        try:
            if os.path.getmtime(path) < now - max_age_seconds:
                if os.path.isdir(path): shutil.rmtree(path)
                else: os.remove(path)
                print(f"Removed old upload: {item}")
        except Exception as e:
            print(f"Failed to remove {item}: {e}")

# Clean on startup
clean_old_uploads()

# Global dictionary to store job status
# Format: job_id -> { 'status': 'queued'|'processing'|'completed'|'error', 'progress': 0, 'message': '', 'file': path }
active_jobs = {}

def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def find_oebps(root_dir):
    """Finds the folder containing the OPF file."""
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith('.opf'):
                return root
    return root_dir # Fallback

def process_job_worker(job_id, en_path, es_path, job_dir, use_local_ai, output_dir=None, user_config=None):
    try:
        active_jobs[job_id]['status'] = 'processing'
        active_jobs[job_id]['message'] = 'Unzipping files...'
        
        # Unpack
        en_extract = os.path.join(job_dir, 'en_extract')
        es_extract = os.path.join(job_dir, 'es_extract')
        
        unzip_file(en_path, en_extract)
        unzip_file(es_path, es_extract)
        
        # Find OEBPS
        en_oebps = find_oebps(en_extract)
        es_oebps = find_oebps(es_extract)
        
        output_filename = 'bilingual_aligned.epub'
        output_path = os.path.join(job_dir, output_filename)
        
        def update_progress(current, total, msg):
            pct = int((current / total) * 100)
            active_jobs[job_id]['progress'] = pct
            active_jobs[job_id]['message'] = msg
            
        # Run alignment
        config = {}
        if use_local_ai:
            config['use_neural'] = True
            
        # Apply user bilingual configuration
        if user_config:
            from bilingual_config import BilingualConfig, LayoutMode, StyleMode
            
            # Map string values to Enums if necessary, or let BilingualConfig handle basic types
            # BilingualConfig uses Enums for layout_mode and style_mode
            
            # Create config object
            b_conf = BilingualConfig()
            
            # Apply fields safely
            if 'layoutMode' in user_config:
                try: b_conf.layout_mode = LayoutMode(user_config['layoutMode'])
                except: pass
            
            if 'styleMode' in user_config:
                try: b_conf.style_mode = StyleMode(user_config['styleMode'])
                except: pass
                
            if 'columnGap' in user_config:
                b_conf.column_gap_percentage = int(user_config['columnGap'])
                
            if 'enColor' in user_config:
                b_conf.original_color = user_config['enColor']
                
            if 'esColor' in user_config:
                b_conf.translation_color = user_config['esColor']
                
            # Add to main config
            config['bilingual'] = b_conf
            print(f"Applied bilingual config: {b_conf}")
        
        # LLM Verification - 3 modes: none, validate, validate_fix
        verify_mode = user_config.get('verifyLLM', 'validate_fix') if user_config else 'validate_fix'
        # Handle legacy boolean values
        if verify_mode is True:
            verify_mode = 'validate_fix'
        elif verify_mode is False:
            verify_mode = 'none'
        
        config['verify_llm'] = verify_mode != 'none'
        config['verify_mode'] = verify_mode  # none, validate, validate_fix
        config['verify_model'] = 'qwen2.5:7b'
        
        if verify_mode != 'none':
            active_jobs[job_id]['message'] = f'Initializing LLM verification ({verify_mode})...'
            # Auto-install model if needed
            try:
                from llm_verifier import AlignmentVerifier
                verifier = AlignmentVerifier(model='qwen2.5:7b')
                if verifier._ensure_ollama():
                    print(f"LLM verification ready (mode: {verify_mode})")
                else:
                    print("LLM verification unavailable, continuing without it")
                    config['verify_llm'] = False
                    config['verify_mode'] = 'none'
            except Exception as e:
                print(f"LLM verification init failed: {e}")
                config['verify_llm'] = False
                config['verify_mode'] = 'none'
            
        def cancel_check():
            return active_jobs.get(job_id, {}).get('status') == 'cancelled'
            
        result = create_bilingual_epub(en_oebps, es_oebps, output_path, config=config, progress_callback=update_progress, cancel_check=cancel_check)
        
        if active_jobs[job_id]['status'] == 'cancelled':
             active_jobs[job_id]['message'] = 'Job cancelled by user.'
             active_jobs[job_id]['progress'] = 0
             # Clean up job directory
             if os.path.exists(job_dir):
                 try:
                     shutil.rmtree(job_dir)
                     print(f"Cleaned up cancelled job dir: {job_dir}")
                 except Exception as exc:
                     print(f"Error cleaning up job dir: {exc}")
             return
        
        # Format filename based on metadata
        # "title - author (bilingual).epub"
        # eliminate - if dont exist title or author
        
        if isinstance(result, dict):
             title = result.get('title')
             author = result.get('author')
             
             clean_title = (title or "").strip()
             clean_author = (author or "").strip()
             
             if clean_title and clean_author:
                 # Check for hyphens to avoid double hyphens? No, usually valid.
                 base_name = f"{clean_title} - {clean_author}"
             elif clean_title:
                 base_name = clean_title
             elif clean_author:
                 base_name = clean_author
             else:
                 base_name = "bilingual_book"
                 
             # sanitize slightly but keep unicode (e.g. accents)
             # secure_filename might be too aggressive removing spaces/accents.
             # User implies "appear" so maybe readable name.
             # Let's keep it readable but safe for browsers.
             # Actually Flask send_file handles unicode names usually if UTF-8.
             # We just need to ensure no paths.
             base_name = base_name.replace('/', '-').replace('\\', '-')
             
             final_name = f"{base_name}.epub"
        else:
             final_name = 'bilingual_aligned.epub'

        # If output_dir is specified and valid, copy the file there
        saved_location_msg = ""
        if output_dir and os.path.isdir(output_dir):
            try:
                # 1. Main EPUB
                dest_path = os.path.join(output_dir, final_name)
                shutil.copy2(output_path, dest_path)
                saved_location_msg = f"Saved to {os.path.abspath(dest_path)}"
                
                # 2. Fixed EPUB (if exists)
                fixed_src = output_path.replace('.epub', '_fixed.epub')
                if os.path.exists(fixed_src):
                    fixed_dest_name = final_name.replace('.epub', ' (Fixed).epub')
                    fixed_dest = os.path.join(output_dir, fixed_dest_name)
                    shutil.copy2(fixed_src, fixed_dest)
                    saved_location_msg += f"\nFixed version: {fixed_dest_name}"
                
                # 3. Verification Report
                flagged_pairs = result.get('flagged_pairs', []) if isinstance(result, dict) else []
                if flagged_pairs:
                    from llm_verifier import generate_report
                    # Generate verification report
                    report_path = generate_report(output_path, flagged_pairs, total_pairs=0)
                    
                    if report_path and os.path.exists(report_path):
                         report_dest_name = final_name.replace('.epub', ' (Report).md')
                         report_dest = os.path.join(output_dir, report_dest_name)
                         shutil.copy2(report_path, report_dest)
                         saved_location_msg += f"\nReport: {report_dest_name}"

            except Exception as e:
                print(f"Error copying to output dir: {e}")

        active_jobs[job_id]['status'] = 'completed'
        active_jobs[job_id]['progress'] = 100
        active_jobs[job_id]['message'] = f'Complete! {saved_location_msg}'.strip()
        active_jobs[job_id]['file'] = output_path
        active_jobs[job_id]['download_name'] = final_name
        
    except Exception as e:
        active_jobs[job_id]['status'] = 'error'
        active_jobs[job_id]['message'] = str(e)

@app.route('/cancel/<job_id>', methods=['POST'])
def cancel_job(job_id):
    if job_id in active_jobs:
        active_jobs[job_id]['status'] = 'cancelled'
        active_jobs[job_id]['message'] = 'Cancelling...'
        return jsonify({'status': 'cancelled'})
    return jsonify({'error': 'Job not found'}), 404

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/config', methods=['GET'])
def config_page():
    return render_template('config.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'en_file' not in request.files or 'es_file' not in request.files:
        return jsonify({'error': 'Missing files'}), 400
    
    en_file = request.files['en_file']
    es_file = request.files['es_file']
    output_dir = request.form.get('output_dir')
    
    # Create a unique session ID for this job
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    os.makedirs(job_dir)
    
    en_path = os.path.join(job_dir, 'en.epub')
    es_path = os.path.join(job_dir, 'es.epub')
    
    en_file.save(en_path)
    es_file.save(es_path)
    
    # Enforce Local AI (User Request)
    use_local_ai = True
    
    # Initialize job status
    active_jobs[job_id] = {
        'status': 'queued',
        'progress': 0,
        'message': 'Queued...',
        'file': None
    }
    
    # Parse user configuration
    import json
    user_config_json = request.form.get('bilingual_config')
    user_config = {}
    if user_config_json:
        try:
            print(f"Received user config: {user_config_json}")
            user_config = json.loads(user_config_json)
        except Exception as e:
            print(f"Failed to parse user config: {e}")

    # Start thread
    thread = threading.Thread(target=process_job_worker, args=(job_id, en_path, es_path, job_dir, use_local_ai, output_dir, user_config))
    thread.start()
    
    return jsonify({'job_id': job_id})

@app.route('/progress/<job_id>', methods=['GET'])
def get_progress(job_id):
    job = active_jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)

@app.route('/download/<job_id>', methods=['GET'])
def download_file(job_id):
    job = active_jobs.get(job_id)
    if not job or job['status'] != 'completed':
        return "File not ready or job not found", 404
    
    download_name = job.get('download_name', 'bilingual_aligned.epub')
    return send_file(job['file'], as_attachment=True, download_name=download_name)

@app.route('/select-directory', methods=['GET'])
def select_directory():
    try:
        # Use AppleScript to pick folder (macOS only)
        # This will open a dialog on the SERVER (which is the user's machine)
        cmd = "osascript -e 'POSIX path of (choose folder with prompt \"Select Output Directory\")'"
        result = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return jsonify({'path': result})
    except Exception as e:
        # If user cancels or error
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8080)
