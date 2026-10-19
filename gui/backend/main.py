import uvicorn
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    print("🚀 Servidor en http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, log_level="error", reload=False)
