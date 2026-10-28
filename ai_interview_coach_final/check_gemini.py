"""Run:  python check_gemini.py   (from project root, venv active)
Tests the Gemini key from .env and prints exactly what works / fails."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from backend.services.ai_service import ai_service, AIServiceError

print("Key loaded:", bool(ai_service.api_key), "| length:", len(ai_service.api_key))
print("Modes:", [m for m, _ in ai_service.clients], "| Models:", ai_service.models)
try:
    out = ai_service.generate_question("Test", "Java Developer", "Fresher", ["Java", "SQL"], ["Java"],
                                       "Technical", "Medium", 1, 5, [])
    idx, model = ai_service._working
    print(f"\nSUCCESS via {ai_service.clients[idx][0]} / {model}\n")
    print(out)
except AIServiceError as e:
    print("\nFAILED:", e)
