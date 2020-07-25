from fastapi import FastAPI
import random

app = FastAPI()


@app.get("/91ba2c3f3dd5241218d2f24a3b1bfe4ce84923cb")
async def root():
    msg = random.randint(0,999999999999999999)
    return {"Random": msg}