import subprocess
import re
import urllib.parse

class MprisManager:
    """
    Simplified MprisManager to restore working path resolution.
    """
    def __init__(self, priority_list=None):
        self.priority_list = priority_list or []
        self.current_player = None

    def _get_output(self, cmd):
        try:
            return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8')
        except Exception:
            return ""

    def find_active_player(self):
        out = self._get_output(['gdbus', 'call', '--session', '--dest', 'org.freedesktop.DBus', 
                               '--object-path', '/org/freedesktop/DBus', '--method', 'org.freedesktop.DBus.ListNames'])
        all_players = re.findall(r"'org\.mpris\.MediaPlayer2\.([^']+)'", out)
        if not all_players: return None

        for p in all_players:
            bus = f"org.mpris.MediaPlayer2.{p}"
            if "'Playing'" in self._get_output(['gdbus', 'call', '--session', '--dest', bus, 
                                               '--object-path', '/org/mpris/MediaPlayer2', '--method', 
                                               'org.freedesktop.DBus.Properties.Get', 'org.mpris.MediaPlayer2.Player', 'PlaybackStatus']):
                self.current_player = bus
                return bus
        
        self.current_player = f"org.mpris.MediaPlayer2.{all_players[0]}"
        return self.current_player

    def get_metadata(self):
        if not self.current_player: return None
        meta = self._get_output(['gdbus', 'call', '--session', '--dest', self.current_player, 
                                '--object-path', '/org/mpris/MediaPlayer2', '--method', 
                                'org.freedesktop.DBus.Properties.Get', 'org.mpris.MediaPlayer2.Player', 'Metadata'])
        result = {}
        # Simple file URL extraction
        url_match = re.search(r"'xesam:url': <'file://([^']+)'", meta)
        if url_match:
            result['url'] = urllib.parse.unquote(url_match.group(1))
            
        title_match = re.search(r"'xesam:title': <'([^']+)'", meta)
        if title_match: result['title'] = title_match.group(1)
            
        artist_match = re.search(r"'xesam:artist': <(?:@as\s+)?\['([^']+)'", meta)
        if artist_match: result['artist'] = artist_match.group(1)
        
        return result

    def get_position(self):
        if not self.current_player: return 0.0
        out = self._get_output(['gdbus', 'call', '--session', '--dest', self.current_player, 
                               '--object-path', '/org/mpris/MediaPlayer2', '--method', 
                               'org.freedesktop.DBus.Properties.Get', 'org.mpris.MediaPlayer2.Player', 'Position'])
        match = re.search(r'int64 (\d+)', out)
        return int(match.group(1)) / 1000000.0 if match else 0.0
