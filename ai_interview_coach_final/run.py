import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure current directory is in sys.path
    cwd = os.path.dirname(os.path.abspath(__file__))
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

    print("==================================================================")
    print("  AI-POWERED INTELLIGENT INTERVIEW COACHING SYSTEM")
    print("==================================================================")
    print("  Starting FastAPI Uvicorn Server at http://127.0.0.1:8000")
    print("  Interactive Swagger Documentation: http://127.0.0.1:8000/docs")
    print("  Frontend Web Interface:           http://127.0.0.1:8000/app/index.html")
    print("==================================================================")

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
