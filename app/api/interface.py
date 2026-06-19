import json
import os
import requests
from bs4 import BeautifulSoup

from app.api.headers import *
from app.settings import get as get_settings
from app.utils import encrypt_password, parseRawHeader, project_root

class ApiError(Exception):
    pass

CACHE_PATH = os.path.join(project_root, "app", "store", "cache.json")

def load_cache() -> tuple[bool, dict]:
    if not os.path.exists(CACHE_PATH):
        return False, {}

    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False, {}

    if "course_inf" not in cache:
        return False, {}

    return True, cache


def save_cache(cache: dict):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def _oauth_cas_login(cache: dict, host: str = GDJWHost):
    s = get_settings()
    url = f"{login_url}?service=http%3A%2F%2F{host}%2Fsso%2Fzfiotlogin"

    response = requests.get(url, headers=parseRawHeader(OAuthCasHeader))
    if response.status_code != 200:
        raise ApiError(f"CAS 登录页面请求失败，状态码 {response.status_code}")

    cas_jsessionid = response.cookies.get("JSESSIONID")

    soup = BeautifulSoup(response.content, "html.parser")
    inputElement = soup.select_one("#fm1 > input[type=hidden]:nth-child(6)")
    execution: str = inputElement.attrs.get("value")

    response = requests.get(
        publicKey_url,
        headers=parseRawHeader(
            f"""
            {PublicKeyHeader}
            Host: {ZJUTHost}
            Referer: {url}
            Cookie: JSESSIONID={cas_jsessionid}"""
        ),
    )
    if response.status_code != 200:
        raise ApiError(f"获取加密公钥失败，状态码 {response.status_code}")

    base_pv0 = response.cookies.get("_pv0")

    json_data = response.json()
    modulus = json_data["modulus"]
    exponent = json_data["exponent"]

    response = requests.post(
        url,
        allow_redirects=False,
        data={
            "username": s.value("studentId"),
            "mobileCode": "",
            "password": encrypt_password(s.value("password"), exponent, modulus),
            "authcode": "",
            "execution": execution,
            "_eventId": "submit",
        },
        headers=parseRawHeader(
            f"""
            {OAuthCasLoginHeader}
            Referer: {url}
            Cookie: JSESSIONID={cas_jsessionid}; _pv0={base_pv0}"""
        ),
    )

    if response.status_code != 302:
        raise ApiError(f"CAS 登录失败，状态码 {response.status_code}（请检查学号和密码）")

    zfiotlogin_ticket_location = response.headers["Location"]
    cache["zfiotlogin_ticket_location"] = zfiotlogin_ticket_location


def _gdjw_login(cache: dict, host: str = GDJWHost):
    response = requests.get(
        cache["zfiotlogin_ticket_location"],
        allow_redirects=False,
        headers=parseRawHeader(GDJWBaseHeader),
    )
    if response.status_code != 302:
        raise ApiError(f"教务系统单点登录失败，状态码 {response.status_code}")

    zfiotlogin_base_location = response.headers["Location"]
    if zfiotlogin_base_location is None:
        raise ApiError("教务系统未返回重定向地址")

    sso_jsessionid = response.cookies.get("JSESSIONID")

    response = requests.get(
        zfiotlogin_base_location,
        allow_redirects=False,
        headers=parseRawHeader(
            f"""
            {GDJWBaseHeader}
            Cookie: JSESSIONID={sso_jsessionid}"""
        ),
    )
    if response.status_code != 302:
        raise ApiError(f"教务系统登录验证失败，状态码 {response.status_code}")

    ticket_login_location = response.headers["Location"]

    response = requests.get(
        ticket_login_location,
        allow_redirects=False,
        headers=parseRawHeader(GDJWBaseHeader),
    )
    if response.status_code != 302:
        raise ApiError(f"教务系统会话建立失败，状态码 {response.status_code}")

    jwglxt_jsessionid = response.cookies.get("JSESSIONID")
    base_route = response.cookies.get("route")
    cache["jwglxt_jsessionid"] = jwglxt_jsessionid
    cache["base_route"] = base_route

    response = requests.get(
        f"http://{host}/jwglxt/xtgl/login_slogin.html",
        allow_redirects=False,
        headers=parseRawHeader(
            f"""
            {GDJWBaseHeader}
            Cookie: JSESSIONID={jwglxt_jsessionid}; route={base_route}"""
        ),
    )
    if response.status_code != 302:
        raise ApiError(f"教务系统初始化失败，状态码 {response.status_code}")

    index_initMenu_location = response.headers["Location"]
    cache["index_initMenu_location"] = index_initMenu_location


def _resolve_semester() -> tuple[str, str]:
    s = get_settings()
    xnm = s.value("acYear")
    xqm = {"1": "3", "2": "12", "3": "16"}.get(s.value("acTerm"), "")
    if not xnm or not xqm:
        raise ApiError("未设置学年或学期")
    return xnm, xqm


def _get_course_table(cache: dict, host: str = GDJWHost):
    xnm, xqm = _resolve_semester()

    response = requests.post(
        f"http://{host}/jwglxt/kbcx/xskbcx_cxXsgrkb.html?gnmkdm=N253508",
        allow_redirects=False,
        headers=parseRawHeader(
            f"""
            {GDJWContentCourseBaseHeader}
            Origin: http://{host}
            Referer: http://{host}/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N253508&layout=default
            Cookie: JSESSIONID={cache['jwglxt_jsessionid']}; route={cache['base_route']}"""
        ),
        data={"xnm": xnm, "xqm": xqm, "kzlx": "ck", "xsdm": "", "kclbdm": ""},
    )
    json_data = response.json()
    cache["course_inf"] = json_data


def _get_course_first_date(cache: dict, host: str = GDJWHost):
    xnm, xqm = _resolve_semester()

    response = requests.post(
        f"http://{host}/jwglxt/kbcx/xskbcxMobile_cxXsgrkb.html",
        headers=parseRawHeader(
            f"""
            {GDJWContentCourseBaseHeader}
            Origin: http://{host}
            Referer: http://{host}/jwglxt/kbcx/xskbcxMobile_cxTimeTableIndex.html?gnmkdm=Y253511
            Cookie: JSESSIONID={cache['jwglxt_jsessionid']}; route={cache['base_route']}"""
        ),
        data={"xnm": xnm, "xqm": xqm, "zs": "1", "kblx": "1", "doType": "app"},
    )
    json_data = response.json()
    try:
        first_date = json_data["rqazcList"][0]["rq"]
        cache["first_date"] = first_date
    except (KeyError, IndexError):
        raise ApiError("获取学期首日失败，教务系统返回数据异常")


def run():
    cache: dict = {}

    _oauth_cas_login(cache)
    _gdjw_login(cache)
    _get_course_table(cache)
    _get_course_first_date(cache)

    save_cache(cache)


async def run_async() -> tuple[bool, Exception | None]:
    import asyncio
    import traceback
    try:
        await asyncio.to_thread(run)
        return True, None
    except Exception as e:
        e.traceback_str = traceback.format_exc()
        return False, e
