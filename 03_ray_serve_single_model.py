from fastapi import FastAPI
from pydantic import BaseModel
from ray import serve
import ray
from transformers import pipeline
import time

# ================== KHỞI TẠO ==================
ray.init(ignore_reinit_error=True)
serve.start()

app = FastAPI()


class TextInput(BaseModel):
    text: str


# ================== DEPLOYMENT ==================
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
        self.classifier = pipeline(
            "text-classification",
            model="nateraw/bert-base-uncased-emotion",
            return_all_scores=True,
            device=-1,  # CPU
        )
        self.start_time = time.time()

    @app.post("/sentiment")
    async def classify(self, input: TextInput):
        if not input.text:
            return {"error": "Vui lòng nhập text"}

        result = self.classifier(input.text)[0]
        return {
            "input": input.text,
            "sentiment": result["label"],
            "score": result["score"],
            "uptime_seconds": round(time.time() - self.start_time, 2),
        }


# ================== DEPLOY ==================
sentiment_app = SentimentAnalysis.bind()
serve.run(sentiment_app, blocking=True)
