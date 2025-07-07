from openai import OpenAI
import json

from .prompts import SYS_PROMPT, SYS_PROMPT_DATA, generate_prompt

from dotenv import load_dotenv
import os

load_dotenv(".env")

TOGETHER_API = os.getenv("TOGETHER_API_KEY")
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
MODEL_STRONG = "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"


class CSS_Selector:

    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=TOGETHER_API, base_url="https://api.together.xyz/v1"
        )

    def get_actions(self, html_content: str, task: str):
        prompt = generate_prompt(html_content, task)
        print(prompt)

        print("len : ", len(SYS_PROMPT) + len(prompt))

        messages = [
            {"role": "system", "content": SYS_PROMPT},
            {"role": "user", "content": prompt},
        ]

        response = (
            self.client.chat.completions.create(model=MODEL_NAME, messages=messages)
            .choices[0]
            .message.content
        )

        return response

    def extract_data(self, html_content, task):
        prompt = f"Taks:{task}\n\nHTML:\n\n" + html_content
        print(prompt)
        messages = [
            {"role": "system", "content": SYS_PROMPT_DATA},
            {"role": "user", "content": prompt},
        ]

        response = (
            self.client.chat.completions.create(model=MODEL_STRONG, messages=messages)
            .choices[0]
            .message.content
        )

        return response
