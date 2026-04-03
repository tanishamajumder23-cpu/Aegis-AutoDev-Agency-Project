import os
from crewai import LLM

# Extremely stable configuration for Groq
my_llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1, # Lower temperature = more stable
    max_tokens=4000
)