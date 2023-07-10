#  LLM Tracer
#  Copyright (c) 2023. Andreas Kirsch
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Inspired by https://stackoverflow.com/a/30024601/854731
from contextlib import AbstractContextManager
from timeit import default_timer


class StopwatchContext(AbstractContextManager):
    """A context the keeps track of the elapsed time.

    The elapsed time is available as the `elapsed_time` attribute.
    Nested contexts are not supported, but reusing the same context is.

    Example:
    ```
    with StopwatchContext() as stopwatch:
        ...

    print(stopwatch.elapsed_time)
    ```
    """

    def __init__(self):
        self._start_time = None
        self._elapsed_time = 0.0

    @property
    def elapsed_time(self):
        if self._start_time is not None:
            return self._elapsed_time + default_timer() - self._start_time
        return self._elapsed_time

    def __enter__(self):
        assert self._start_time is None
        self._start_time = default_timer()
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        end_time = default_timer()
        self._elapsed_time += end_time - self._start_time
        self._start_time = None
