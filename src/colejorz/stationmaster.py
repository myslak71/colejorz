"""Colejorz stationmaster."""
from queue import Queue

from colejorz.pilothouse import Pilothouse


class StationMaster:
    def __init__(self):
        self._queue = Queue()
        self._pilothouse = Pilothouse(self._queue)

    @property
    def state(self):
        return self._pilothouse.status

    def change_state(self, level):
        self._queue.put(level)
        self._pilothouse.event.set()

    def exit(self):
        self._pilothouse.exit()