ZJUTHost = 'oauth.zjut.edu.cn'
GDJWHost = 'www.gdjw.zjut.edu.cn'

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
GDJWExamQueryHeader = """
        Accept: application/json, text/javascript, */*; q=0.01
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
        Connection: keep-alive
        Content-Type: application/x-www-form-urlencoded;charset=UTF-8
        """
GDJWGradeQueryHeader = """
        Accept: application/json, text/javascript, */*; q=0.01
        Accept-Encoding: gzip, deflate
        Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
        Connection: keep-alive
        Content-Type: application/x-www-form-urlencoded;charset=UTF-8
        X-Requested-With: XMLHttpRequest
        """