import pytest

from src.model import Playlist

class TestPlaylist:

    @pytest.mark.parametrize(
        "start,end,current,expected,priority",
        [
            # --- Non-wrapping cases 09:00 <-> 15:00 ---
            ("09:00", "15:00", "08:59", False, 360),  # just before start
            ("09:00", "15:00", "09:00", True, 360),   # exactly at start
            ("09:00", "15:00", "12:00", True, 360),   # during
            ("09:00", "15:00", "14:59", True, 360),   # just before end
            ("09:00", "15:00", "15:00", False, 360),  # exactly at end
            ("09:00", "15:00", "23:00", False, 360),  # way after
    
            # --- Wrapping cases (crossing midnight) 21:00 <-> 03:00 ---
            ("21:00", "03:00", "20:59", False, 360),  # just before start
            ("21:00", "03:00", "21:00", True, 360),   # exactly at start
            ("21:00", "03:00", "23:59", True, 360),   # before midnight
            ("21:00", "03:00", "00:00", True, 360),   # after midnight, inside
            ("21:00", "03:00", "02:59", True, 360),   # just before end
            ("21:00", "03:00", "03:00", False, 360),  # exactly at end
            ("21:00", "03:00", "11:00", False, 360),  # way after
    
            # --- Equal start and end 12:00 <-> 12:00 ---
            ("12:00", "12:00", "11:59", False, 0),
            ("12:00", "12:00", "12:00", False, 0),
            ("12:00", "12:00", "12:01", False, 0),
    
            # --- Midnight boundaries 18:00 <-> 00:00 ---
            ("18:00", "00:00", "17:59", False, 360),  # before start
            ("18:00", "00:00", "23:59", True, 360),   # before end
            ("18:00", "00:00", "00:00", False, 360),  # exactly at end
    
            # --- Midnight boundaries 00:00 <-> 06:00 ---
            ("00:00", "06:00", "00:00", True, 360),   # start at midnight
            ("00:00", "06:00", "05:59", True, 360),   # before end
            ("00:00", "06:00", "06:00", False, 360),  # exactly at end

            # --- All day 00:00 <-> 24:00 ---
            ("00:00", "24:00", "00:00", True, 1440),   # exactly at start
            ("00:00", "24:00", "10:00", True, 1440),   # during
            ("00:00", "24:00", "24:00", False, 1440),  # exactly at end
        ]
    )
    def test_is_active_and_priority(self, start, end, current, expected, priority):
        playlist = Playlist("Test Playlist", start, end)
        assert playlist.is_active(current) == expected
        assert playlist.get_priority() == priority

    def test_reorder_plugins(self):
        playlist = Playlist("Test Playlist", "00:00", "24:00", plugins=[
            {"plugin_id": "p1", "name": "inst1", "plugin_settings": {}, "refresh": {}},
            {"plugin_id": "p2", "name": "inst2", "plugin_settings": {}, "refresh": {}},
            {"plugin_id": "p3", "name": "inst3", "plugin_settings": {}, "refresh": {}},
        ])
        
        # Original order: inst1, inst2, inst3
        assert [p.name for p in playlist.plugins] == ["inst1", "inst2", "inst3"]
        
        # New order: inst2, inst1, inst3
        new_order_ids = ["p2:inst2", "p1:inst1", "p3:inst3"]
        result = playlist.reorder_plugins(new_order_ids)
        
        assert result is True
        assert [p.name for p in playlist.plugins] == ["inst2", "inst1", "inst3"]
        
        # Reorder with missing plugin should fail
        result = playlist.reorder_plugins(["p2:inst2", "p1:inst1"])
        assert result is False
        assert [p.name for p in playlist.plugins] == ["inst2", "inst1", "inst3"]

        # Reorder with non-existent plugin should fail
        result = playlist.reorder_plugins(["p2:inst2", "p1:inst1", "p4:inst4"])
        assert result is False
        assert [p.name for p in playlist.plugins] == ["inst2", "inst1", "inst3"]
        