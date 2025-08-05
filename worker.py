"""
RQ worker to allow adding exception handlers. To use it, start the worker with
`rq worker -w worker.Worker` (or `python worker.py`)

See details in the RQ documentation:
https://python-rq.org/docs/workers/
"""
from redis import Redis
import rq


def handle_exception(job, exc_type, exc_value, traceback):
    del exc_value, traceback
    if issubclass(exc_type, RuntimeError):
        return True
    job.retries_left = 0
    return False


class Worker(rq.Worker):
    def __init__(self, *args, exception_handlers=None, **kwargs):
        if exception_handlers is None:
            exception_handlers = [handle_exception]
        super().__init__(*args, exception_handlers=exception_handlers, **kwargs)


if __name__ == "__main__":
    w = Worker(["default"], connection=Redis())
    w.work()
