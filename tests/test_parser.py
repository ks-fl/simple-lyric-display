import pytest
from core.parser import LrcParser

def test_parse_simple_lrc():
    parser = LrcParser()
    lrc_content = "[00:12.34]Hello World\n[00:15.00]Second Line"
    
    # Mocking open since parser reads from file
    import builtins
    from unittest.mock import patch, mock_open
    
    with patch("builtins.open", mock_open(read_data=lrc_content)), \
         patch("os.path.exists", return_value=True):
        lyrics = parser.parse("dummy.lrc")
        
    assert len(lyrics) == 2
    assert lyrics[0][0] == 12.34
    assert lyrics[0][1] == "Hello World"
    assert lyrics[1][0] == 15.00

def test_get_index_at():
    parser = LrcParser()
    parser.lyrics = [(10.0, "Line 1"), (20.0, "Line 2"), (30.0, "Line 3")]
    
    assert parser.get_index_at(5.0) == -1
    assert parser.get_index_at(10.0) == 0
    assert parser.get_index_at(15.0) == 0
    assert parser.get_index_at(25.0) == 1
    assert parser.get_index_at(35.0) == 2

def test_parse_empty_file():
    parser = LrcParser()
    from unittest.mock import patch, mock_open
    with patch("builtins.open", mock_open(read_data="")), \
         patch("os.path.exists", return_value=True):
        lyrics = parser.parse("empty.lrc")
    assert lyrics == []
