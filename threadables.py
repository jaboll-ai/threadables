"""
threadables: A minimal producer-consumer threading toolkit with graceful shutdowns.

Provides:
- Enqueuer: A thread class for feeding a queue from an iterator.
- Worker: A thread class for consuming items from a queue.
- Colorized console output for lifecycle events.
"""

from collections.abc import Callable
from typing import Iterator
import threading
from queue import Queue, Empty, Full

COLORAMA_WARNING = True

try:
    from colorama import Style, Fore
except ImportError:
    print("colorama is not installed. Install with 'pip install colorama'\nDisable warning with 'threadables.COLORAMA_WARNING = False'")

def __clrd(text, color:str, style:str = "normal"):
    try:
        c = getattr(Fore, color.upper())
        s = getattr(Style, style.upper())
    except AttributeError:
        return text
    return f"{c}{s}{text}{Style.RESET_ALL}"
        
def enqueuer(queue: Queue, iterator: Iterator, filter_func: Callable, n_workers: int, n:int =None, kill_event: threading.Event = None):
    """
    `For convenience use Enqueuer class.`
    Function to be used as a target for threading.Thread.
    Enqueue items from an iterator into a Queue, while optionally limiting the
    number of items and checking for a kill event. When done, place a sentinel
    value (None) into the queue to tell workers to quit.

    :param queue: The queue to put items into.
    :param iterator: An iterator yielding items to enqueue.
    :param filter_func: A callable that takes an item and returns True if it
                        should be enqueued, False otherwise. (e.g. `lambda x: x > 0`)
    :param n_workers: The number of worker threads that will be consuming the
                      queue. Needed for graceful exit. If set to 0, the workers
                      need to be killed manually.
    :param n: The maximum number of items to enqueue, or None for no limit.
    :param kill_event: An optional threading.Event that, if set, will cause the
                       enqueuer to exit early.
    """
    i = 0
    iterator = iter(iterator)
    file = next(iterator)
    while True:
        if filter_func(file):
            if kill_event and kill_event.is_set():
                print(f"{__clrd('Enqueuer', 'magenta')} {__clrd('killed', 'red')}")
                return
            try:
                queue.put(file, timeout=10)
            except Full: continue
            i += 1
            if n is not None and i >= n:
                break
        try:
            file = next(iterator)
        except StopIteration:
            break
    for _ in range(n_workers):
        queue.put(None)  # Sentinels to stop workers
    print(f"{__clrd('Enqueuer', 'magenta')} {__clrd('exited gracefully', 'green')}")
    
    
def worker(queue: Queue, func: Callable, exit_func: Callable=None, kill_event: threading.Event = None):
    """
    `For convenience use Worker class.`
    Function to be used as a target for threading.Thread.
    Consume items from a Queue and call a given function on each item. If the
    item is None, exit the loop. If a kill event is given and set, exit the loop
    early.

    :param queue: The queue to consume from.
    :param func: A callable that takes a single argument.
    :param exit_func: An optional callable to call when exiting the loop.
    :param kill_event: An optional threading.Event that, if set, will cause the
                       worker to exit early.
    """
    while True:
        if kill_event and kill_event.is_set():
            print(f"{__clrd('Worker', 'yellow')}{__clrd(f'<{func.__name__}>', 'yellow', 'dim')} {__clrd('killed', 'red')}")
            return
        try:
            result = queue.get(timeout=10)
        except Empty:
            continue
        if result is None:
            if exit_func is not None: exit_func()
            break
        func(result)
        queue.task_done()
    print(f"{__clrd('Worker', 'yellow')}{__clrd(f'<{func.__name__}>', 'yellow', 'dim')} {__clrd('exited gracefully', 'green')}")
    

class Enqueuer(threading.Thread):
    """
    `Enqueuer` is a convenience wrapper around the enqueuer method, extending threading.Thread.
    This class is used for enqueuing items into a queue from an iterator, applying a filter function
    to determine which items to enqueue. It also handles sentinels for workers so they
    can gracefully exit. It can also be killed when signaled by a threading.Event.
    """

    def __init__(self, queue: Queue, iterator: Iterator, filter_func: Callable, n_workers: int, n:int =None, kill_event: threading.Event = None, *args, **kwargs):
        """
        :param queue: The queue to put items into.
        :param iterator: An iterator yielding items to enqueue.
        :param filter_func: A callable that takes an item and returns True if it
                            should be enqueued, False otherwise. (e.g. `lambda x: x > 0`)
        :param n_workers: The number of worker threads that will be consuming the
                queue. Needed for graceful exit. If set to 0, the workers
                need to be killed manually.
        :param n: The maximum number of items to enqueue, or None for no limit.
        :param kill_event: An optional threading.Event that, if set, will cause the
                        enqueuer to exit early.
        """
        kwargs.pop("target", None)
        kwargs.pop("args", None)
        super().__init__(target=enqueuer, args=(queue, iterator, filter_func, n_workers, n, kill_event), *args, **kwargs)
        
class Worker(threading.Thread):
    """
    `Worker` is a convenience wrapper around the worker method, extending threading.Thread.
    This class is used for consuming items from a queue and applying a function to each item.
    It also handles sentinels for workers so they can gracefully exit. It can also be killed when signaled by a threading.Event.
    """
    def __init__(self, queue: Queue, func: Callable, exit_func: Callable=None, kill_event: threading.Event = None, *args, **kwargs):
        """
        :param queue: The queue to consume from.
        :param func: A callable that takes a single argument.
        :param exit_func: An optional callable to call when exiting the loop.
        :param kill_event: An optional threading.Event that, if set, will cause the
                        worker to exit early.
        """
        kwargs.pop("target", None)
        kwargs.pop("args", None)
        super().__init__(target=worker, args=(queue, func, exit_func, kill_event), *args, **kwargs)