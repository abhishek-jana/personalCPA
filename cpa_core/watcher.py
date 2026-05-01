import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cpa_core.knowledge_base import KnowledgeBase

class CollectionWatcher(FileSystemEventHandler):
    def __init__(self, kb: KnowledgeBase, base_dir: str = "data/collections"):
        self.kb = kb
        self.base_dir = base_dir

    def on_modified(self, event):
        if event.is_directory:
            # If a directory is modified (file added/removed), trigger a sync
            print(f"Watcher: Directory {event.src_path} modified, syncing...")
            self.kb.sync(self.base_dir)

    def on_created(self, event):
        if not event.is_directory:
            print(f"Watcher: File {event.src_path} created, syncing...")
            self.kb.sync(self.base_dir)

    def on_deleted(self, event):
        print(f"Watcher: Item {event.src_path} deleted, syncing...")
        self.kb.sync(self.base_dir)

def start_watcher(kb: KnowledgeBase, base_dir: str = "data/collections"):
    event_handler = CollectionWatcher(kb, base_dir)
    observer = Observer()
    observer.schedule(event_handler, base_dir, recursive=True)
    observer.start()
    print(f"Started filesystem watcher on {base_dir}")
    return observer
