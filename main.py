from fastapi import FastAPI

app = FastAPI(title="AI Data Analyst API")


@app.get("/health")
def health():
    return {"status": "ok"}
