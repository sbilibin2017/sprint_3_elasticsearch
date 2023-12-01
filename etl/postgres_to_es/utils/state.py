from typing import Any

import dateutil.parser
import redis


class State:
    """Class for fixing and receiving etl status."""

    def __init__(self, redisclient: redis.Redis) -> None:
        self.redisclient = redisclient

    def set_state(self, key: str, value: Any) -> None:
        """Update status."""
        self.redisclient.set(key, value.isoformat())

    def get_state(self, key: str) -> Any:
        """Get status."""
        try:
            return dateutil.parser.isoparse(self.redisclient.get(key))
        except Exception:
            return None
