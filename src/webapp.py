from flask import Flask, render_template, request, Response, send_file, url_for
import json
import threading
import queue
import os
from pathlib import Path
from src.main import process_dataset

app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"), static_folder=str(Path(__file__).parent / "static"))

# Shared queue for streaming progress
progress_queues = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    data = request.form
    directory = data.get('directory')
    if not directory or not os.path.isdir(directory):
        return ("Invalid directory", 400)

    # create a queue for this session
    q = queue.Queue()
    session_id = str(os.getpid())  # simple single-user ID
    progress_queues[session_id] = q

    # output file path
    output_path = os.path.join(directory, 'resultados.json')

    def worker():
        try:
            process_dataset(directory, progress_queue=q, output_path=output_path)
        except Exception as e:
            q.put({"type": "error", "error": str(e)})
        finally:
            q.put({"type": "done"})

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    return {"session_id": session_id}

@app.route('/stream')
def stream():
    # single-session implementation
    session_id = str(os.getpid())
    q = progress_queues.get(session_id)
    if q is None:
        return ("No active session", 404)

    def event_stream():
        while True:
            try:
                item = q.get()
                # Serialize to proper JSON for SSE so client can parse reliably
                try:
                    payload = json.dumps(item, ensure_ascii=False)
                except Exception:
                    # Fallback: coerce problematic values then dump
                    safe_item = {}
                    for k, v in (item.items() if isinstance(item, dict) else []):
                        if v is None:
                            safe_item[k] = None
                        else:
                            safe_item[k] = v
                    payload = json.dumps(safe_item, ensure_ascii=False)

                yield f"data: {payload}\n\n"
                if isinstance(item, dict) and item.get('type') in ('finished', 'done'):
                    break
            except Exception as e:
                print(f"Error in event stream: {e}")
                err_payload = json.dumps({"type": "error", "error": str(e)})
                yield f"data: {err_payload}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')

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
    app.run(debug=True)
