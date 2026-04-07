import os
from crewai import LLM

# Stable LLM configuration for Groq — used by all agents
my_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1,   
    max_tokens=800    # THE FIX: Slashed from 4000 to keep you under the 6000 limit
)