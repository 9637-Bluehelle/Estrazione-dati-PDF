from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import json
from Estrazione_dati_PDF import process_file
#
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

try:
  cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
  if cred_json:
    # Crea un file temporaneo o usa StringIO per caricare da stringa
    cred = credentials.Certificate(json.loads(cred_json))
  else:
    # Fallback o gestione di un errore se le credenziali non sono disponibili
    print("WARNING: Firebase credentials not found in environment.")
    # Solleva un errore o gestisci l'inizializzazione parziale se necessario.
            
  if 'cred' in locals() and not firebase_admin._apps:
    initialize_app(cred)
    db = firestore.client() # Variabile globale per Firestore
  elif not firebase_admin._apps:
    print("ERROR: Could not initialize Firebase Admin SDK. Missing credentials.")
except Exception as e:
    print(f"Error initializing Firebase: {e}")

def get_api_key_from_firebase(uid_utente):
    # Assumiamo che tu stia usando Firestore e che le chiavi siano memorizzate
    # in una collezione 'users' con il campo 'openai_api_key'.
    try:
        # Assicurati che 'db' sia stato inizializzato
        if 'db' not in globals():
             raise Exception("Firebase DB not initialized.")
             
        user_ref = db.collection('raccolta').document(uid_utente)
        user_doc = user_ref.get()

        if user_doc.exists:
            # Modifica 'openai_api_key' con il nome del campo nel tuo database
            api_key = user_doc.to_dict().get('api_key')
            if api_key:
                return api_key
            else:
                raise Exception("Chiave API OpenAI non trovata per questo utente.")
        else:
            raise Exception("Utente non trovato nel database Firebase.")

    except Exception as e:
        print(f"Errore nel recupero della chiave API per {uid_utente}: {e}")
        raise e
#
app = Flask(__name__)
CORS(app, origins=["https://convertitorepdfxml.vercel.app", "http://localhost:3000"])
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
#
    uid_utente = request.form.get('uid') # Ottiene l'UID al posto della chiave API
    if not uid_utente:
        return "UID utente non fornito", 401 # Unauthorized o Bad Request
        
    try:
        # Chiama la funzione per recuperare la chiave
        api_key = get_api_key_from_firebase(uid_utente)
    except Exception as e:
        # Se c'è un errore nel recupero (utente non trovato, chiave mancante, ecc.)
        return jsonify({"errore": f"Autenticazione fallita: {str(e)}"}), 401
#
    # Salva temporaneamente il file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
        file_path = temp_file.name
        file.save(file_path)
    """
    try:
        api_key =  request.form.get('api_key')
    except Exception as e:
        return jsonify({"errore": str(e)}), 500
    """
    try:
        # Elabora il file con la funzione esistente
        file_data = process_file(file_path, filename, anagrafica, api_key)
        return jsonify(file_data), 200

    except Exception as e:
        return jsonify({"errore": str(e)}), 500

    finally:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing temp file: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render PORT come env
    os.system("gunicorn FlaskAPI_perEstrattore:app --bind 0.0.0.0:$PORT --workers 1")



