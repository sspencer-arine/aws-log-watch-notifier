from enum import Enum
from logging import basicConfig, getLogger

from typer import Context, Typer

from aws_log_watch_notifier.cli.notify import notify_app

logger = getLogger(__name__)

root_app = Typer()
root_app.add_typer(notify_app)


# Add enum for all logging levels
class LogLevelEnum(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@root_app.callback()
def root_callback(ctx: Context, log_level: LogLevelEnum = LogLevelEnum.WARNING, aws_profile: str | None = None):
    ctx.ensure_object(dict)

    ctx.obj["aws_profile"] = aws_profile

    basicConfig()
    getLogger("aws_log_watch_notifier").setLevel(log_level.name)
