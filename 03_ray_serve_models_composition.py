import time

import ray
from ray import serve
from pydantic import BaseModel
from transformers import pipeline
from fastapi import FastAPI

ray.init(ignore_reinit_error=True)
serve.start(detached=True, http_options={"host": "localhost", "port": 3000})

app = FastAPI()


class TextRequest(BaseModel):
    text: str


# --- Emotion Model ---
@serve.deployment
class EmotionModel:
    def __init__(self):
        self.pipe = pipeline(
            "text-classification", model="j-hartmann/emotion-english-distilroberta-base"
        )

    async def __call__(self, request: TextRequest):
        return self.pipe(request.text)[0]


# --- Rating Model ---
@serve.deployment
class RatingModel:
    def __init__(self):
        self.pipe = pipeline(
            "text-classification", model="kmack/YELP-Review_Classifier"
        )

    async def __call__(self, text: str, emotion: dict):
        new_text = f"{text} This review feels {emotion['label']}."
        res = self.pipe(new_text)[0]
        label_num = int(res["label"].split("_")[1])
        stars = label_num + 1
        return {"rating": stars, "score": res["score"]}


# --- Sentiment Model ---
@serve.deployment
class SentimentModel:
    def __init__(self):
        self.pipe = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )

    async def __call__(self, text: str, rating: dict, emotion: dict):
        combined_text = f"{text} This review has {rating['rating']} stars and feels {emotion['label']}."
        return self.pipe(combined_text)[0]


# --- Pipeline ---
@serve.deployment
@serve.ingress(app)
class PredictApp:
    def __init__(self, emotion_handle, rating_handle, sentiment_handle):
        self.emotion_handle = emotion_handle
        self.rating_handle = rating_handle
        self.sentiment_handle = sentiment_handle

    @app.post("/predict")
    async def predict(self, request: TextRequest):
        emotion_res = self.emotion_handle.remote(request)
        emotion = await emotion_res

        rating_res = self.rating_handle.remote(request.text, emotion)
        rating = await rating_res

        sentiment_res = self.sentiment_handle.remote(request.text, rating, emotion)
        sentiment = await sentiment_res

        return {
            "text": request.text,
            "emotion": emotion["label"],
            "rating": rating["rating"],
            "sentiment": sentiment["label"],
        }


# --- Deployments ---
emotion_handle = EmotionModel.bind()
rating_handle = RatingModel.bind()
sentiment_handle = SentimentModel.bind()
predict_app = PredictApp.bind(emotion_handle, rating_handle, sentiment_handle)

try:
    serve.run(predict_app, blocking=True)
except KeyboardInterrupt:
    serve.shutdown()
    time.sleep(1)
    ray.shutdown()
    print("Shutdowned Ray Serve")
