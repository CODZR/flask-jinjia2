import json
import re
from flask import Request, Response
from openai import BadRequestError
import requests

from slack_sdk.signature import SignatureVerifier
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, Optional, Callable, List

from app.response import empty_response

from ..chat.conversation import reply_conversation, reply_raw
from ..chat.detect_task import detect_task
from ..chat.rewriter import rewrite_ads, rewrite_ui, proofread
from . import SLACK_SIGN_SECRET, slack_client
from .user_profile import user_profile_provider
from .message import Message, get_thread_head, get_thread_messages

AUTH_TEST = slack_client.auth_test()
SLACK_BOT_USER_ID = AUTH_TEST["user_id"]
SLACK_TEAM_ID = AUTH_TEST["team_id"]
ABOUT_PAGE_LINK = f"slack://app?team={SLACK_TEAM_ID}&id=A0512MD4JJH&tab=about"


def handle_webhook_event(request: Request, *, is_dev: bool):
    _validate_request(request)

    body = request.json_body
    event_type = body.get("type")
    if event_type == "url_verification":
        return _handle_url_verification(body)

    if event_type == "event_callback":
        event = body.get("event")
        if not event:
            raise BadRequestError("")

        def dev_forwarder(m: Message) -> bool:
            if not m.args.dev:
                return False

            signer = SignatureVerifier(SLACK_SIGN_SECRET)
            timestamp = str(int(signer.clock.now()))
            sig = signer.generate_signature(timestamp=timestamp, body=request.raw_body)
            headers = {
                "Content-Type": "application/json",
                "X-Slack-Request-Timestamp": timestamp,
                "X-Slack-Signature": sig,
            }

            r = requests.post(
                "https://vira-dev.vibe.dev/slack/event",
                data=request.raw_body,
                headers=headers,
            )
            print(
                f"Forwarded request to dev endpoint. Status code: {r.status_code}. Body: {request.raw_body}"
            )

            return True

        return _handle_event_callback(
            event, dev_forwarder=None if is_dev else dev_forwarder
        )

    return empty_response()


def handle_queued_event(event: Dict[str, Any], *, is_dev: bool = False) -> None:
    channel_id = event.get("channel")
    user_id = event.get("user")
    ts = event.get("ts")

    if not channel_id or not ts or not user_id:
        return

    thread_ts = event.get("thread_ts")

    history = []
    if thread_ts:
        history = get_thread_messages(channel_id, thread_ts, latest_ts=ts)

    user_message = Message(
        user=user_profile_provider.get(user_id),
        ts=ts,
        text=event.get("text"),
        blocks=event.get("blocks"),
        thread_ts=thread_ts,
        profile_provider=user_profile_provider,
    )

    reply_ts = thread_ts if thread_ts else ts
    _make_reply(
        channel_id=channel_id,
        reply_ts=reply_ts,
        user_message=user_message,
        history=history,
        is_dev=is_dev,
    )


def _validate_request(request) -> None:
    verifier = SignatureVerifier(SLACK_SIGN_SECRET)
    is_valid = verifier.is_valid_request(request.raw_body, request.headers)
    if not is_valid:
        raise BadRequestError("Invalid request signature")


def _handle_url_verification(body: Dict[str, Any]):
    return make_response({"challenge": body.get("challenge")})


def _handle_event_callback(
    event: Dict[str, Any], *, dev_forwarder: Optional[Callable[[Message], bool]] = None
):
    if not _should_process(event):
        return empty_response()

    m = Message(
        user=user_profile_provider.get(event["user"]),
        ts=event["ts"],
        text=event.get("text"),
        blocks=event.get("blocks"),
        thread_ts=event.get("thread_ts"),
    )

    if dev_forwarder:
        forwarded = dev_forwarder(m)
        if forwarded:
            return empty_response()

    if m.args.help:
        _reply_to_event(
            event,
            f"Hi! I'm Vira :wave:. I'm your personal assistant. <{ABOUT_PAGE_LINK}|See what I can do>",
        )
        return empty_response()

    _queue_event(event)
    return empty_response()


def _should_process(event: Dict[str, Any]) -> bool:
    # never process messages from app itself
    user = event.get("user")
    if user == SLACK_BOT_USER_ID:
        return False

    # always process if app is mentioned
    if event.get("type") == "app_mention":
        return True

    if event.get("type") != "message" or "subtype" in event:
        return False

    message_text = event.get("text", "").strip()
    channel_type = event.get("channel_type")

    # always process if the message is in DM (with bot)
    if channel_type == "im":
        return True

    # if the bot is mentioned in the message, skip because it will be handled by app_mention event.
    if f"<@{SLACK_BOT_USER_ID}>" in message_text:
        return False

    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts")
    if not thread_ts:
        return False

    thread_head = get_thread_head(channel_id, thread_ts)
    if not thread_head or SLACK_BOT_USER_ID not in thread_head.mentioned_user_ids:
        return False

    print(f"Received message in a watched thread (thread_ts={thread_ts}): {event}")
    # If a thread head has mentioned the bot, the thread is treated as "watched thread".
    # Any reply in the watched thread will be processed, except:
    # - the message starts with mention to someone other than the bot.
    mention_at_begining = re.match(r"^<@([A-Z0-9]+)>", message_text)
    if mention_at_begining and mention_at_begining.group(1) != SLACK_BOT_USER_ID:
        print(
            "Skip message in the watched thread. It starts with mention to someone other than the bot"
        )
        return False

    return True


def _reply_to_event(event: Dict[str, Any], text: str) -> None:
    channel_id = event.get("channel", "")
    reply_ts = event.get("thread_ts", event.get("ts"))
    slack_client.chat_postMessage(channel=channel_id, thread_ts=reply_ts, text=text)


def _queue_event(event) -> None:
    queue_url = "YOUR_QUEUE_URL"  # 替换为您的队列 URL

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    body = {
        "Action": "SendMessage",
        "MessageBody": json.dumps(event),
    }

    response = requests.post(queue_url, headers=headers, data=body)

    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print("Failed to send message.")


def _make_reply(
    *,
    channel_id: str,
    reply_ts: str,
    user_message: Message,
    history: List[Message],
    is_dev: bool,
) -> None:
    response_text = None
    file_content = None
    task = None

    if user_message.args.raw:
        reply_content = reply_raw(user_message)
    else:
        task = detect_task(user_message, history)
        if task:
            print(f"Detected task: {task}")

        if task == "ads":
            reply_content = rewrite_ads(user_message, history)
        elif task == "ui":
            reply_content = rewrite_ui(user_message, history)
        elif task == "proofread":
            proofread_result = proofread(user_message, history)
            reply_content = proofread_result.corrected_text
        else:
            reply_content = reply_conversation(user_message, history)

    if not reply_content:
        return

    if len(reply_content) > 2000:
        response_text = "See the attached file."
        file_content = reply_content
    else:
        response_text = reply_content

    blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": response_text}}]

    context_elements = []
    if task:
        context_elements.append(
            {"type": "mrkdwn", "text": f"<{ABOUT_PAGE_LINK}|Task: {task}>"}
        )

    if is_dev:
        context_elements.append({"type": "plain_text", "text": "dev build"})

    if len(context_elements) > 0:
        blocks.append({"type": "context", "elements": context_elements})

    try:
        if file_content:
            slack_client.files_upload(
                channels=channel_id,
                thread_ts=reply_ts,
                content=file_content,
                initial_comment=response_text,
            )
        else:
            slack_client.chat_postMessage(
                channel=channel_id,
                thread_ts=reply_ts,
                blocks=blocks,
                text=response_text,
            )
    except SlackApiError as e:
        print(f"Failed to post message: {e.response['error']}")
