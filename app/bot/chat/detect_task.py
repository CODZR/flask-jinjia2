import json

from textwrap import dedent
from typing import List, Optional
from ..slack.message import Message
from .openai import OpenAIResponder
from .utils import get_final_completion
from .prompt_builder import build_common_prompt


def detect_task(message: Message, history: List[Message] = []) -> Optional[str]:
    task_message = dedent(
        """\
        Here is the message from {user_name} that your job is based on:
        ###
        {message}
        ###

        Your job is to detect if {user_name} is asking you to do one of the tasks below. Here's the rules:
        ###
        1. If the message relates to the copy of an ads campaign, \
        and {user_name} is asking you to rewrite or refine the copy: set "task" to "ads";
        2. If the message relates to a text for UI (user interface), \
        and {user_name} is asking you to rewrite or refine the UI text: set "task" to "ui";
        3. If the message relates to a piece of text, \
        and {user_name} is asking you to proofread, correct grammar, or improve readability of the text: \
        set "task" to "proofread";
        ###
        If none of the above rules apply: set "task" to "no_task". If multiple rules apply, \
        choose the one you are most confident with.
        Reply with a JSON object, with keys defined in the above rules. No text is allowed outside the JSON object.
        """
    )

    responder = OpenAIResponder()
    prompt = build_common_prompt(responder=responder, task_message=task_message, message=message, history=history)

    completion = responder.get_completion(prompt)
    answer = get_final_completion(completion)
    task = json.loads(answer).get("task")
    if task == "no_task":
        return None

    return task
