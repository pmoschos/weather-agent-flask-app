import asyncio
import threading
from concurrent.futures import Future
from typing import Any, Coroutine, Optional


class AsyncRunner:
    """
    Runs coroutines on a dedicated event loop in a background thread.
    Use this to avoid creating a new loop per request in Flask.
    """
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro: Coroutine[Any, Any, Any], timeout: Optional[float] = None):
        future: Future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    def stop(self):
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=2)
