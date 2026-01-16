#!/usr/bin/env python3
"""
Test script to find which Gemini models are available with your API key.
Run this to determine which model name to use in classification_graph.py
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY or GEMINI_API_KEY not set!")
    exit(1)

# List of models to test
models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-pro",
    "gemini-1.0-pro",
]

print("Testing Gemini models...")
print("=" * 60)

working_models = []

for model_name in models_to_test:
    try:
        print(f"Testing: {model_name}...", end=" ")
        llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
        # Try a simple test call
        response = llm.invoke("Say 'test'")
        print("✓ WORKS!")
        working_models.append(model_name)
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "NOT_FOUND" in error_msg:
            print("✗ 404 Not Found")
        else:
            print(f"✗ Error: {error_msg[:50]}...")

print("\n" + "=" * 60)
if working_models:
    print(f"\n✓ Working models: {', '.join(working_models)}")
    print(f"\nRecommended: Use '{working_models[0]}' in classification_graph.py")
else:
    print("\n✗ No working models found. Check your API key and permissions.")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
