import ray
from ray import serve
from pydantic import BaseModel
from transformers import pipeline
from fastapi import FastAPI

ray.init(ignore_reinit_error=True)
serve.start(detached=True, http_options={"host": "127.0.0.1", "port": 8000})

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
class FinalSentimentModel:
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
class Pipeline:
    def __init__(self, emotion_handle, rating_handle, final_handle):
        self.emotion_handle = emotion_handle
        self.rating_handle = rating_handle
        self.final_handle = final_handle

    @app.post("/predict")
    async def predict(self, request: TextRequest):
        emotion_resp = self.emotion_handle.remote(request)
        emotion = await emotion_resp

        rating_resp = self.rating_handle.remote(request.text, emotion)
        rating = await rating_resp

        sentiment_resp = self.final_handle.remote(request.text, rating, emotion)
        sentiment = await sentiment_resp

        return {
            "text": request.text,
            "emotion": emotion["label"],
            "rating": rating["rating"],
            "sentiment": sentiment["label"],
        }


# --- Bind deployments ---
emotion_handle = EmotionModel.bind()
rating_handle = RatingModel.bind()
final_handle = FinalSentimentModel.bind()
pipeline = Pipeline.bind(emotion_handle, rating_handle, final_handle)

serve.run(pipeline, blocking=True)
