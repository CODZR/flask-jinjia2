import abc
import json

from dataclasses import dataclass
import os
from typing import Optional, Generator

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class Prompt:
    @dataclass
    class Entry:
        role: str
        content: str

    def __init__(self):
        self.entries = []

    def __str__(self) -> str:
        return json.dumps([x.__dict__ for x in self.entries], indent=2)

    def append(self, role: str, content: str):
        self.entries.append(Prompt.Entry(role, content))


class Completion:
    @abc.abstractproperty
    def content(self) -> Optional[str]:
        return None


class Responder:
    @abc.abstractmethod
    def get_completion(self, prompt: Prompt) -> Generator[Completion, None, None]:
        yield from ()

    @abc.abstractmethod
    def exceeds_token_limit(self, prompt: Prompt) -> bool:
        return False
