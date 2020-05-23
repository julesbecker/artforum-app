from google.cloud import firestore

# Project ID is determined by the GCLOUD_PROJECT environment variable
from flask import Flask, jsonify, abort
app = Flask(__name__)

@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404

@app.route('/', defaults={'id': None})
@app.route('/<id>')
def get_review(id):
    db = firestore.Client()
    reviews_ref = db.collection("reviews")

    if id == None:
        query = reviews_ref.order_by("selection_count").limit(1).stream()
        for doc in query:
            id = doc.id
            result = doc.to_dict()
            result['id'] = id
            break

        db.collection("reviews").document(id).update({"selection_count": firestore.Increment(1)})
        return jsonify(result)
        
    else:
        doc = db.collection("reviews").document(id).get()

        if doc.exists:
            result = doc.to_dict()
            result['id'] = id
            return jsonify(result)
        else:
            abort(404, description="id not found")

if __name__ == '__main__':
    app.run(port=8080)
