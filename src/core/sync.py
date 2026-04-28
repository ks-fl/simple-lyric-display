import os

from PySide6.QtCore import QObject, QTimer

from core.mpris import MprisManager
from core.parser import LrcParser
from utils.constants import TIMER_INTERVAL_MS


class SyncManager(QObject):
    """
    Manages synchronization between the MPRIS player and the lyrics widget.

    This class monitors the active media player via MPRIS, parses the corresponding
    LRC files, and calculates the current lyric index based on playback position.
    """

    def __init__(self, config, lyrics_widget):
        """
        Initializes the SyncManager with configuration and a target widget.

        Args:
            config (Config): Application configuration manager.
            lyrics_widget (LyricsWidget): The widget responsible for rendering lyrics.
        """
        super().__init__()
        self.config = config
        self.lyrics_widget = lyrics_widget
        self.mpris = MprisManager(self.config.get(["mpris", "selected_player"]))
        self.parser = LrcParser()

        self.curr_track = ""
        self.last_idx = -1

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sync_state)

    def start(self):
        """
        Starts the synchronization timer.
        """
        self.timer.start(TIMER_INTERVAL_MS)

    def stop(self):
        """
        Stops the synchronization timer.
        """
        self.timer.stop()

    def sync_state(self):
        """
        Timer callback that synchronizes the UI with the MPRIS player state.

        Queries the player for metadata and playback position, updates the
        lyrics data if the track has changed, and updates the current lyric
        highlighting index.
        """
        if not self.mpris.find_active_player():
            return

        meta = self.mpris.get_metadata()
        if not meta:
            return

        # Handle track change
        self._sync_track(meta)

        # Sync lyric position
        pos = self.mpris.get_position()
        idx = self.parser.find_index(pos)
        if idx != self.last_idx:
            self.last_idx = idx
            self.lyrics_widget.set_current_index(idx)

    def _sync_track(self, meta):
        """
        Updates the lyric parser and widget if a new track is detected.

        Args:
            meta (dict): Metadata of the currently playing track.
        """
        url = meta.get("url", "")
        if url == self.curr_track:
            return

        self.curr_track = url
        lrc_path = os.path.splitext(url)[0] + ".lrc"
        self.lyrics_widget.set_lyrics(self.parser.parse(lrc_path), meta)
        self.last_idx = -2
