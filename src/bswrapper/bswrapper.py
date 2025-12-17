from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
import time
import requests

class APIError(Exception):
    def __init__(self, status_code: int, message: str, *, response_text: str | None = None):
        super().__init__(f'API Error: {status_code} - {message}')
        self.status_code = status_code
        self.response_text = response_text

class NotFound(APIError):
    pass

class Unauthorized(APIError):
    pass

class RateLimited(APIError):
    def __init__(self, status_code: int, message: str, retry_after: float | None):
        super().__init__(status_code, message)
        self.retry_after = retry_after

@dataclass(slots = True)
class ClubSummary:
    tag: str | None
    name: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "ClubSummary":
        return cls(
            tag = data.get("tag"),
            name = data.get("name")
        )

@dataclass(slots = True)
class Player:
    tag: str | None
    name: str | None
    trophies: int | None
    highest: int | None
    explevel: int | None
    club: Optional[ClubSummary]
    solo: int | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Player":
        club_data = data.get("club")
        return cls(
            tag=data.get("tag"),
            name=data.get("name"),
            trophies=data.get("trophies"),
            highest=data.get("highestTrophies"),
            explevel=data.get("expLevel"),
            club=ClubSummary.from_api(club_data) if isinstance(club_data, dict) else None,
            solo=data.get("soloVictories"),
        )
    
@dataclass(slots = True)
class Club:
    tag: str | None
    name: str | None
    trophies: int | None
    required: int | None
    type: str | None
    description: str | None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Club":
        return cls(
            tag=data.get("tag"),
            name=data.get("name"),
            trophies=data.get("trophies"),
            required=data.get("requiredTrophies"),
            type=data.get("type"),
            description=data.get("description")
        )

class BSClient:
    def __init__(
        self,
        apiKey: str,
        *,
        timeout: float = 10.0,
        max_retries: int = 1,
        baseURL: str = "https://api.brawlstars.com/v1",
    ):
        self.apiKey = apiKey
        self.baseURL = baseURL.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.apiKey}",
                "Accept": "application/json",
            }
        )

    def close(self) -> None:
        self._session.close()

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        tag = tag.strip().upper()
        if tag.startswith("#"):
            tag = tag[1:]
        return tag

    def _request_json(self, endpoint: str) -> dict[str, Any]:
        url = f"{self.baseURL}{endpoint}"

        for attempt in range(self.max_retries + 1):
            try:
                resp = self._session.get(url, timeout=self.timeout)
            except requests.RequestException as e:
                raise APIError(f"Network error: {e}") from e

            if resp.status_code == 200:
                return resp.json()

            # Rate limit
            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        ra = float(retry_after)
                    except ValueError:
                        ra = 1.0 # fallback
                else:
                    ra = 2.0 ** attempt # exponential backoff incase not retry_after

                if attempt < self.max_retries:
                    time.sleep(ra + 0.1)
                    continue

                raise RateLimited(429, "Rate limited", retry_after = ra)

            # Other common statuses
            if resp.status_code == 404:
                raise NotFound(404, "Not found", response_text=resp.text)
            if resp.status_code in (401, 403):
                raise Unauthorized(resp.status_code, "Unauthorized/Forbidden", response_text=resp.text)

            raise APIError(resp.status_code, resp.reason, response_text=resp.text)

        # logically unreachable
        raise APIError("Unexpected retry loop exit")
    
    def __enter__(self) -> "BSClient":
        return self
    
    def __close__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def getplayer(self, tag: str) -> Player:
        tag = self._normalize_tag(tag)
        data = self._request_json(f"/players/%23{tag}")
        return Player.from_api(data)

    def getclub(self, tag: str) -> Club:
        tag = self._normalize_tag(tag)
        data = self._request_json(f"/clubs/%23{tag}")
        return Club.from_api(data)
    
    

