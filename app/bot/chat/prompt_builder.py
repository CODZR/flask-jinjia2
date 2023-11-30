from textwrap import dedent
from typing import List

from ..slack.message import Message
from . import Prompt, Responder

USER_MESSAGE_CONTEXT = dedent(
    """\
    Here is the conversations history to help you understand user's message better. \
    Each message is in format of `<user name>: message`:
    ###
    {context}
    ###
    """
)


def build_common_prompt(
    *,
    responder: Responder,
    task_message: str,
    message: Message,
    history: List[Message] = [],
    system_message: str = "Your name is Vira.",
) -> Prompt:
    history_begin = 0
    history_end = len(history)

    formatted_history = [m.format_for_chat for m in history]

    def make_prompt(begin: int, end: int) -> Prompt:
        context = ""
        if begin < end:
            context = USER_MESSAGE_CONTEXT.format(context="\n---\n".join(formatted_history[begin:end]))

        user_message = task_message.format(message=message.format_for_chat, user_name=message.user.display_name)

        prompt = Prompt()
        prompt.append("system", system_message)
        prompt.append("user", context + user_message)
        return prompt

    prompt = make_prompt(history_begin, history_end)

    while history_begin < history_end and responder.exceeds_token_limit(prompt):
        history_begin = (history_begin + history_end + 1) // 2
        prompt = make_prompt(history_begin, history_end)

    return prompt
