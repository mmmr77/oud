from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, MetaData, Text, UniqueConstraint, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    })


class Poet(Base):
    __tablename__ = "poet"
    __table_args__ = (Index("ix_poet_name", "name"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    name: Mapped[str | None] = mapped_column(Text)
    cat_id: Mapped[int | None] = mapped_column(BigInteger)
    description: Mapped[str | None] = mapped_column(Text)


class Cat(Base):
    __tablename__ = "cat"
    __table_args__ = (
        Index("ix_cat_poet_id", "poet_id"),
        Index("ix_cat_poet_id_parent_id", "poet_id", "parent_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    poet_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("poet.id"))
    text: Mapped[str | None] = mapped_column(Text)
    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("cat.id"))
    url: Mapped[str | None] = mapped_column(Text)


class Poem(Base):
    __tablename__ = "poem"
    __table_args__ = (
        Index("ix_poem_cat_id", "cat_id"),
        Index("idx_poem_songlastchecked", "song_last_checked"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    cat_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("cat.id"))
    title: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    song_last_checked: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    username: Mapped[str | None] = mapped_column(Text)
    creation_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Opinion(Base):
    __tablename__ = "opinion"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("user.id"))
    message: Mapped[str | None] = mapped_column(Text)
    creation_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Omen(Base):
    __tablename__ = "omen"
    __table_args__ = (Index("ix_omen_poem_id", "poem_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    poem_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("poem.id"))
    interpretation: Mapped[str | None] = mapped_column(Text)


class PoemSnd(Base):
    __tablename__ = "poemsnd"
    __table_args__ = (Index("ix_poemsnd_poem_id_audio_order", "poem_id", "audio_order"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    poem_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("poem.id"))
    title: Mapped[str | None] = mapped_column(Text)
    dnldurl: Mapped[str | None] = mapped_column(Text)
    audio_order: Mapped[int | None] = mapped_column(BigInteger)
    artist: Mapped[str | None] = mapped_column(Text)
    telegram_file_id: Mapped[str | None] = mapped_column(Text)
    recitation_type: Mapped[int | None] = mapped_column(BigInteger)


class Song(Base):
    __tablename__ = "song"
    __table_args__ = (Index("ix_song_poem_id", "poem_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    poem_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("poem.id", ondelete="CASCADE"))
    title: Mapped[str | None] = mapped_column(Text)
    artist: Mapped[str | None] = mapped_column(Text)
    download_url: Mapped[str | None] = mapped_column(Text)
    telegram_file_id: Mapped[str | None] = mapped_column(Text)
    duration: Mapped[int | None] = mapped_column(Integer)
    source_page: Mapped[str | None] = mapped_column(Text)


class Fav(Base):
    __tablename__ = "fav"
    __table_args__ = (
        UniqueConstraint("poem_id", "user_id", name="uq_fav_poem_user"),
        Index("ix_fav_user_id", "user_id"),
        Index("ix_fav_poem_id", "poem_id"),
    )

    poem_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("poem.id"), primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), primary_key=True, nullable=False)


class Verse(Base):
    __tablename__ = "verse"
    __table_args__ = (
        Index("ix_verse_poem_id", "poem_id"),
        Index("ix_verse_poem_id_vorder", "poem_id", "vorder"),
    )

    poem_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("poem.id"), primary_key=True)
    vorder: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    position: Mapped[int | None] = mapped_column(BigInteger)
    text: Mapped[str | None] = mapped_column(Text)
