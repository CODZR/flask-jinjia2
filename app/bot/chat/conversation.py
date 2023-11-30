import re

from textwrap import dedent
from typing import List, Optional
from ..slack.message import Message
from .openai import OpenAIResponder
from .utils import get_final_completion
from .prompt_builder import build_common_prompt
from . import Prompt


def reply_conversation(message: Message, history: List[Message] = []) -> Optional[str]:
    system_message = dedent(
        """\
        Your name is Vira. You're a helpful Slack bot that acts as a personal assistant to your users. \
        Your preferred languange is English.
        Vibe is an innovative workspace solutions company founded in 2018. They focus on improving \
        collaboration for hybrid teams with products like smart whiteboards and AI cameras. \
        With over 30,000 customers worldwide, Vibe values great products, transparency, empathy, \
        long-term thinking, and freedom with responsibility.
        """
    )

    task_message = dedent(
        """\
        Here is the message from {user_name}:
        ###
        {message}
        ###

        1. Who is {user_name} talking to in the last message? \
        Set "talk_to" to the user being talked to if you can tell, otherwise, set "talk_to" to "Vira";
        2. Which language is {user_name} using? \
        Set "lang" to the language if you can tell, otherwise, set "lang" to "English";
        3. If "talk_to" is "Vira": reply to {user_name}'s last message as a personal assistant, \
        using the same language as {user_name}, and set "content" to your reply message; \
        otherwise, set "content" to "NO COMMENT";

        Your reply must be exactly in the following format:
        ###
        Step $(step): {user_name} is talking to $(talk_to).
        Step $(step): {user_name} is using $(lang).
        Final Answer: $(content)
        ###
        """
    )

    responder = OpenAIResponder()
    prompt = build_common_prompt(
        responder=responder,
        task_message=task_message,
        message=message,
        history=history,
        system_message=system_message,
    )

    completion = responder.get_completion(prompt)
    answer = get_final_completion(completion)

    m = re.search(r"^Final Answer: (.*)$", answer, re.MULTILINE | re.DOTALL)
    if not m or m.group(1) == "NO COMMENT":
        return None

    return m.group(1)


def reply_raw(message: Message) -> str:
    prompt = Prompt()
    prompt.append("user", message.text_for_human)

    responder = OpenAIResponder()
    completion = responder.get_completion(prompt)
    return get_final_completion(completion)
