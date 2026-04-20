import datetime
import logging
import time
import requests

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.auroravision.net/api/rest"


class Session:
    """
    Aurora Vision API v3 client.
    Authentication: API key + Basic Auth → short-lived session token (60 min idle expiry).
    """

    _headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,pl;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    def __init__(self, user, password, api_key, installationID, timezone):
        self._user = user
        self._password = password
        self._api_key = api_key
        self._installationID = installationID
        self._timezone = timezone
        self._token = None

    def get_data(self, extended=False):
        """
        Returns energy/power data as a dict, or empty dict on failure.
        extended=False → summary dict with keys: today, start-of-1-days-ago, lifetime
        extended=True  → 15-min power bins dict keyed by 'YYYY-MM-DD HH:MM:SS'
        """
        if self._token is None:
            if not self._authenticate():
                return {}

        if extended:
            return self._fetch_extended()
        return self._fetch_summary()

    def _authenticate(self):
        """
        Exchange credentials for a session token via /authenticate.
        Returns True on success, False on failure.
        """
        try:
            resp = requests.get(
                f"{_BASE_URL}/authenticate",
                headers={**self._headers, "X-AuroraVision-ApiKey": self._api_key},
                auth=(self._user, self._password),
                timeout=15,
            )
            if resp.status_code == 200:
                self._token = resp.json()["result"]
                logger.info("Aurora Vision authentication successful")
                return True
            else:
                logger.error(
                    f"Authentication failed with HTTP {resp.status_code}: {resp.text[:500]}"
                )
                return False
        except Exception as ex:
            logger.exception(f"Authentication request failed: {ex}")
            return False

    def _get(self, url, params=None):
        """
        GET request with token header. Re-authenticates once on 401.
        Returns parsed JSON dict/list, or None on failure.
        """
        for attempt in range(2):
            try:
                resp = requests.get(
                    url,
                    headers={**self._headers, "X-AuroraVision-Token": self._token},
                    params=params,
                    timeout=15,
                )
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 401 and attempt == 0:
                    logger.warning("Token expired — re-authenticating")
                    if not self._authenticate():
                        return None
                    continue
                else:
                    logger.error(
                        f"HTTP {resp.status_code} from {url}: {resp.text[:500]}"
                    )
                    return None
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out: {url}")
                return None
            except requests.exceptions.ConnectionError as ex:
                logger.error(f"Connection error: {ex}")
                return None
            except Exception as ex:
                logger.exception(f"Unexpected error: {ex}")
                return None
        return None

    def _fetch_summary(self):
        """
        Fetches today energy, yesterday energy, and lifetime cumulative energy.
        Returns dict with keys: today, start-of-1-days-ago, lifetime.
        """
        result = {}
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)
        fmt = "%Y%m%d"

        base = f"{_BASE_URL}/v1/stats/energy/aggregated/{self._installationID}/GenerationEnergy"
        calls = [
            ("today",               f"{base}/delta",      today.strftime(fmt),     tomorrow.strftime(fmt)),
            ("start-of-1-days-ago", f"{base}/delta",      yesterday.strftime(fmt), today.strftime(fmt)),
            ("lifetime",            f"{base}/cumulative",  "20000101",              tomorrow.strftime(fmt)),
        ]

        for key, url, start_date, end_date in calls:
            data = self._get(url, params={
                "startDate": start_date,
                "endDate": end_date,
                "timeZone": self._timezone,
            })
            if data:
                r = data.get("result", {})
                result[key] = self._generate_value_unit_dict(r.get("value"), r.get("units", ""))
            else:
                logger.warning(f"No data returned for '{key}'")

        return result

    def get_irradiance(self):
        """
        Fetches 15-min irradiance timeseries (W/m²) for today.
        Returns dict keyed by 'YYYY-MM-DD HH:MM:SS' → {value, unit}, or {} on failure.
        """
        if self._token is None:
            if not self._authenticate():
                return {}

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        url = (
            f"{_BASE_URL}/v1/stats/power/timeseries/{self._installationID}"
            f"/Irradiance/average"
        )
        data = self._get(url, params={
            "startDate": today.strftime("%Y%m%d"),
            "endDate": tomorrow.strftime("%Y%m%d"),
            "timeZone": self._timezone,
            "sampleSize": "Min15",
        })

        result = {}
        for bin_item in (data or {}).get("result", []):
            ts = self._convert_epoch_to_string(bin_item["start"])
            result[ts] = self._generate_value_unit_dict(
                bin_item.get("value"), bin_item.get("units", "watts")
            )
        return result

    def _fetch_extended(self):
        """
        Fetches 15-min power timeseries for today.
        Returns dict keyed by 'YYYY-MM-DD HH:MM:SS' → {value, unit}.
        """
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        url = (
            f"{_BASE_URL}/v1/stats/power/timeseries/{self._installationID}"
            f"/GenerationPower/average"
        )
        data = self._get(url, params={
            "startDate": today.strftime("%Y%m%d"),
            "endDate": tomorrow.strftime("%Y%m%d"),
            "timeZone": self._timezone,
            "sampleSize": "Min15",
        })

        result = {}
        for bin_item in (data or {}).get("result", []):
            ts = self._convert_epoch_to_string(bin_item["start"])
            result[ts] = self._generate_value_unit_dict(
                bin_item.get("value"), bin_item.get("units", "watts")
            )
        return result

    def _convert_epoch_to_string(self, epoch):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(epoch))

    def _generate_value_unit_dict(self, value, raw_unit):
        units = {
            "kilowatts": "kW",
            "watts": "W",
            "kilowatt-hours": "kWh",
            "megawatt-hours": "MWh",
        }
        return {"value": value, "unit": units.get(raw_unit, raw_unit)}
