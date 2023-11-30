import json
import openai
import re

from typing import Optional, Generator

from ..chat import Prompt
from . import OPENAI_API_KEY, Prompt, Completion, Responder


openai.api_key = OPENAI_API_KEY


class OpenAIChatCompletion(Completion):
    def __init__(self, raw):
        self.__raw = raw

        choices = self.__raw.get("choices", [])
        if len(choices) == 0:
            self.__content = None
        else:
            choice = choices[0]
            if "delta" in choice:
                self.__content = choice["delta"].get("content")
            elif "message" in choice:
                self.__content = choice["message"].get("content")
            else:
                self.__content = None

    def __str__(self) -> str:
        return json.dumps(self.__raw, indent=2)

    @property
    def content(self) -> Optional[str]:
        return self.__content


class OpenAIResponder(Responder):
    def __init__(
        self,
        *,
        model: str = "gpt-3.5-turbo",
        stream: bool = False,
        temperature: float = 0.0,
    ):
        self.model = model
        self.stream = stream
        self.temperature = temperature

    def get_completion(self, prompt: Prompt) -> Generator[Completion, None, None]:
        messages = [x.__dict__ for x in prompt.entries]

        print(f"Sending prompt to OpenAI: {prompt}")

        result = openai.ChatCompletion.create(
            model=self.model,
            stream=self.stream,
            temperature=self.temperature,
            messages=messages,
        )

        if self.stream:
            counter = 0
            for c in result:
                counter += 1
                cc = OpenAIChatCompletion(c)
                if cc.content is not None:
                    yield cc

            print(f"Received {counter} streaming responses from OpenAI.")
        else:
            print(f"Received response from OpenAI: {result}")
            yield OpenAIChatCompletion(result)

    def exceeds_token_limit(self, prompt: Prompt) -> bool:
        # TODO(jiulongw): use real tokenizer
        estimated_tokens = 0
        for e in prompt.entries:
            content = e.role + ": " + e.content
            words = re.findall(r"\b\w+\b", content)
            estimated_tokens += len(words) * 4 / 3

        return estimated_tokens > 2048
