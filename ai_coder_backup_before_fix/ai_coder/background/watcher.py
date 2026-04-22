"""Placeholder watcher for future local process management."""

from __future__ import annotations


class BackgroundWatcher:
    """acpx owns the real background lifecycle in this version."""

    def start(self) -> bool:
        return False

    def stop(self) -> bool:
        return False
