from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from datetime import date
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class League(Base):
    __tablename__ = "league"
    league_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    league_name: Mapped[str]
    scoring_type: Mapped[str]
    last_changed_date: Mapped[date]
    
    teams: Mapped[List["Team"]] = relationship(back_populates="league")

class Team(Base):
    __tablename__ = "team"
    team_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("league.league_id"))
    team_name: Mapped[str]
    last_changed_date: Mapped[date]
    
    league: Mapped["League"] = relationship(back_populates="teams")
    players: Mapped[List["Player"]] = relationship(secondary="team_player", back_populates="teams")

class Player(Base):
    __tablename__ = "player"
    player_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    gsis_id: Mapped[Optional[str]]
    first_name: Mapped[str]
    last_name: Mapped[str]
    position: Mapped[str]
    last_changed_date: Mapped[date]
    
    performances: Mapped[List["Performance"]] = relationship(back_populates="player")
    teams: Mapped[List["Team"]] = relationship(secondary="team_player", back_populates="players")

class TeamPlayer(Base):
    __tablename__ = "team_player"
    team_id: Mapped[int] = mapped_column(ForeignKey("team.team_id"), primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("player.player_id"), primary_key=True, index=True)
    last_changed_date: Mapped[date]

class Performance(Base):
    __tablename__ = "performance"
    performance_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("player.player_id"))
    week_number: Mapped[str]
    fantasy_points: Mapped[float]
    last_changed_date: Mapped[date]
    
    player: Mapped["Player"] = relationship(back_populates="performances")