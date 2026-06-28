import enum
from dataclasses import dataclass

from .models import Recitation


class Action(enum.Enum):
    NEW = "new"  # insert metadata + upload audio
    AUDIO_ONLY = "audio"  # row exists without telegram_file_id; re-send audio only


@dataclass(frozen=True)
class PlannedItem:
    recitation: Recitation
    action: Action


def build_plan(
        recitations: list[Recitation],
        done_ids: set[int],
        incomplete_ids: set[int],
        known_poem_ids: set[int],
        cap: int,
) -> list[PlannedItem]:
    healing: list[PlannedItem] = []
    new: list[PlannedItem] = []

    for recitation in recitations:
        if recitation.poem_id not in known_poem_ids:
            continue
        if recitation.id in done_ids:
            continue
        if recitation.id in incomplete_ids:
            healing.append(PlannedItem(recitation, Action.AUDIO_ONLY))
        else:
            new.append(PlannedItem(recitation, Action.NEW))

    return (healing + new)[:cap]
