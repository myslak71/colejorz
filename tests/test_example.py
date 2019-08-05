"""Example tests."""


def test_placeholder(stationmaster):
    """Expected state for not doing anything Statiomaster."""
    assert stationmaster.state == {
        'pilothouse': 'working',
        'run': 'Until next instruction received',
        'speed': 0
    }
