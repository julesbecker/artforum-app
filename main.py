from google.cloud import firestore
from flask import Flask, jsonify, abort, request
import os
import nltk
from flask_cors import CORS

app = Flask(__name__)

# Disable strict slashes
app.url_map.strict_slashes = False

# Configure CORS properly
CORS(app)  # Enable CORS

# the .download() call is only necessary on the first run
nltk.download('punkt', download_dir='./nltk')
nltk.download("punkt_tab", download_dir="./nltk")
nltk.data.path.append("./nltk")

# Handle Google Cloud credentials from environment variable
if 'KEY_JSON' in os.environ:
    # Write the key data to a temporary file
    key_json = os.environ.get('KEY_JSON')
    temp_key_path = '/tmp/google_creds.json'
    with open(temp_key_path, 'w') as f:
        f.write(key_json)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_key_path
elif os.path.exists('./key.json'):
    # Fallback for local development
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"
else:
    raise RuntimeError("No Google Cloud credentials found. Set KEY_JSON environment variable or provide key.json file.")

app = Flask(__name__)

# Firestore db
db = firestore.Client()
artforum_ref = db.collection("reviews")
pitchfork_ref = db.collection("pitchfork")


def format_text(text, length):
    sentences = nltk.tokenize.sent_tokenize(text)
    if len(sentences) > 3 and length > 250:
        if length > 500:
            # split into 3 paragraphs
            first_third = " ".join(sentences[: len(sentences) // 3])
            second_third = " ".join(
                sentences[len(sentences) // 3 : 2 * len(sentences) // 3]
            )
            third_third = " ".join(sentences[2 * len(sentences) // 3 :])
            return "<p>{}</p><p>{}</p><p>{}</p>".format(
                first_third, second_third, third_third
            )
        else:
            # split into 2 paragraphs
            first_half = " ".join(sentences[: len(sentences) // 2])
            second_half = " ".join(sentences[len(sentences) // 2 :])
            return "<p>{}</p><p>{}</p>".format(first_half, second_half)
    else:
        return "<p>{}</p>".format(text)


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route("/artforum/", defaults={"id": None})
@app.route("/artforum/<id>")
def get_art_review(id):
    if id is None:
        query = artforum_ref.order_by("selection_count").limit(1).stream()
        for doc in query:
            id = doc.id
            result = doc.to_dict()
            result["id"] = id
            result["text"] = "<p>{}</p>".format(result["text"])
            break

        db.collection("reviews").document(id).update(
            {"selection_count": firestore.Increment(1)}
        )
        return jsonify(result)
    else:
        doc = artforum_ref.document(id).get()

        if doc.exists:
            result = doc.to_dict()
            result["id"] = id
            result["text"] = "<p>{}</p>".format(result["text"])
            return jsonify(result)
        else:
            abort(404, description="id not found")


@app.route("/pitchfork/", defaults={"id": None})
@app.route("/pitchfork/<id>")
def get_music_review(id):
    if id is None:
        score = request.args.get("score")
        genre = request.args.get("genre")

        query = pitchfork_ref

        if score is not None:
            query = query.where("score", "==", float(score))
        if genre is not None:
            query = query.where("genre", "==", genre)

        query = query.order_by("selection_count").limit(1).stream()
        result = None

        for doc in query:
            id = doc.id
            result = doc.to_dict()
            result["id"] = id
            break

        # if query was empty, result will still be None
        if result is None:
            abort(404, description="incorrect query")
        else:
            pitchfork_ref.document(id).update(
                {"selection_count": firestore.Increment(1)}
            )
            result["text"] = format_text(result["text"], result["length"])
            return jsonify(result)
    else:
        doc = pitchfork_ref.document(id).get()

        if doc.exists:
            result = doc.to_dict()
            result["id"] = id
            result["text"] = format_text(result["text"], result["length"])
            return jsonify(result)
        else:
            abort(404, description="id not found")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
