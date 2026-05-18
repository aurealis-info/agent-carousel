from aurealis_carousel.layout_moves import LAYOUT_MOVES_GUIDE, VALID_MOVES


def test_valid_moves_set_has_ten_entries():
    assert len(VALID_MOVES) == 10


def test_guide_mentions_every_move():
    for move in VALID_MOVES:
        assert move in LAYOUT_MOVES_GUIDE, f"{move!r} not found in LAYOUT_MOVES_GUIDE"
