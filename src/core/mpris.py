import re
import subprocess
import urllib.parse

# DBus Constants
DBUS_DEST_MPRIS = "org.freedesktop.DBus"
DBUS_PATH_MPRIS = "/org/freedesktop/DBus"
MPRIS_PREFIX = "org.mpris.MediaPlayer2."
MPRIS_INTERFACE_PLAYER = "org.mpris.MediaPlayer2.Player"
MPRIS_OBJECT_PATH = "/org/mpris/MediaPlayer2"


class MprisManager:
    """
    Manages communication with MPRIS-compatible media players over DBus.
    """

    def __init__(self, selected_player=None):
        self.selected_player = selected_player
        self.current_player = None

    def _call_dbus(self, dest, method, *args, object_path=MPRIS_OBJECT_PATH):
        """Query: Execute a DBus call via gdbus."""
        cmd = [
            "gdbus",
            "call",
            "--session",
            "--dest",
            dest,
            "--object-path",
            object_path,
            "--method",
            method,
        ]
        cmd.extend(args)
        try:
            return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8")
        except subprocess.CalledProcessError:
            return ""

    def get_available_players(self):
        """Query: List all available MPRIS player names."""
        out = self._call_dbus(
            DBUS_DEST_MPRIS, "org.freedesktop.DBus.ListNames", object_path=DBUS_PATH_MPRIS
        )
        return re.findall(r"'org\.mpris\.MediaPlayer2\.([^']+)'", out)

    def find_active_player(self):
        """Query: Locate the active MPRIS player based on selection or playback status."""
        all_players = self.get_available_players()
        if not all_players:
            self.current_player = None
            return None

        # 1. If a specific player is selected, use it if available
        if self.selected_player and self.selected_player in all_players:
            self.current_player = f"{MPRIS_PREFIX}{self.selected_player}"
            return self.current_player

        # 2. Otherwise, find one that is actually 'Playing'
        for p in all_players:
            bus = f"{MPRIS_PREFIX}{p}"
            status = self._call_dbus(
                bus, "org.freedesktop.DBus.Properties.Get", MPRIS_INTERFACE_PLAYER, "PlaybackStatus"
            )
            if "'Playing'" in status:
                self.current_player = bus
                return bus

        # 3. Fallback to the first available player
        self.current_player = f"{MPRIS_PREFIX}{all_players[0]}"
        return self.current_player

    def get_metadata(self):
        """Query: Retrieve metadata for the currently active track."""
        if not self.current_player:
            return None

        meta_str = self._call_dbus(
            self.current_player,
            "org.freedesktop.DBus.Properties.Get",
            MPRIS_INTERFACE_PLAYER,
            "Metadata",
        )
        if not meta_str:
            return None

        return {
            "url": self._parse_metadata_field(
                meta_str, r"'xesam:url': <'file://([^']+)'", unquote=True
            ),
            "title": self._parse_metadata_field(meta_str, r"'xesam:title': <'([^']+)'"),
            "artist": self._parse_metadata_field(
                meta_str, r"'xesam:artist': <(?:@as\s+)?\['([^']+)'"
            ),
        }

    def _parse_metadata_field(self, meta, pattern, unquote=False):
        match = re.search(pattern, meta)
        if not match:
            return ""
        val = match.group(1)
        return urllib.parse.unquote(val) if unquote else val

    def get_position(self):
        """Query: Get current playback position in seconds."""
        if not self.current_player:
            return 0.0

        out = self._call_dbus(
            self.current_player,
            "org.freedesktop.DBus.Properties.Get",
            MPRIS_INTERFACE_PLAYER,
            "Position",
        )
        match = re.search(r"int64 (\d+)", out)
        # Position is in microseconds
        return int(match.group(1)) / 1000000.0 if match else 0.0
