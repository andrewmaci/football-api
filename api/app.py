from fastapi import FastAPI

from api.v0 import counts, leagues, performances, players, teams

app = FastAPI(title="Football API")

app.include_router(players.router, prefix="/v0")
app.include_router(performances.router, prefix="/v0")
app.include_router(leagues.router, prefix="/v0")
app.include_router(teams.router, prefix="/v0")
app.include_router(counts.router, prefix="/v0")
