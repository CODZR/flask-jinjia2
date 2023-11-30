from collections import deque
from datetime import timedelta, datetime
from typing import Generator

from . import Completion


def accumulate_completion(
    completion: Generator[Completion, None, None],
    *,
    throttle: timedelta = timedelta(seconds=1),
) -> Generator[str, None, None]:
    content = ""
    last_yield_time = None
    has_new_content = False
    for c in completion:
        if c.content:
            content += c.content
            has_new_content = True

        now = datetime.now()
        if has_new_content and (
            last_yield_time is None or last_yield_time + throttle > now
        ):
            last_yield_time = now
            has_new_content = False
            yield content

    if has_new_content:
        yield content

    print(f"Accumulated completion: {content}")


def get_final_completion(completion: Generator[Completion, None, None]) -> str:
    (content,) = deque(accumulate_completion(completion), 1)
    return content
