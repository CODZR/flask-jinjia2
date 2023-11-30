import argparse
import re

from typing import List, Dict, Optional, Sequence, cast
from slack_sdk.models.blocks import Block, SectionBlock
from .user_profile import UserProfile, UserProfileProvider, user_profile_provider
from . import slack_client

command_parser = argparse.ArgumentParser(add_help=False, usage="@Vira [optional arguments] message")
command_parser.add_argument("--dev", action="store_true", help="use dev environment.")
command_parser.add_argument("--help", action="store_true", help="show help.")
command_parser.add_argument("--raw", action="store_true", help="send raw text to OpenAI.")


class Message:
    @staticmethod
    def __normalize_text(*, text: Optional[str], blocks: Optional[Sequence[Dict]]) -> str:
        if blocks is None or len(blocks) == 0:
            return text or ""

        if blocks[0].get("type") == "rich_text":
            return text or ""

        parsed_blocks = Block.parse_all(blocks=blocks)
        segments = []
        for block in parsed_blocks:
            if block.type == "section":
                section_block = cast(SectionBlock, block)
                if section_block.text and (
                    section_block.text.type == "mrkdwn" or section_block.text.type == "plain_text"
                ):
                    segments.append(section_block.text.text.strip())

        return "\n".join(segments)

    def __init__(
        self,
        *,
        user: UserProfile,
        ts: str,
        text: Optional[str] = None,
        blocks: Optional[Sequence[Dict]] = None,
        thread_ts: Optional[str] = None,
        profile_provider: Optional[UserProfileProvider] = None,
    ):
        self.user = user
        self.user_id = user.user_id
        self.text = Message.__normalize_text(text=text, blocks=blocks)
        self.ts = ts
        self.thread_ts = thread_ts
        self.args_parse_error = None
        self.__mentioned_user_ids = None
        self.__text_for_human = None
        self.__profile_provider = profile_provider

        try:
            (parsed_args, extra) = command_parser.parse_known_args(self.text.split(" "))
            self.args = parsed_args
            self.__text_without_args = " ".join(extra)
        except SystemExit as e:
            self.args = command_parser.parse_args([])
            self.__text_without_args = self.text
            self.args_parse_error = e

    @property
    def text_for_human(self) -> str:
        if self.__text_for_human is None:

            def replace(match):
                user_id = match.group(1)
                if self.__profile_provider is None:
                    return "@" + user_id
                else:
                    profile = self.__profile_provider.get(user_id)
                    return "@" + profile.display_name

            self.__text_for_human = re.sub(r"<@([A-Z0-9]+)>", replace, self.__text_without_args)

        return self.__text_for_human

    @property
    def mentioned_user_ids(self) -> List[str]:
        if self.__mentioned_user_ids is None:
            self.__mentioned_user_ids = re.findall(r"<@([A-Z0-9]+)>", self.text)

        return self.__mentioned_user_ids

    @property
    def format_for_chat(self) -> str:
        escaped = self.text_for_human.replace("\n---\n", "\n===\n")
        return f"<{self.user.display_name}>: {escaped}"


def get_thread_head(channel_id, thread_ts) -> Optional[Message]:
    resp = slack_client.conversations_history(channel=channel_id, oldest=thread_ts, inclusive=True, limit=1)
    messages = resp.get("messages")
    if not messages or len(messages) == 0:
        return None

    message = messages[0]
    if message.get("ts") != thread_ts:
        return None

    return Message(
        user=user_profile_provider.get(message["user"]),
        ts=message["ts"],
        text=message.get("text"),
        blocks=message.get("blocks"),
        thread_ts=message.get("thread_ts"),
    )


def get_thread_messages(channel_id: str, thread_ts: str, *, latest_ts: Optional[str] = None) -> List[Message]:
    history = []
    for page in slack_client.conversations_replies(channel=channel_id, ts=thread_ts, latest=latest_ts):
        for message in page.get("messages", []):
            if "subtype" in message:
                continue

            m = Message(
                user=user_profile_provider.get(message["user"]),
                ts=message["ts"],
                text=message.get("text"),
                blocks=message.get("blocks"),
                thread_ts=message.get("thread_ts"),
            )

            history.append(m)

    return history
