from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Recitation:
    id: int
    poem_id: int
    audio_title: str
    mp3_url: str
    audio_artist: str
    audio_order: int
    recitation_type: int

    @classmethod
    def from_api(cls, data: dict) -> Self:
        return cls(
            id=data["id"],
            poem_id=data["poemId"],
            audio_title=data["audioTitle"],
            mp3_url=data["mp3Url"],
            audio_artist=data["audioArtist"],
            audio_order=data["audioOrder"],
            recitation_type=data["recitationType"],
        )
