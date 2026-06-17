import requests
from bs4 import BeautifulSoup

import app.utils as web_utils
from app.account.account import Account
from exception import WebException
from stats import *

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

    account.to_pkl()
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
            Cookie: {sso_jsessionid}""")
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

    account.to_pkl()
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
    account['kbList'] = json['kbList']

    account.to_pkl()
    return True

if __name__ == '__main__':
    ac: Account = Account.from_file('my_account.json')
    print('\n', ac.studentId, ac.password)

    # TODO
    # isAble: bool
    # isAble = OAuthCasLogin(ac)
    # isAble = GDJWLogin(ac) if isAble else False
    # isAble = getCourseTable(ac) if isAble else False