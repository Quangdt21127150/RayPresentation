import time

import ray
from ray import serve
from starlette.requests import Request

ray.init()
serve.start()


@serve.deployment(num_replicas=2)
class HelloApp:
    def __init__(self):
        self.message = "This is Ray Serve."

    async def __call__(self, request: Request):
        name = request.query_params.get("name", "World")
        return {
            "message": f"{self.message} Hello {name}!",
            "status": "success",
        }


# Deploy
hello_app = HelloApp.bind()

try:
    serve.run(hello_app, blocking=True)  # Keep ray serve running
except KeyboardInterrupt:
    serve.shutdown()
    time.sleep(1)
    ray.shutdown()
    print("Shutdowned Ray Serve")
