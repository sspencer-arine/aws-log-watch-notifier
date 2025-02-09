from logging import getLogger
from time import sleep, time
from typing import TYPE_CHECKING, Iterator

from boto3 import Session
from typeguard import typechecked

if TYPE_CHECKING:
    from mypy_boto3_logs.type_defs import FilteredLogEventTypeDef


logger = getLogger(__name__)


@typechecked
def poll_log_streams_for_log_group(boto3_session: Session, log_group: str) -> Iterator["FilteredLogEventTypeDef"]:

    logs_client = boto3_session.client("logs")

    last_event_timestamp = int(time() * 1000)

    sleep_seconds = 15

    while True:
        filter_log_events_paginator = logs_client.get_paginator("filter_log_events")

        event_timestamps = []

        for filter_log_events_page in filter_log_events_paginator.paginate(
            logGroupName=log_group,
            # Silly trick to avoid duplicate events from appearing as we increment the
            # last_event_timestamp to the max of the event timestamps we've seen.  This adds one
            # msec.
            startTime=last_event_timestamp + 1,
        ):
            for event in filter_log_events_page["events"]:
                event_timestamp = event.get("timestamp", 0)
                event_timestamps.append(event_timestamp)

                yield event

        last_event_timestamp = max([last_event_timestamp, *event_timestamps])

        logger.debug(f"Sleeping for {sleep_seconds} seconds")
        sleep(sleep_seconds)
