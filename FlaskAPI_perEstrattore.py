from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import json
from Estrazione_dati_PDF import process_file

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://convertitore-app-pdf-xml-rlgs.vercel.app"}})#"http://localhost:3000"
#app.config['DEBUG'] = True

@app.route('/', methods=['POST'])
def process_file_api():
    if 'file' not in request.files:
        return "File non fornito", 400

    file = request.files['file']
    filename = file.filename

    # Parsing dell'anagrafica
    anagrafica_data = request.form.get('anagrafica')
    if not anagrafica_data:
        return "Anagrafica non fornita", 400

    try:
        anagrafica = json.loads(anagrafica_data)
    except json.JSONDecodeError:
        return "Anagrafica non valida", 400

    # Salva temporaneamente il file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
        file_path = temp_file.name
        file.save(file_path)

    try:
        # Elabora il file con la funzione esistente
        file_data = process_file(file_path, filename, anagrafica)
        return jsonify(file_data), 200

    except Exception as e:
        return f"Errore: {str(e)}", 500

    finally:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing temp file: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render PORT come env
    os.system("gunicorn FlaskAPI_perEstrattore:app --bind 0.0.0.0:$PORT --workers 1")
