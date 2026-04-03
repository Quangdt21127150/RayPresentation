from fastapi import FastAPI
from pydantic import BaseModel
from ray import serve
import ray
from transformers import pipeline
import time

ray.init(ignore_reinit_error=True)
serve.start()

app = FastAPI()


class TextInput(BaseModel):
    text: str


@serve.deployment(
    autoscaling_config={
        "min_replicas": 1,
        "max_replicas": 4,
        "target_num_ongoing_requests_per_replica": 5,
    },
)
@serve.ingress(app)
class SentimentAnalysis:
    def __init__(self):
        print("Đang tải mô hình Sentiment Analysis...")
        self.sentiment_model = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True,
            device=-1,  # CPU
        )

    @app.post("/sentiment")
    async def classify(self, input: TextInput):
        if not input.text:
            return {"error": "Vui lòng nhập text"}

        result = self.sentiment_model(input.text)[0]
        return {
            "input": input.text,
            "sentiment": result["label"],
            "score": result["score"] * 100,
        }


# ================== DEPLOY ==================
sentiment_app = SentimentAnalysis.bind()

try:
    serve.run(sentiment_app, blocking=True)
except KeyboardInterrupt:
    serve.shutdown()
    time.sleep(1)
    ray.shutdown()
    print("Shutdowned Ray Serve")
