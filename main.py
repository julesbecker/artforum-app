from google.cloud import firestore
from flask import Flask, jsonify, abort, request
import os
import nltk

# the .download() call can be removed after first run
nltk.download('punkt', download_dir='./nltk')
nltk.data.path.append('./nltk')

# change "path/to/key.json" to the path to the Google Cloud key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"

app = Flask(__name__)

# Firestore db
db = firestore.Client()
artforum_ref = db.collection("reviews")
pitchfork_ref = db.collection("pitchfork") 


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route('/artforum/', defaults={'id': None})
@app.route('/artforum/<id>')
def get_art_review(id):
    if id is None:
        query = artforum_ref.order_by("selection_count").limit(1).stream()
        for doc in query:
            id = doc.id
            result = doc.to_dict()
            result['id'] = id
            break

        db.collection("reviews").document(id).update(
            {"selection_count": firestore.Increment(1)})
        return jsonify(result)
    else:
        doc = artforum_ref.document(id).get()

        if doc.exists:
            result = doc.to_dict()
            result['id'] = id
            return jsonify(result)
        else:
            abort(404, description="id not found")


@app.route('/pitchfork/', defaults={'id': None})
@app.route('/pitchfork/<id>')
def get_music_review(id):
    if id is None:
        score = request.args.get('score')
        genre = request.args.get('genre')

        query = pitchfork_ref

        if score is not None:
            query = query.where('score', '==', float(score))
        if genre is not None:
            query = query.where('genre', '==', genre)

        query = query.order_by("selection_count").limit(1).stream() 
        result = None

        for doc in query:
            id = doc.id
            result = doc.to_dict()
            result['id'] = id
            break

        # if query was empty, result will still be None
        if result is None:
            abort(404, description="incorrect query")
        else:
            pitchfork_ref.document(id).update(
                {"selection_count": firestore.Increment(1)})

            sentences = nltk.tokenize.sent_tokenize(result['text'])

            if len(sentences) > 3:
                if result['length'] > 500:
                    first_third = ' '.join(sentences[:len(sentences)//3])
                    second_third = ' '.join(sentences[len(sentences)//3:2*len(sentences)//3])
                    third_third = ' '.join(sentences[2*len(sentences)//3:])
                    result['text'] = '<p>{}</p>\n<p>{}</p>\n<p>{}</p>'.format(first_third, second_third, third_third)
                elif result['length'] > 250:
                    first_half = ' '.join(sentences[:len(sentences)//2])
                    second_half = ' '.join(sentences[len(sentences)//2:]) 
                    result['text'] = '<p>{}</p>\n<p>{}</p>'.format(first_half, second_half)

            return jsonify(result) 
    else:
        doc = pitchfork_ref.document(id).get()

        if doc.exists:
            result = doc.to_dict()
            result['id'] = id
            return jsonify(result)
        else:
            abort(404, description="id not found")


if __name__ == '__main__':
    app.run(port=8080)
