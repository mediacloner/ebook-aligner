import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
import zipfile

from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for

from align_book import create_bilingual_epub
from aligner.config import AlignerConfig

logging.getLogger("werkzeug").setLevel(logging.WARNING)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def clean_old_uploads(max_age_seconds: int = 7200) -> None:
    if not os.path.exists(UPLOAD_FOLDER):
        return
    now = time.time()
    for item in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, item)
        try:
            if os.path.getmtime(path) < now - max_age_seconds:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
        except Exception as exc:
            print(f"Failed to remove {item}: {exc}")


clean_old_uploads()

active_jobs: dict = {}


def unzip_file(zip_path: str, extract_to: str) -> None:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def find_oebps(root_dir: str) -> str:
    for root, _dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith(".opf"):
                return root
    return root_dir


def process_job_worker(
    job_id: str,
    en_path: str,
    es_path: str,
    job_dir: str,
    output_dir: str | None,
    user_config: dict | None = None,
) -> None:
    try:
        active_jobs[job_id]["status"] = "processing"
        active_jobs[job_id]["message"] = "Unzipping files..."

        en_extract = os.path.join(job_dir, "en_extract")
        es_extract = os.path.join(job_dir, "es_extract")
        unzip_file(en_path, en_extract)
        unzip_file(es_path, es_extract)

        en_oebps = find_oebps(en_extract)
        es_oebps = find_oebps(es_extract)

        output_path = os.path.join(job_dir, "tandem.epub")

        def update_progress(current, total, msg):
            pct = int((current / total) * 100) if total else 0
            active_jobs[job_id]["progress"] = pct
            active_jobs[job_id]["message"] = msg

        def cancel_check():
            return active_jobs.get(job_id, {}).get("status") == "cancelled"

        user_config = user_config or {}
        config = {
            "use_neural": user_config.get("useNeural", True) is not False,
            "bypass_alignment": bool(user_config.get("bypassAlignment", False)),
            "local_mode": bool(user_config.get("localMode", False)),
            "word_budget_split": user_config.get("wordBudgetSplit", True) is not False,
        }
        output_mode = user_config.get("outputMode")
        if isinstance(output_mode, str) and output_mode.strip().lower() in ("inline", "footnote"):
            config["output_mode"] = output_mode.strip().lower()
        target_chunk_words = user_config.get("targetChunkWords")
        if isinstance(target_chunk_words, int) and target_chunk_words > 0:
            config["target_chunk_words"] = target_chunk_words
        result = create_bilingual_epub(
            en_oebps, es_oebps, output_path, config=config,
            progress_callback=update_progress, cancel_check=cancel_check,
        )

        if active_jobs[job_id]["status"] == "cancelled":
            active_jobs[job_id]["message"] = "Job cancelled by user."
            active_jobs[job_id]["progress"] = 0
            if os.path.exists(job_dir):
                shutil.rmtree(job_dir, ignore_errors=True)
            return

        title = (result or {}).get("title") if isinstance(result, dict) else None
        author = (result or {}).get("author") if isinstance(result, dict) else None
        title = (title or "").strip()
        author = (author or "").strip()
        if title and author:
            base_name = f"{title} - {author}"
        elif title:
            base_name = title
        elif author:
            base_name = author
        else:
            base_name = "tandem_book"
        base_name = base_name.replace("/", "-").replace("\\", "-")
        final_name = f"{base_name} (Tandem).epub"

        saved_msg = ""
        delivered_to_output_dir = False
        dest_path: str | None = None
        normalized_dir: str | None = None
        if output_dir:
            normalized_dir = os.path.abspath(os.path.expanduser(output_dir.strip()))
            print(f"[job {job_id}] Output dir requested: {output_dir!r} -> {normalized_dir!r}")
            try:
                os.makedirs(normalized_dir, exist_ok=True)
            except OSError as exc:
                saved_msg = f"Could not create output dir {normalized_dir}: {exc}"
                print(f"[job {job_id}] {saved_msg}")
                normalized_dir = None

        if normalized_dir and os.path.isdir(normalized_dir):
            try:
                dest_path = os.path.join(normalized_dir, final_name)
                shutil.copy2(output_path, dest_path)
                saved_msg = f"Saved to {dest_path}"
                delivered_to_output_dir = True
                print(f"[job {job_id}] {saved_msg}")
            except Exception as exc:
                saved_msg = f"Save failed: {exc}"
                print(f"[job {job_id}] Error copying to output dir: {exc}")

        # Drop the large transient artefacts now that we don't need them. Either
        # the EPUB has been copied to the user's output_dir (so the whole job
        # folder is disposable) or we only keep the final tandem.epub for the
        # /download route and discard the extracts and source EPUBs.
        if delivered_to_output_dir and dest_path:
            shutil.rmtree(job_dir, ignore_errors=True)
            output_path = dest_path
        else:
            for path in (en_extract, es_extract, en_path, es_path):
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                    elif os.path.isfile(path):
                        os.remove(path)
                except Exception as exc:
                    print(f"Cleanup warning ({path}): {exc}")

        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["progress"] = 100
        active_jobs[job_id]["message"] = f"Complete! {saved_msg}".strip()
        active_jobs[job_id]["file"] = output_path
        active_jobs[job_id]["download_name"] = final_name
    except Exception as exc:
        active_jobs[job_id]["status"] = "error"
        active_jobs[job_id]["message"] = str(exc)


@app.route("/cancel/<job_id>", methods=["POST"])
def cancel_job(job_id):
    if job_id in active_jobs:
        active_jobs[job_id]["status"] = "cancelled"
        active_jobs[job_id]["message"] = "Cancelling..."
        return jsonify({"status": "cancelled"})
    return jsonify({"error": "Job not found"}), 404


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/config", methods=["GET"])
def config_page():
    return render_template("config.html")


@app.route("/status", methods=["GET"])
def status():
    cfg = AlignerConfig.from_env()
    return jsonify({
        "openai_key": bool(cfg.openai_api_key),
        "openai_model": cfg.openai_model,
        "aligner_use_llm": cfg.adjudicator_enabled,
        "adjudicator": cfg.has_llm(),
    })


@app.route("/upload", methods=["POST"])
def upload_files():
    if "en_file" not in request.files or "es_file" not in request.files:
        return jsonify({"error": "Missing files"}), 400

    en_file = request.files["en_file"]
    es_file = request.files["es_file"]
    output_dir = request.form.get("output_dir")

    user_config: dict = {}
    raw_config = request.form.get("bilingual_config")
    if raw_config:
        try:
            parsed = json.loads(raw_config)
            if isinstance(parsed, dict):
                user_config = parsed
        except json.JSONDecodeError:
            pass

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_FOLDER, job_id)
    os.makedirs(job_dir)

    en_path = os.path.join(job_dir, "en.epub")
    es_path = os.path.join(job_dir, "es.epub")
    en_file.save(en_path)
    es_file.save(es_path)

    active_jobs[job_id] = {"status": "queued", "progress": 0, "message": "Queued...", "file": None}
    thread = threading.Thread(
        target=process_job_worker,
        args=(job_id, en_path, es_path, job_dir, output_dir, user_config),
    )
    thread.start()
    return jsonify({"job_id": job_id})


@app.route("/progress/<job_id>", methods=["GET"])
def get_progress(job_id):
    job = active_jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(job)


@app.route("/download/<job_id>", methods=["GET"])
def download_file(job_id):
    job = active_jobs.get(job_id)
    if not job or job["status"] != "completed":
        return "File not ready or job not found", 404
    download_name = job.get("download_name", "tandem.epub")
    return send_file(job["file"], as_attachment=True, download_name=download_name)


def _pick_directory_command() -> list[str] | None:
    if sys.platform == "darwin":
        return [
            "osascript",
            "-e",
            'POSIX path of (choose folder with prompt "Select Output Directory")',
        ]
    if shutil.which("zenity"):
        return ["zenity", "--file-selection", "--directory", "--title=Select Output Directory"]
    if shutil.which("kdialog"):
        return ["kdialog", "--getexistingdirectory", os.path.expanduser("~")]
    return None


@app.route("/select-directory", methods=["GET"])
def select_directory():
    cmd = _pick_directory_command()
    if cmd is None:
        return jsonify({
            "error": "No folder picker available. Install zenity or kdialog, or type the path manually.",
        }), 501
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Folder picker timed out."}), 504
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 500
    if result.returncode != 0:
        # User cancelled the dialog — not an error.
        return jsonify({"path": ""})
    path = result.stdout.strip()
    return jsonify({"path": path})


if __name__ == "__main__":
    app.run(debug=True, port=8080)
