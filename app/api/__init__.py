import requests
from bs4 import BeautifulSoup

import app.utils as web_utils
from app.account.account import Account

class WebException(Exception):
    def __init__(self, code):
        self.code = code

ZJUTHost = 'oauth.zjut.edu.cn'
GDJWHost = 'www.gdjw.zjut.edu.cn'
GDJWFixHost = 'www.gdjwjf.zjut.edu.cn'

login_url = f'https://{ZJUTHost}/cas/login'
publicKey_url = f'https://{ZJUTHost}/cas/v2/getPubKey'

OAuthCasHeader = """
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
        Accept-Encoding: gzip, deflate, br, zstd
        Accept-Language: zh-CN,zh;q=0.9
        Cache-Control: max-age=0
        Connection: keep-alive
        Sec-Fetch-Dest: document
        Sec-Fetch-Mode: navigate
        Sec-Fetch-Site: none
        Sec-Fetch-User: ?1
        Upgrade-Insecure-Requests: 1
"""
PublicKeyHeader = """
        Accept: application/json, text/javascript, */*; q=0.01
        Accept-Encoding: gzip, deflate, br, zstd
        Accept-Language: zh-CN,zh;q=0.9 
        Connection: keep-alive
        Sec-Fetch-Dest: empty
        Sec-Fetch-Mode: cors
        Sec-Fetch-Site: same-origin
        X-Requested-With: XMLHttpRequest
        """
OAuthCasLoginHeader = """
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
        Accept-Encoding: gzip, deflate, br, zstd
        Accept-Language: zh-CN,zh;q=0.9
        Cache-Control: max-age=0
        Connection: keep-alive
        Content-Type: application/x-www-form-urlencoded
        Origin: https://oauth.zjut.edu.cn
        Sec-Fetch-Dest: document
        Sec-Fetch-Mode: navigate
        Sec-Fetch-Site: same-origin
        Sec-Fetch-User: ?1
        Upgrade-Insecure-Requests: 1
        """

GDJWBaseHeader = """
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
        Cache-Control: max-age=0
        Connection: keep-alive
        Upgrade-Insecure-Requests: 1
        """
GDJWContentCourseBaseHeader = """
        Accept: */*
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
        Connection: keep-alive
        Content-Type: application/x-www-form-urlencoded;charset=UTF-8
        X-Requested-With: XMLHttpRequest
        """

def OAuthCasLogin(account: Account, host: str = GDJWHost) -> bool:
    url = f'{login_url}?service=http%3A%2F%2F{host}%2Fsso%2Fzfiotlogin'

    response = requests.get(url,headers=web_utils.parseRawHeader(OAuthCasHeader))
    if response.status_code != 200: return False

    cas_jsessionid = response.cookies.get('JSESSIONID')

    soup = BeautifulSoup(response.content, 'html.parser')
    inputElement = soup.select_one('#fm1 > input[type=hidden]:nth-child(6)')
    execution: str = inputElement.attrs.get('value')

    response = requests.get(
        publicKey_url,
        headers=web_utils.parseRawHeader(f'''
            {PublicKeyHeader}
            Host: {ZJUTHost}
            Referer: {url}
            Cookie: JSESSIONID={cas_jsessionid}''')
    )
    if response.status_code != 200: return False

    base_pv0 = response.cookies.get('_pv0')

    json = response.json()
    modulus = json['modulus']
    exponent = json['exponent']

    response = requests.post(
        url,
        allow_redirects=False,
        data={
            'username': account.studentId,
            'mobileCode': '',
            'password': account.crypto(exponent, modulus),
            'authcode': '',
            'execution': execution,
            '_eventId': 'submit',
        },
        headers=web_utils.parseRawHeader(f'''
            {OAuthCasLoginHeader}
            Referer: {url}
            Cookie: JSESSIONID={cas_jsessionid}; _pv0={base_pv0}''')
    )
    if response.status_code != 302: return False
    zfiotlogin_ticket_location = response.headers['Location']
    account['zfiotlogin_ticket_location'] = zfiotlogin_ticket_location

    account.to_json()
    return True

def GDJWLogin(account: Account, host: str = GDJWHost) -> bool:
    response = requests.get(
        account['zfiotlogin_ticket_location'],
        allow_redirects=False,
        headers=web_utils.parseRawHeader(f"""
        {GDJWBaseHeader}""")
    )
    if response.status_code != 302: return False
    zfiotlogin_base_location = response.headers['Location']
    if zfiotlogin_base_location is None: raise Exception()
    sso_jsessionid = response.cookies.get('JSESSIONID')

    response = requests.get(
        zfiotlogin_base_location,
        allow_redirects=False,
        headers=web_utils.parseRawHeader(f"""
            {GDJWBaseHeader}
            Cookie: JSESSIONID={sso_jsessionid}""")
    )
    if response.status_code != 302: return False
    ticket_login_location = response.headers['Location']

    response = requests.get(
        ticket_login_location,
        allow_redirects=False,
        headers=web_utils.parseRawHeader(f"""
            {GDJWBaseHeader}""")
    )
    if response.status_code != 302: return False
    jwglxt_jsessionid = response.cookies.get('JSESSIONID')
    base_route = response.cookies.get('route')
    account['jwglxt_jsessionid'] = jwglxt_jsessionid
    account['base_route'] = base_route

    response = requests.get(
        f'http://{host}/jwglxt/xtgl/login_slogin.html',
        allow_redirects=False,
        headers=web_utils.parseRawHeader(f"""
            {GDJWBaseHeader}
            Cookie: JSESSIONID={jwglxt_jsessionid}; route={base_route}""")
    )
    if response.status_code != 302: return False
    index_initMenu_location = response.headers['Location']
    account['index_initMenu_location'] = index_initMenu_location

    account.to_json()
    return True

def getCourseTable(account: Account, host: str = GDJWHost) -> bool:
    xnm = account['acYear']
    xqm: str = ''
    match account['acTerm']:
        case '1': xqm = '3'
        case '2': xqm = '12'
        case '3': xqm = '16'
    if not xqm: return False

    response = requests.post(
        f'http://{host}/jwglxt/kbcx/xskbcx_cxXsgrkb.html?gnmkdm=N253508',
        allow_redirects=False,
        headers=web_utils.parseRawHeader(f"""
            {GDJWContentCourseBaseHeader}
            Origin: http://{host}
            Referer: http://{host}/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N253508&layout=default
            Cookie: JSESSIONID={account['jwglxt_jsessionid']}; route={account['base_route']}"""),
        data={
            'xnm': xnm,
            'xqm': xqm,
            'kzlx': 'ck',
            'xsdm': '',
            'kclbdm': ''
        }
    )
    json = response.json()
    account['course_inf'] = json

    account.to_json()
    return True

def run(account: Account, host: str = GDJWHost) -> bool:
    able: bool
    able = OAuthCasLogin(ac)
    able = GDJWLogin(ac) if able else False
    able = getCourseTable(ac) if able else False
    return able

if __name__ == '__main__':
    ac: Account = Account.from_file('my_account.json')
    ac['acYear'] = '2025'
    ac['acTerm'] = '1'
    print('\n', ac.studentId, ac.password)

    isAble: bool
    isAble = OAuthCasLogin(ac)
    isAble = GDJWLogin(ac) if isAble else False
    isAble = getCourseTable(ac) if isAble else False