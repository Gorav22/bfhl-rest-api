from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from math import gcd
from functools import reduce
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

OFFICIAL_EMAIL = "gorav0083.be23@chitkara.edu.in"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------- Utility Functions ---------------- #

def generate_fibonacci(n: int):
    if n < 0:
        raise ValueError("Number must be non-negative")
    series = []
    a, b = 0, 1
    for _ in range(n):
        series.append(a)
        a, b = b, a + b
    return series


def get_primes(numbers: List[int]):
    if not numbers:
        raise ValueError("List cannot be empty")

    def is_prime(x):
        if x < 2:
            return False
        for i in range(2, int(x**0.5) + 1):
            if x % i == 0:
                return False
        return True

    return [num for num in numbers if is_prime(num)]


def calculate_lcm(numbers: List[int]):
    if not numbers:
        raise ValueError("List cannot be empty")

    def lcm(a, b):
        return abs(a * b) // gcd(a, b)

    return reduce(lcm, numbers)


def calculate_hcf(numbers: List[int]):
    if not numbers:
        raise ValueError("List cannot be empty")

    return reduce(gcd, numbers)


def ask_gemini(question: str):
    if not GEMINI_API_KEY:
        raise ValueError("AI API key not configured")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}

    body = {
        "contents": [
            {
                "parts": [{"text": question}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body, timeout=10)


    if response.status_code != 200:
        raise ValueError("AI service error")

    result = response.json()

    answer = result["candidates"][0]["content"]["parts"][0]["text"]

    # Return single-word response as required
    return answer.strip().split()[0]


# ---------------- Request Model ---------------- #

class BFHLRequest(BaseModel):
    fibonacci: Optional[int] = None
    prime: Optional[List[int]] = None
    lcm: Optional[List[int]] = None
    hcf: Optional[List[int]] = None
    AI: Optional[str] = None


# ---------------- Routes ---------------- #

@app.post("/bfhl")
def process_request(request: BFHLRequest):

    provided_keys = [k for k, v in request.dict().items() if v is not None]

    if len(provided_keys) != 1:
        raise HTTPException(
            status_code=400,
            detail={
                "is_success": False,
                "official_email": OFFICIAL_EMAIL,
                "error": "Exactly one key must be provided"
            }
        )

    key = provided_keys[0]
    value = getattr(request, key)

    try:
        if key == "fibonacci":
            data = generate_fibonacci(value)

        elif key == "prime":
            data = get_primes(value)

        elif key == "lcm":
            data = calculate_lcm(value)

        elif key == "hcf":
            data = calculate_hcf(value)

        elif key == "AI":
            data = ask_gemini(value)

        else:
            raise ValueError("Invalid key")

        return {
            "is_success": True,
            "official_email": OFFICIAL_EMAIL,
            "data": data
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "is_success": False,
                "official_email": OFFICIAL_EMAIL,
                "error": str(e)
            }
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "is_success": False,
                "official_email": OFFICIAL_EMAIL,
                "error": "Internal server error"
            }
        )


@app.get("/health")
def health_check():
    return {
        "is_success": True,
        "official_email": OFFICIAL_EMAIL
    }
