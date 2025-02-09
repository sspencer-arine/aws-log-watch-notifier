import json
from collections import deque
from logging import getLogger
from typing import TYPE_CHECKING, Any

from boto3 import Session
from httpx import Client
from typer import Context, Typer

from aws_log_watch_notifier.client.poll import poll_log_streams_for_log_group

if TYPE_CHECKING:
    from mypy_boto3_logs.type_defs import FilteredLogEventTypeDef

logger = getLogger(__name__)

notify_app = Typer(name="notify")


@notify_app.callback()
def notify_callback(ctx: Context):
    pass


@notify_app.command(name="test")
def notify_command_test(ctx: Context):
    pass


@notify_app.command(name="run")
def notify_command_run(
    ctx: Context,
    log_group: str,
    slack_notification_url: str,
    lambda_runtime_errors: bool = False,
    lambda_application_errors: bool = False,
    provisioned_throughput_exceeded: bool = False,
):

    ctx.ensure_object(dict)

    aws_profile = ctx.obj["aws_profile"] or None

    boto3_session = Session(profile_name=aws_profile)

    buffer: deque["FilteredLogEventTypeDef"] = deque(maxlen=10000)

    event_log_stream_contexts: dict[str, dict[str, Any]] = {}

    with Client() as httpx_client:
        httpx_client.post(
            slack_notification_url,
            json={
                "json_code": "...",
                "log_stream_name": f"Starting polling for {log_group}",
            },
        )

    for event in poll_log_streams_for_log_group(boto3_session, log_group):
        buffer.append(event)

        # {'logStreamName': '2025/01/28/[$LATEST]f2226dc7c24043a4adb2824eec68fc5e', 'timestamp':
        # 1738028601527, 'message': 'START RequestId: 75cea95f-5461-40da-8dca-69448abc4c13
        # Version: $LATEST\n', 'ingestionTime': 1738028604499, 'eventId':
        # '38759332990412138916068335471738556083422818113071611908'}

        event_log_stream_name = event.get("logStreamName", "")
        event_timestamp = event.get("timestamp", 0)
        event_message = event.get("message", "")
        event_id = event.get("eventId", "")

        if not event_log_stream_name or not event_timestamp or not event_message or not event_id:
            continue

        if event_message.startswith("START RequestId:"):
            event_metadata = event_message.split(maxsplit=1)[-1]
            event_log_stream_contexts[event_log_stream_name] = {
                "type": "lambda",
                "metadata": event_metadata,
                "start": event_timestamp,
                "end": None,
                "errors": [],
            }

        event_log_stream_context = event_log_stream_contexts.get(event_log_stream_name)

        if event_log_stream_context:
            if event_log_stream_context.get("type") == "lambda":
                log_steam_data_errors = event_log_stream_context.get("errors")

                if not isinstance(log_steam_data_errors, list):
                    continue

                event_error = False

                for event_message_line in event_message.splitlines():
                    if lambda_runtime_errors and "Task timed out" in event_message_line:
                        event_error = True

                    if lambda_application_errors and event_message_line.startswith("Traceback"):
                        event_error = True

                    if (
                        provisioned_throughput_exceeded
                        and "ProvisionedThroughputExceededException" in event_message_line
                    ):
                        event_error = True

                if event_error:
                    log_steam_data_errors.append(event_message)

                if event_message.startswith("END RequestId:"):
                    event_log_stream_context["end"] = event_timestamp

                    if event_log_stream_context.get("errors"):
                        with Client() as httpx_client:
                            httpx_client.post(
                                slack_notification_url,
                                json={
                                    "json_code": f"{json.dumps(event_log_stream_context, indent=2, sort_keys=True)}",
                                    "log_stream_name": event_log_stream_name,
                                },
                            )
