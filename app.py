#python SDK used to acces gemini Models
!pip install -q -U google-generativeai
     

import google.generativeai as genai

#loading api_key sercurely from .env
import os
from dotenv import load_dotenv