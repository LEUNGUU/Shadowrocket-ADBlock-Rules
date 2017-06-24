# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import threading
import time
import sys
import requests


urls = ['http://alexa.chinaz.com/Global/index.html']
for i in range(2,21):
    urls.append('http://alexa.chinaz.com/Global/index_%d.html'%i)

urls_scan_over = False

domains = []


# thread to scan pages in urls
class UrlScaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global urls_scan_over, urls

        done_num = 0

        while len(urls):
            html = self.fetchHTML( urls.pop(0) )
            self.praseHTML(html)

            done_num = done_num + 25
            print('top500 已获取：%d/500'%done_num)

            time.sleep(1)

        urls_scan_over = True
        print('top500 网站获取完毕。')


    def fetchHTML(self, url):
        success = False
        try_times = 0
        while try_times < 5 and not success:
            r = requests.get(url)
            if r.status_code != 200:
                time.sleep(1)
                try_times = try_times + 1
            else:
                success = True
                break

        if not success:
            sys.exit('error in request %s\n\treturn code: %d' % (url, r.status_code) )

        r.encoding = 'utf-8'
        return r.text


    def praseHTML(self, html):
        soup = BeautifulSoup(html, "lxml")
        namesDom = soup.select("div.righttxt h3 span")

        for name in namesDom:
            domains.append(name.string)


requests_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Cache-Control': 'max-age=0',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-HK;q=0.6,zh-TW;q=0.4,en;q=0.2',
    'Connection': 'keep-alive'
}


# thread to visit websites
class DomainScaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while not urls_scan_over or len(domains):
            if len(domains) == 0:
                time.sleep(2)
                continue

            domain = domains.pop(0)

            if domain.endswith('.cn'):
                continue
            if 'google' in domain:
                continue

            is_proxy = False

            try:
                requests.get('http://' + domain, timeout=10, headers=requests_header)
            except BaseException:
                try:
                    requests.get('http://www.' + domain, timeout=10, headers=requests_header)
                except BaseException:
                    is_proxy = True

            if is_proxy:
                file_proxy.write(domain + '\n')
            else:
                file_direct.write(domain + '\n')

            print('[剩余域名数量：%d]\tProxy %s：%s' % (len(domains), is_proxy, domain) )


print('5s later to start refresh top500 lists...')
time.sleep(5)

# output files
file_proxy = open('resultant/top500_proxy.list', 'w', encoding='utf-8')
file_direct = open('resultant/top500_direct.list', 'w', encoding='utf-8')

now_time = time.strftime("%Y-%m-%d %H:%M:%S")
file_proxy.write('# top500 proxy list update time: ' + now_time + '\n')
file_direct.write('# top500 direct list update time: ' + now_time + '\n')

# Start Thread
UrlScaner().start()
for i in range(5):
    DomainScaner().start()
