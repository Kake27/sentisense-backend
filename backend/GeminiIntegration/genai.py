from google import genai
from dotenv import load_dotenv
import os
import json

load_dotenv()


class Genai:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def get_solutions(self, prompt):
        try :
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
            )
            

            raw_text = response.candidates[0].content.parts[0].text  
            cleaned_text = raw_text.replace("json", "").replace("```", "").strip()

            try:
                parsed_response = json.loads(cleaned_text)
                # print(parsed_response) 
                return parsed_response 

            except json.JSONDecodeError as e:
                print("Error decoding JSON:",e)

        except Exception as e:
            print("An error occurred: "+str(e))
            return None

