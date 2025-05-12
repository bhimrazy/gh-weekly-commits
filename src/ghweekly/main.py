import requests
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict


def fetch_weekly_commits(
    username: str,
    repos: List[str],
    start: datetime,
    end: datetime,
    headers: Optional[Dict] = None,
) -> pd.DataFrame:
    offset_start = (0 - start.weekday()) % 7
    first_monday = pd.Timestamp(start) + pd.Timedelta(days=offset_start)

    offset_end = (0 - end.weekday()) % 7
    last_monday = pd.Timestamp(end) + pd.Timedelta(days=offset_end)

    weeks = pd.date_range(start=first_monday, end=last_monday, freq="7D")
    df = pd.DataFrame(0, index=weeks, columns=[r.split("/")[-1] for r in repos])

    for full_repo in repos:
        short_name = full_repo.split("/")[-1]
        commit_dates = []
        page = 1

        while True:
            resp = requests.get(
                f"https://api.github.com/repos/{full_repo}/commits",
                headers=headers,
                params={
                    "author": username,
                    "since": start.isoformat() + "Z",
                    "until": end.isoformat() + "Z",
                    "per_page": 100,
                    "page": page,
                },
            )
            if resp.status_code != 200:
                print(f"Error fetching {full_repo}: HTTP {resp.status_code}")
                break

            data = resp.json()
            if not data:
                break

            for c in data:
                dt = datetime.fromisoformat(
                    c["commit"]["author"]["date"].replace("Z", "+00:00")
                ).replace(tzinfo=None)
                commit_dates.append(dt)

            page += 1

        if commit_dates:
            s = pd.Series(1, index=pd.to_datetime(commit_dates))
            weekly = s.resample("W-MON", label="left", closed="left").sum()
            weekly = weekly.reindex(weeks, fill_value=0)
            df[short_name] = weekly

    return df
