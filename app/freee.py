import datetime
import os
import requests
from db import Cursor


class FreeeUser:
    def __init__(self, employee_id=None):
        self.employee_id = employee_id

    @classmethod
    def get_employee_id(cls):
        try:
            with Cursor() as cur:
                cur.execute(
                    "SELECT employee_id FROM freee_users LIMIT 1",
                )
            row = cur.fetchone()

            return cls(
                employee_id=row[0],
            )
        except Exception:
            return cls()

    def add(self, employee_id):
        with Cursor() as cur:
            cur.execute(
                "INSERT INTO freee_users (employee_id) VALUES (%s)",
                (employee_id,),
            )


class FreeeAccessToken:
    def __init__(self, token=None, refresh_token=None, expired_at=None):
        self.token = token
        self.refresh_token = refresh_token
        self.expired_at = expired_at

    @classmethod
    def get_token(cls):
        try:
            with Cursor() as cur:
                cur.execute(
                    "SELECT token, refresh_token, expired_at FROM freee_access_tokens LIMIT 1",
                )
                row = cur.fetchone()
                return cls(token=row[0], refresh_token=row[1], expired_at=row[2])
        except Exception:
            return cls()

    def add(self, token, refresh_token, expired_at):
        with Cursor() as cur:
            cur.execute(
                "INSERT INTO freee_access_tokens (token, refresh_token, expired_at) VALUES (%s, %s, %s)",
                (
                    token,
                    refresh_token,
                    expired_at,
                ),
            )

    def update_token(self, token, expired_at):
        with Cursor() as cur:
            cur.execute(
                "UPDATE freee_access_tokens SET token = %s, expired_at = %s",
                (
                    token,
                    expired_at,
                ),
            )


def get_and_add_token():
    freee_access_token = FreeeAccessToken()

    row = freee_access_token.get_token()

    # first time
    if row.token is None:
        params = {
            "grant_type": "authorization_code",
            "client_id": os.environ["FREEE_CLIENT_ID"],
            "client_secret": os.environ["FREEE_CLIENT_SECRET"],
            "code": os.environ["FREEE_CODE"],
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post(
            "https://accounts.secure.freee.co.jp/public_api/token",
            params=params,
            headers=headers,
        )
        j = r.json()

        token = j["access_token"]
        refresh_token = j["refresh_token"]
        created_unixtime = j["created_at"]
        created_at = datetime.datetime.fromtimestamp(created_unixtime)
        expires_seconds = j["expires_in"]
        expired_at = created_at + datetime.timedelta(seconds=expires_seconds)

        freee_access_token = FreeeAccessToken()
        freee_access_token.add(
            token=token, refresh_token=refresh_token, expired_at=expired_at
        )
        return token

    # valied token
    elif row.expired_at >= datetime.datetime.now():
        return row.token

    # if the token has expired, use refresh token to get the token again
    else:
        params = {
            "grant_type": "refresh_token",
            "refresh_token": row.refresh_token,
            "client_id": os.environ["FREEE_CLIENT_ID"],
            "client_secret": os.environ["FREEE_CLIENT_SECRET"],
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        }

        response = requests.post(
            "https://accounts.secure.freee.co.jp/public_api/token",
            data=params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        j = response.json()

        token = j["access_token"]
        created_unixtime = j["created_at"]
        created_at = datetime.datetime.fromtimestamp(created_unixtime)
        expires_seconds = j["expires_in"]
        expired_at = created_at + datetime.timedelta(seconds=expires_seconds)

        freee_access_token.update_token(token=token, expired_at=expired_at)
        return token


def get_and_add_employee_id():
    user = FreeeUser()
    row = user.get_employee_id()
    if row.employee_id is not None:
        return row.employee_id

    token = get_and_add_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }
    r = requests.get("https://api.freee.co.jp/hr/api/v1/users/me", headers=headers)
    j = r.json()

    employee_id = j["companies"][0]["employee_id"]
    user.add(employee_id)

    return employee_id


def is_working():
    try:
        employee_id = get_and_add_employee_id()
        date = get_date()

        token = get_and_add_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        }
        r = requests.get(
            "https://api.freee.co.jp/hr/api/v1/employees/{}/work_records/{}".format(
                employee_id, date
            ),
            headers=headers,
        )
        j = r.json()

        clock_in_at = j["clock_in_at"]
        clock_out_at = j["clock_out_at"]

        if clock_in_at is None:
            return False

        if clock_out_at is None:
            return True

        clock_in_at = datetime.datetime.strptime(
            j["clock_in_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        clock_out_at = datetime.datetime.strptime(
            j["clock_out_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

        return now >= clock_in_at and now <= clock_out_at
    except Exception:
        return True


def get_date():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

    # 1 -> 01
    month = str(now.month).rjust(2, "0")
    day = str(now.day).rjust(2, "0")
    return "{}{}".format(month, day)
