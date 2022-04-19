import os
import gpt_2_simple as gpt2
from google.cloud import firestore

# replace './key.json' with the path to your Google Cloud key
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"

sess = gpt2.start_tf_sess()
gpt2.load_gpt2(sess, checkpoint_dir="/storage/checkpoint", run_name="pitchfork_run1")

db = firestore.Client()
reviews_ref = db.collection("reviews")

scores = [x / 2 for x in range(21)]
genres = [
    "Rock",
    "Electronic",
    "Rap",
    "Pop/R&B",
    "Experimental",
    "Folk/Country",
    "Metal",
    "Jazz",
]
pairs = [(i, j) for i in scores for j in genres]

def process(review):
    # remove everything before the last <|startoftext|>
    review = review.split("<|startoftext|>")[-1]

    # and also before the last newline (this will get rid of the prompt)
    review = review.split("\n")[-1]

    # throw out reviews shorter than a sentence
    if review.count(".") == 0:
        return None
    else:
        # trim after the last period
        review = review.rsplit(".", 1)[0] + "."

        return review


for score, genre in pairs:
    review_prefix = "<|startoftext|>" + str(score) + "\n" + genre + "\n"
    text = gpt2.generate(
        sess,
        run_name="pitchfork_run1",
        checkpoint_dir="/storage/checkpoint",
        prefix=review_prefix,
        truncate="<|endoftext|>",
        return_as_list=True,
        include_prefix=False,
        nsamples=50,
        batch_size=10,
        length=500,
        temperature=0.7,
        top_p=0.95,
    )

    # the "if process(r)" removes None values from the list
    processed = [process(r) for r in text if process(r)]

    batch = db.batch()

    for review in processed:
        data = {
            "text": review,
            "score": score,
            "genre": genre,
            "length": len(review.split()),
            "added": firestore.SERVER_TIMESTAMP,
            "selection_count": 0,
        }

        # create a ref with auto-generated ID
        new_review_ref = reviews_ref.document()

        # add it to the batch
        batch.set(new_review_ref, data)

    batch.commit()
