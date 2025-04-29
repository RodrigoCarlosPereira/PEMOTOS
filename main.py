from fastapi import FastAPI

app = FastAPI()

@app.get("/teste", status_code=200)
def test():
    return {"message": "Hello World"}