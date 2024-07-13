import google.generativeai as genai
import os

API_KEY = "AIzaSyCuD8qqwj1YfENc56dagWYdgtN0RPwc_vw"  # Google AI Studio API key for Gemini API

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content("Write a email to my dad asking for a pet dog")
print(response.text)