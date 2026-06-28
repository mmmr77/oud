from recitation_uploader import selection
from recitation_uploader.models import Recitation
from recitation_uploader.selection import Action

KNOWN = {1, 2, 3}


def rec(id_, poem_id=1):
    return Recitation(id_, poem_id, "t", "u", "a", 1, 0)


def test_new_recitation_is_planned_as_new():
    plan = selection.build_plan([rec(10)], set(), set(), KNOWN, cap=100)
    assert len(plan) == 1
    assert plan[0].action == Action.NEW
    assert plan[0].recitation.id == 10


def test_done_recitation_is_dropped():
    plan = selection.build_plan([rec(10)], {10}, set(), KNOWN, cap=100)
    assert plan == []


def test_incomplete_recitation_is_audio_only():
    plan = selection.build_plan([rec(10)], set(), {10}, KNOWN, cap=100)
    assert len(plan) == 1
    assert plan[0].action == Action.AUDIO_ONLY


def test_unknown_poem_is_filtered_out():
    plan = selection.build_plan([rec(10, poem_id=999)], set(), set(), KNOWN, cap=100)
    assert plan == []


def test_healing_ordered_before_new():
    plan = selection.build_plan([rec(10), rec(11)], set(), {11}, KNOWN, cap=100)
    assert [(p.recitation.id, p.action) for p in plan] == [
        (11, Action.AUDIO_ONLY),
        (10, Action.NEW),
    ]


def test_cap_does_not_starve_healing():
    plan = selection.build_plan([rec(10), rec(11), rec(12)], set(), {11}, KNOWN, cap=1)
    assert len(plan) == 1
    assert plan[0].recitation.id == 11
    assert plan[0].action == Action.AUDIO_ONLY


def test_empty_inputs():
    assert selection.build_plan([], set(), set(), KNOWN, cap=100) == []
