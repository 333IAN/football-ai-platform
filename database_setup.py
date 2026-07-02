import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

# 1. Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)

Base = declarative_base()

# 2. Define Models with STRING IDs
class Team(Base):
    __tablename__ = 'teams'

    team_id = Column(String(50), primary_key=True) 
    name = Column(String(100), nullable=False)
    country = Column(String(100))
    fifa_rank = Column(Integer)
    elo_rating = Column(Float, default=1500.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    home_matches = relationship("Match", foreign_keys='Match.home_team_id', back_populates="home_team")
    away_matches = relationship("Match", foreign_keys='Match.away_team_id', back_populates="away_team")
    players = relationship("Player", back_populates="team")


class Match(Base):
    __tablename__ = 'matches'

    match_id = Column(String(50), primary_key=True)
    home_team_id = Column(String(50), ForeignKey('teams.team_id'), index=True)
    away_team_id = Column(String(50), ForeignKey('teams.team_id'), index=True)
    match_date = Column(DateTime, nullable=False, index=True)
    competition_name = Column(String(100), nullable=False)
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_xg = Column(Float)
    away_xg = Column(Float)
    status = Column(String(50), default='SCHEDULED')
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")


class Player(Base):
    __tablename__ = 'players'

    player_id = Column(String(50), primary_key=True)
    team_id = Column(String(50), ForeignKey('teams.team_id'))
    name = Column(String(150), nullable=False)
    position = Column(String(50))

    team = relationship("Team", back_populates="players")
    events = relationship("MatchEvent", back_populates="player")


class MatchEvent(Base):
    __tablename__ = 'match_events'

    event_id = Column(Integer, primary_key=True, autoincrement=True) # We let Postgres auto-generate this one
    match_id = Column(String(50), ForeignKey('matches.match_id', ondelete='CASCADE'), index=True)
    player_id = Column(String(50), ForeignKey('players.player_id'))
    minute = Column(Integer, nullable=False)
    event_type = Column(String(50), nullable=False, index=True)
    x_coordinate = Column(Float)
    y_coordinate = Column(Float)
    event_details = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())

    match = relationship("Match", back_populates="events")
    player = relationship("Player", back_populates="events")


if __name__ == "__main__":
    print("Rebuilding database schema with String IDs...")
    Base.metadata.create_all(bind=engine)
    print("Database schema successfully updated!")