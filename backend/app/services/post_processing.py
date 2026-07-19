from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool
from dotenv import load_dotenv
import os

client = genai.Client()
model = "gemini-3.5-flash"
generation_config = {"thinking_level": "low"}

# for allowing the response to access web internet allegedly
# response = client.models.generate_content(
#     model="gemini-3.5-flash",
#     contents="What are the latest updates on the Gemini API?",
#     config=GenerateContentConfig(
#         tools=[
#             Tool(
#                 google_search=GoogleSearch()
#             )
#         ]
#     ),
# )
def find_legitimacy(Post post)