import requests
import re
import random
from time import sleep
import threading

def get_headersDict(text):
    text = text.strip().split('\n')
    headers = {x.split(':', 1)[0].strip(): x.split(':', 1)[1].strip() for x in text}
    return headers

def getDict(text, patten, patten2, stri_patten = ''):
    lis = text.split(patten)
    cookieDict = {}
    for str in lis:
        cookie = str.strip().split(patten2)
        cookieDict[cookie[0].strip(stri_patten)] = cookie[1].strip(stri_patten)
    return cookieDict

def getHTMLText(url, headers = {}, param = {}):
    try_time = 0
    while try_time < 5:
        try:
            r=requests.get(url, headers = headers, params = param, timeout = 20)
            r.raise_for_status()
            r.encoding=r.apparent_encoding
            return r.text
        except:
            try_time += 1

def get_image_content(url, headers):
    try_time = 0
    while try_time < 5:
        try:
            r = requests.get(url, headers = headers)
            r.raise_for_status()
            return r.content
        except:
            try_time += 1

class Proxy_pool(object):
    def __init__(self):
        self.proxylist = []
        self.lock = False
        self.page = 1
        self.enable_proxy = True
        self.tsk = threading.Thread(target = self.run)
        self.tsk.setDaemon(True)
        self.tsk.start()
    
    def kuai(self):
        url = 'https://www.kuaidaili.com/free/inha/' + str(self.page) + '/'
        text = getHTMLText(url)
        rawlist = re.findall('<td data-title="IP"[\s\S]+?最后验证时间', text)
        for raw in rawlist:
            lis = re.sub('<[\s\S]+?>', '', raw).split('\n')
            ip = lis[0].strip()
            port = lis[1].strip()
            type = lis[3].strip().lower()
            fake = lis[2].strip()
            if '高匿' in fake:
                proxy = {type: type + '://' + ip + ':' + port}
                test = requests.get('https://www.baidu.com', proxies = proxy)
                if test.status_code == 200 and not proxy in self.proxylist:
                    self.lock = True
                    self.proxylist.append(proxy)
                    self.lock = False
    
    def free(self):
        url = 'https://ip.jiangxianli.com/?page={}&country=中国'.format(self.page)
        text = getHTMLText(url)
        rawlist = re.findall('<tr>[\s\S]+?</tr>', text)[1:]
        for raw in rawlist:
            lis = re.findall('<td>[\s\S]+?</td>', raw)
            ip = lis[0].strip('<>td/')
            port = lis[1].strip('<>td/')
            type = lis[3].strip('<>td/').lower()
            fake = lis[2].strip('<>td/')
            if '高匿' in fake:
                proxy = {type: type + '://' + ip + ':' + port}
                test = requests.get('https://www.baidu.com', proxies = proxy)
                if test.status_code == 200 and not proxy in self.proxylist:
                    self.lock = True
                    self.proxylist.append(proxy)
                    self.lock = False

    def run(self):
        while True:
            self.free()
            self.kuai()
            self.page += 1
            sleep(2)
    
    def get_proxy(self):
        while True:
            if self.enable_proxy:
                if not self.lock and self.proxylist:
                    return random.choice(self.proxylist)
            else:
                return {}
    
    def get_HTMLText(self, url, headers = {}, param = {}):
        try_time = 0
        while True:
            try:
                proxy = self.get_proxy()
                r=requests.get(url, headers = headers, params = param, proxies = proxy)
                r.raise_for_status()
                r.encoding=r.apparent_encoding
                return r.text
            except:
                try_time += 1

    def get_content(self, url, headers = {}):
        try_time = 0
        while True:
            try:
                proxy = self.get_proxy()
                r = requests.get(url, headers = headers, proxies = proxy)
                r.raise_for_status()
                return r.content
            except:
                try_time += 1
    
    def post_content(self, url, headers = {}, data = {}):
        try_time = 0
        while True:
            try:
                proxy = self.get_proxy()
                r = requests.post(url, data = data, headers = headers, proxies = proxy)
                r.raise_for_status()
                return r.content
            except:
                try_time += 1

    def post_HTMLText(self, url, headers = {}, cookies = {}, data = {}, encoding = {}):
        while True:
            try:
                # proxy = self.get_proxy()
                r = requests.post(url, data = data, headers = headers, cookies = cookies, timeout = 10)
                r.raise_for_status()
                if encoding:
                    r.encoding = encoding
                else:
                    r.encoding = r.apparent_encoding
                return r.text
            except:
                pass