import time

import ray
from ray import serve
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime

ray.init(ignore_reinit_error=True)
serve.start()


@serve.deployment
class MyApp:
    def __init__(self):
        self.hello_msg = "This is Ray Serve."
        self.goodbye_msg = "Last words from Ray Serve:"

    async def __call__(self, request: Request):
        path = request.url.path.rstrip("/")

        if path == "/hello":
            if request.method == "GET":
                name = request.query_params.get("name", "World")
                return {"message": f"{self.hello_msg} Hello {name}"}

            elif request.method == "POST":
                data = await request.json()
                meet_at = datetime.now().isoformat()
                return {"info": data, "meet_at": meet_at}

        elif path == "/goodbye":
            if request.method == "GET":
                name = request.query_params.get("name", "Friend")
                return {"message": f"{self.goodbye_msg} Goodbye {name}"}

            elif request.method == "POST":
                data = await request.json()
                leave_at = datetime.now().isoformat()
                return {"info": data, "leave_at": leave_at}

        return JSONResponse(
            status_code=404,
            content={"error": f"Route {path} not found. Supported: /hello, /goodbye"},
        )


# Deploy app
my_app = MyApp.bind()

try:
    serve.run(my_app, blocking=True)
except KeyboardInterrupt:
    serve.shutdown()
    time.sleep(1)
    ray.shutdown()
    print("Shutdowned Ray Serve")
