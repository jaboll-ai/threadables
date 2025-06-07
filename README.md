# 🧵 threadables

A lightweight Python utility for parallelizing producer-consumer workflows using threads and queues — with graceful shutdowns, filtering, and clean output.

## ✨ Features

- Threaded enqueuer and worker design
- Optional kill signals for early exit
- Simple filter functions and exit hooks
- Colorized console logging with `colorama`
- Drop-in `Enqueuer` and `Worker` thread classes

## 📦 Installation

- Download files and put into your project or use:

```bash
git add submodule https://github.com/jaboll-ai/threadables
```
- For coloued output:
```bash
pip install colorama
```
## 🚀 Quick Start

```python
from queue import Queue
from threadables import Enqueuer, Worker
import threading

def my_filter(item):
    return item % 2 == 0

def process(item):
    print(f"Processing {item}")

queue = Queue()
kill_event = threading.Event()

producer = Enqueuer(queue, range(10), my_filter, n_workers=1, kill_event=kill_event)
consumer = Worker(queue, process, kill_event=kill_event)

producer.start()
consumer.start()

producer.join()
queue.join()
```

## 🛑 Shutdown

To stop all threads early:

```python
kill_event.set()
```

This signals both the enqueuer and workers to exit cleanly. Either pass the same `threading.Event` or diffrent once depending on use case.

## 📁 Project Structure

```
threadables/
├── __init__.py
├── threadables.py
```

## 🧪 Example Use Cases

- Parallel file processing
- Filtered batch data pipelines
- Multi-threaded logging or scraping tools

---

## ✅ Requirements

- Python 3.7+
- `colorama` for styled terminal output

---
