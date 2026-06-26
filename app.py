from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from pipeline import run_pipeline
import os
import tempfile
import zipfile

app = Flask(__name__)
CORS(app)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    user_prompt = data["prompt"]

    final_schema, validation, generated_files = run_pipeline(user_prompt)

    # Create zip file
    zip_path = "/home/aarush/Documents/vscode/temp/generated_app.zip"
    app_dir = "/home/aarush/Documents/vscode/temp/generated_app"
    
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = filepath.replace(app_dir + "/", "")
                zipf.write(filepath, arcname)

    return jsonify({
        "schema": final_schema,
        "validation": validation,
        "generated_files": generated_files
    })

@app.route("/health",methods=["GET"])
def health():
    return jsonify({"status":"ok"})

@app.route("/download", methods=["GET"])
def download():
    zip_path = "/home/aarush/Documents/vscode/temp/generated_app.zip"
    return send_file(zip_path, as_attachment=True, download_name="generated_app.zip")

if __name__ == "__main__":
    app.run(debug=False, port=5000)