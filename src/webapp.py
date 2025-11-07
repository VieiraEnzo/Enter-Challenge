from flask import Flask, render_template, request, Response, send_file, jsonify
import json
import threading
import queue
import os
import time
import logging
from pathlib import Path
from src.main import process_dataset
import traceback

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"), static_folder=str(Path(__file__).parent / "static"))

# Disable Flask's request logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Shared storage for results (simpler than queues)
processing_results = {}
processing_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    data = request.form
    directory = data.get('directory')
    if not directory or not os.path.isdir(directory):
        return ("Invalid directory", 400)

    session_id = str(os.getpid())
    
    # Initialize storage for this session
    processing_results[session_id] = []
    processing_status[session_id] = {"done": False, "error": None}

    # output file path
    output_path = os.path.join(directory, 'resultados.json')

    def worker():
        try:
            # Create a queue to collect results
            q = queue.Queue()
            
            # Start a background thread to collect results as they arrive
            def collector():
                while True:
                    try:
                        item = q.get(timeout=0.1)
                        if item.get('type') in ('finished', 'done'):
                            processing_status[session_id]["done"] = True
                            break
                        processing_results[session_id].append(item)
                    except queue.Empty:
                        # Check if processing is done
                        if processing_status[session_id].get("done"):
                            break
                        continue
            
            collector_thread = threading.Thread(target=collector, daemon=True)
            collector_thread.start()
            
            # Process in main worker thread
            process_dataset(directory, progress_queue=q, output_path=output_path)
            
            # Wait for collector to finish
            collector_thread.join(timeout=5)
            
        except Exception as e:
            print("\n" + "="*50)
            print(">>> ERROR IN WORKER THREAD <<<")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(traceback.format_exc())
            print("="*50 + "\n")
            processing_status[session_id]["error"] = str(e)
            processing_status[session_id]["done"] = True

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    return jsonify({"session_id": session_id, "status": "started"})

@app.route('/poll')
def poll():
    """Simple polling endpoint - much more reliable than SSE"""
    session_id = str(os.getpid())
    
    if session_id not in processing_status:
        return jsonify({"error": "No active session"}), 404
    
    status = processing_status[session_id]
    results = processing_results.get(session_id, [])
    
    return jsonify({
        "done": status["done"],
        "error": status["error"],
        "results": results,
        "count": len(results)
    })

@app.route('/download')
def download():
    directory = request.args.get('dir')
    if not directory:
        return ("Missing dir param", 400)
    path = os.path.join(directory, 'resultados.json')
    if not os.path.exists(path):
        return ("File not found", 404)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    print("Starting Flask server...")
    print("Server running on http://0.0.0.0:5000")
    app.run(debug=True, use_reloader=False, threaded=True, host='0.0.0.0', port=5000)