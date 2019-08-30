"""Colejorz stationmaster."""
from typing import Dict, Union
from queue import Queue

from colejorz.pilothouse import Pilothouse


class StationMaster:
    """
    Colejorz station master.

    Triggers speed and direction change in the pilothouse.
    """

    def __init__(self):
        """Initialize stationmaster, queue and Pilothouse."""
        self._queue = Queue()  # type: Queue[Dict[str, int]]
        self._pilothouse = Pilothouse(self._queue)

    @property
    def state(self) -> Dict[str, Union[int, str]]:
        """Return state."""
        return self._pilothouse.status

    def change_state(self, level: int, timed: int = 0):
        """Request state change (speed and direction)."""
        self._queue.put({'speed': level, 'timed': timed})
        self._pilothouse.event.set()

    def exit(self):
        """Exit the Stationmaster."""
        self._pilothouse.exit()
