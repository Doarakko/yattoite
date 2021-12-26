import datetime
import os
import requests
from db import Cursor


def initialise():
    try:
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
        # print(json.dumps(j, indent=2))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(token),
        }
        r = requests.get("https://api.freee.co.jp/hr/api/v1/users/me", headers=headers)
        j = r.json()
        # print(json.dumps(j, indent=2))
        employee_id = j["companies"][0]["employee_id"]
        freee_user = FreeeUser()
        freee_user.add(employee_id)
    except Exception as e:
        print(e)


class FreeeUser:
    def __init__(self, employee_id=None):
        self.employee_id = employee_id

    def create_table(self):
        with Cursor() as cur:
            cur.execute(
                "CREATE TABLE freee_users (\
                        id SERIAL NOT NULL,\
                        employee_id integer,\
                        created_at TIMESTAMP DEFAULT NOW(),\
                        updated_at TIMESTAMP DEFAULT NOW(),\
                        PRIMARY KEY (id)\
                    );"
            )

    @classmethod
    def get_employee_id(cls):
        with Cursor() as cur:
            cur.execute(
                "SELECT employee_id FROM freee_users limit 1",
            )
            row = cur.fetchone()

            return cls(
                employee_id=row[0],
            )

    def add(self, employee_id):
        with Cursor() as cur:
            cur.execute(
                "INSERT INTO freee_users (employee_id) VALUES (%s)",
                (employee_id,),
            )


class FreeeAccessToken:
    def __init__(self, token=None, refresh_token=None):
        self.token = token
        self.refresh_token = refresh_token

    def create_table(self):
        with Cursor() as cur:
            cur.execute(
                "CREATE TABLE freee_access_tokens (\
                        id SERIAL NOT NULL,\
                        token TEXT NOT NULL,\
                        refresh_token TEXT NOT NULL,\
                        expired_at TIMESTAMP NOT NULL,\
                        created_at TIMESTAMP DEFAULT NOW(),\
                        updated_at TIMESTAMP DEFAULT NOW(),\
                        PRIMARY KEY (id)\
                    );"
            )

    @classmethod
    def get_token(cls):
        with Cursor() as cur:
            cur.execute(
                "SELECT token FROM freee_access_tokens WHERE expired_at >= NOW() LIMIT 1",
            )
            row = cur.fetchone()
            return cls(token=row[0])

    @classmethod
    def get_refresh_token(cls):
        with Cursor() as cur:
            cur.execute(
                "SELECT refresh_token FROM freee_access_tokens LIMIT 1",
            )
            row = cur.fetchone()
            return cls(refresh_token=row[0])

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


def get_token():
    freee_access_token = FreeeAccessToken()
    try:
        row = freee_access_token.get_token()
        return row.token
    except Exception:
        row = freee_access_token.get_refresh_token()
        params = {
            "grant_type": "refresh_token",
            "refresh_token": row.refresh_token,
            "client_id": os.environ["FREEE_CLIENT_ID"],
            "client_secret": os.environ["FREEE_CLIENT_SECRET"],
            "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
        }
        # encoded_params = urllib.parse.urlencode(params)

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


def get_employee_id():
    user = FreeeUser()
    row = user.get_employee_id()
    return row.employee_id


def is_working():
    token = get_token()

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(token),
    }

    employee_id = get_employee_id()
    date = get_date()
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

    clock_in_at = datetime.datetime.strptime(j["clock_in_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
    clock_out_at = datetime.datetime.strptime(
        j["clock_out_at"], "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

    return now >= clock_in_at and now <= clock_out_at


def get_date():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    month = str(now.month).ljust(2 - len(str(now.month)), "0")
    day = str(now.day).ljust(2 - len(str(now.day)), "0")
    return "{}{}".format(month, day)
