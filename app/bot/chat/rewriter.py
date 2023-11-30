import json

from dataclasses import dataclass
from textwrap import dedent
from typing import List
from ..slack.message import Message
from .openai import OpenAIResponder
from .utils import get_final_completion
from .prompt_builder import build_common_prompt


def rewrite_git_message(message: Message, history: List[Message] = []) -> str:
    system_message = dedent(
        """\
        Your name is Vira. You are a software developer who write professional git commit messages.
        """
    )

    task_message = dedent(
        """\
        Here is the message from {user_name}:
        ###
        {message}
        ###

        Your task is to extract the description about a git commit from the message, \
        and rewrite it into a professional git commit message. You should use conventional commit format \
        such as `feat(canvas): implement new toolbar` or `fix(web): keep promoted status for losing follow`.
        Here is a list of scopes you can use, you can also make new scope from the context:
        - canvas: the canvas engine project.
        - web: the canvas web app.
        - proto: the shared protobuf definitions.
        - be: the backend system
        - libs: shared frontend libs
        - ipad: the canvas ipad app
        - cast: the screen cast project

        Reply the commit message only (title and a optional description). No other text is allowed.
        """
    )

    responder = OpenAIResponder()
    prompt = build_common_prompt(
        responder=responder, task_message=task_message, message=message, history=history, system_message=system_message
    )

    completion = responder.get_completion(prompt)
    answer = get_final_completion(completion)

    return answer


def rewrite_email(message: Message, history: List[Message] = []) -> str:
    task_message = dedent(
        """\
        Here is the message from {user_name}:
        ###
        {message}
        ###

        Your task is to extract the draft email from the message, and rewrite it into a professional email. \
        Unless {user_name} has specified the tone, you should use a tone of a customer support professional.
        """
    )

    responder = OpenAIResponder(temperature=0.3)
    prompt = build_common_prompt(responder=responder, task_message=task_message, message=message, history=history)

    completion = responder.get_completion(prompt)
    answer = get_final_completion(completion)

    return answer


def rewrite_ads(message: Message, history: List[Message] = []) -> str:
    task_message = dedent(
        """\
        Here is the message from {user_name}:
        ###
        {message}
        ###

        Your task is to extract the draft ads copy from the message, and rewrite it in a way that is more catchy, \
        appealing, and effective. It should drive more clicks and conversions. You should reply with 3 versions.
        """
    )

    responder = OpenAIResponder(temperature=0.5)
    prompt = build_common_prompt(responder=responder, task_message=task_message, message=message, history=history)

    completion = responder.get_completion(prompt)
    answer = get_final_completion(completion)

    return answer


def rewrite_ui(message: Message, history: List[Message] = []) -> str:
    task_message = dedent(
        """\
        Here is the message from {user_name}:
        ###
        {message}
        ###

        Here's the context of the company Vibe Inc:
        ###
        Vibe is an innovative workspace solutions company founded in 2018. They focus on improving \
        collaboration for hybrid teams with products like smart whiteboards and AI cameras. \
        With over 30,000 customers worldwide, Vibe values great products, transparency, empathy, \
        long-term thinking, and freedom with responsibility.
        Vibe offers following apps:
        - Vibe Canvas: a digital whiteboard for real-time remote collaboration.
        - Vibe One: a companion app for Vibe's hardware.
        - Vibe Room: an all-in-one meeting room solution using Vibe's ecosystem.
        - Vibe OS: a custom operating system for Vibe's hardware based on Chromium OS.
        ###

        Your task is to extract the piece of text for the user interface, and rewrite it in a way that is \
        user friendly, easy to understand, and concise. You should reply with 3 versions. Here's the rules:
        ###
        Vibe's software products needs to be capitalized. For example, "Vibe Canvas" instead of "Vibe canvas".
        "Sign up" should be used instead of "Register".
        "Sign in" should be used instead of "Log in".
        "Sign off" should be used instead of "Log out".
        The code used to share canvas is called "分享码" in Chinese.
        "Canvas" is called "白板" in Chinese
        ###
        """
    )

    responder = OpenAIResponder(temperature=0.1)
    prompt = build_common_prompt(responder=responder, task_message=task_message, message=message, history=history)

    completion = responder.get_completion(prompt)
    answer = get_final_completion(completion)

    return answer


@dataclass
class ProofreadResult:
    original_text: str
    corrected_text: str


def proofread(message: Message, history: List[Message] = []) -> ProofreadResult:
    task_message = dedent(
        """\
        Here is the message from {user_name}:
        ###
        {message}
        ###

        Your task is to proofread the piece of text that {user_name} requested. \
        You should correct grammar and improve readability.

        Reply a JSON object with the following keys: "original_text", "corrected_text". \
        No other text is allowed.
        """
    )

    responder = OpenAIResponder()
    prompt = build_common_prompt(responder=responder, task_message=task_message, message=message, history=history)

    completion = responder.get_completion(prompt)
    answer = get_final_completion(completion)
    o = json.loads(answer)
    return ProofreadResult(**o)
