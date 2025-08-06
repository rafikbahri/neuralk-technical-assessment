"""
RQ worker to allow adding exception handlers. To use it, start the worker with
`rq worker -w worker.Worker` (or `python worker.py`)

See details in the RQ documentation:
https://python-rq.org/docs/workers/
"""
from redis import Redis
import rq
import setproctitle

from logger import get_logger

logger = get_logger(__name__)


def handle_exception(job, exc_type, exc_value, traceback):
    del traceback
    if issubclass(exc_type, RuntimeError):
        logger.warning(f"Job {job.id} encountered a RuntimeError: {exc_value}. Will retry.")
        return True
    logger.error(f"Job {job.id} failed with {exc_type.__name__}: {exc_value}. No more retries.")
    job.retries_left = 0
    return False


class Worker(rq.Worker):
    def __init__(self, *args, exception_handlers=None, **kwargs):
        if exception_handlers is None:
            exception_handlers = [handle_exception]
        super().__init__(*args, exception_handlers=exception_handlers, **kwargs)
        
    def execute_job(self, job, *args, **kwargs):
        """Override to add logging before and after job execution"""
        logger.info(f"Starting job {job.id} of type {job.func_name}")
        result = super().execute_job(job, *args, **kwargs)
        logger.info(f"Completed job {job.id} with status: {job.get_status()}")
        return result


if __name__ == "__main__":
    setproctitle.setproctitle("neuralk-worker")
    logger.info("Starting RQ worker")
    w = Worker(["default"], connection=Redis())
    try:
        w.work()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker stopped due to error: {type(e).__name__}: {e}", exc_info=True)
