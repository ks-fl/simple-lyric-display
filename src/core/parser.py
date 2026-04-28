import os
import re


class LrcParser:
    """
    Simplified LRC parser as it was before the breaking refactor.
    """

    def __init__(self):
        self.lyrics = []

    def parse(self, lrc_path):
        self.lyrics = []
        if not lrc_path or not os.path.exists(lrc_path):
            return []

        try:
            with open(lrc_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    # Very simple regex for [mm:ss.xx]
                    matches = re.findall(r"\[(\d+):(\d+\.?\d*)\]", line)
                    text = re.sub(r"\[.*?\]", "", line).strip()
                    for m, s in matches:
                        self.lyrics.append((int(m) * 60 + float(s), text))
            self.lyrics.sort()
            return self.lyrics
        except Exception:
            return []

    def find_index(self, current_seconds):
        index = -1
        for i, (sec, _text) in enumerate(self.lyrics):
            if current_seconds >= sec:
                index = i
            else:
                break
        return index
