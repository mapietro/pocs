from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class ThrottleState:
    failures: int
    window_start: datetime
    locked_until: datetime | None = None

class InMemoryLoginThrottle:
    """
    CONCEITO: protege contra brute force.
    Em 1 worker, memória é OK.
    Depois vira Redis/DB atrás da mesma interface.
    """
    def __init__(self, max_failures: int = 5, window_minutes: int = 10, lock_minutes: int = 5):
        self.max_failures = max_failures
        self.window = timedelta(minutes=window_minutes)
        self.lock = timedelta(minutes=lock_minutes)
        self._data: dict[str, ThrottleState] = {}

    def _now(self) -> datetime:
        return datetime.utcnow()

    def is_locked(self, key: str) -> bool:
        st = self._data.get(key)
        if not st or not st.locked_until:
            return False
        return st.locked_until > self._now()

    def register_failure(self, key: str) -> None:
        now = self._now()
        st = self._data.get(key)
        if not st or (now - st.window_start) > self.window:
            st = ThrottleState(failures=0, window_start=now)
        st.failures += 1
        if st.failures >= self.max_failures:
            st.locked_until = now + self.lock
        self._data[key] = st

    def register_success(self, key: str) -> None:
        self._data.pop(key, None)
