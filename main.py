# version 2.0: fix the newest encrypt of tju. :D
from image_base import get_headersDict, Proxy_pool
import re
import os
from time import sleep, time
from Crypto.Cipher import AES
from json import dumps
import base64

headers = {}
cookies = {}
proxy_pool = None
KEY = 'xiaofaai@act_id!'.encode('utf-8')
IV = 'tongjixf@act_id!'.encode('utf-8')

def getDict(text, patten, patten2, stri_patten = ''):
    lis = text.split(patten)
    cookieDict = {}
    for str in lis:
        cookie = str.strip().split(stri_patten + patten2)
        cookieDict[cookie[0].strip(stri_patten)] = cookie[1].strip(stri_patten)
    return cookieDict

def get_classList(type): # 2 有余位；3 已报满；7 未开始
    d = 'page=1&seltype=&level=1'
    data = getDict(d, '&', '=')
    data['selstatus'] = type
    url = 'http://yjsqd.tongji.edu.cn/Pc/getActivityList.json'
    num = 1
    speech_dict_list = []
    while True:
        data['page'] = num
        t = proxy_pool.post_HTMLText(url, headers = headers, cookies = cookies, data = data).replace('\/', '/')
        text = t.encode('utf-8').decode('unicode_escape')
        if '"data":null' in text:
            break
        tmp_lis = format_class(text)
        speech_dict_list.extend(tmp_lis)
        num += 1
    for each in speech_dict_list:
        print(each['activity_name'])
    return speech_dict_list

def format_class(text):
    f = re.search('\[[\s\S]+?\]',text).group(0).strip('[]')
    lis = f.split('},')
    dict_lis = []
    for i in lis:
        tmp = i.strip('{}')
        dic = getDict(tmp, ',', ':', '"')
        if '请勿报名' in dic['activity_name']:
            continue
        dict_lis.append(dic)
    return dict_lis

def single_speech(s_id):
    sleep(1)
    url = 'http://yjsqd.tongji.edu.cn/Swoole/' #result.json push.json
    data2 = {'act_id':s_id}
    q_url = url + 'push.json'
    r_url = url + 'result.json'
    act_str = {'act_id' : s_id, 'buy_ticket_type' : "PC", 'time' : None}
    while True:
        second = int(time())
        headers2 = {'Token':encrypt('"' + str(second) + '@tj"')}
        act_str['time'] = second
        json = dumps(act_str).replace(' ', '')
        data = {'act_str': encrypt(json)}
        q_text = proxy_pool.post_HTMLText(q_url, headers2, cookies, data).encode('utf-8').decode('unicode_escape')
        if '排队' in q_text:
            break
        sleep(1)
    while True:
        text = proxy_pool.post_HTMLText(r_url, headers, cookies, data2).encode('utf-8').decode('unicode_escape')
        if not '排队' in text:
            print(text)
            break
        sleep(1)
    if '相同时间' in text:
        return True
    else:
        return False

            

def get_speech(mode = ''):
    file_path = os.path.join('speech.txt')
    speech_dict_list = []
    if not os.path.exists(file_path) or mode == 'new':
        speech_dict_list = get_classList(2) + get_classList(3) + get_classList(7)
        with open(file_path, 'w', encoding = 'utf-8') as f:
            for each in speech_dict_list:
                tmp_str = (each['activity_name'] + ' $ ' + each['activity_id'] + ' $ ' + each['activity_start_time']
                            + ' $ ' + each['activity_end_time'] + ' $ ' + each['activity_status'])
                f.write(tmp_str + '\n')
    elif os.path.exists(file_path):
        with open(file_path, 'r', encoding = 'utf-8') as f:
            for line in f:
                dic = {}
                lis = line.split(' $ ')
                dic['activity_name'] = lis[0]
                dic['activity_id'] = lis[1]
                dic['activity_start_time'] = lis[2]
                dic['activity_end_time'] = lis[3]
                dic['activity_status'] = lis[4]
                speech_dict_list.append(dic)
    if speech_dict_list:
        return speech_dict_list

def get_queue(lis):
    t_q = Queue()
    for i in lis:
        print(i['activity_name'])
        t_q.put((i['activity_name'], i['activity_id']))
    if t_q:
        return t_q

def decrypt(text):
    b = base64.b64decode(text.encode())
    c = base64.b64decode(b)
    cryptor = AES.new(KEY, AES.MODE_CBC, IV)
    d = cryptor.decrypt(c)
    d = d.rstrip(b'\0')
    e = base64.b64decode(d)
    return e.decode()

def encrypt(text): # nopadding
    b = base64.b64encode(text.encode())
    add = len(b) % 16
    b = b + (add and (16 - add) or 0) * b'\0'
    cryptor = AES.new(KEY, AES.MODE_CBC, IV)
    c = cryptor.encrypt(b)
    d = base64.b64encode(c)
    e = base64.b64encode(d)
    return e.decode()

def main():
    global headers, cookies, proxy_pool
    h = '''
   Host: yjsqd.tongji.edu.cn
Connection: keep-alive
Content-Length: 23
Accept: application/json, text/plain, */*
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36
Content-Type: application/x-www-form-urlencoded;charset=UTF-8
Origin: http://yjsqd.tongji.edu.cn
Referer: http://yjsqd.tongji.edu.cn/PC/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
'''
    c = 'PHPSESSID=9nrh422ga8turssvcg0u39qfjb; think_language=zh-CN; pwapp_unbs=10191911; pwapp_ext_sid=2030563; pwapp_uname=%E4%BD%95%E6%8B%93; tokens=6648d26956bf5d6b8139ef4f901e3fec; connection_id=a527a5c3063ae6f1749bb0527f2d1819; YXMC=%E7%8E%AF%E5%A2%83%E7%A7%91%E5%AD%A6%E4%B8%8E%E5%B7%A5%E7%A8%8B%E5%AD%A6%E9%99%A2; IS_YXMC=10191911'
    headers = get_headersDict(h)
    cookies = getDict(c, ';', '=')
    proxy_pool = Proxy_pool()
    lis = get_speech()
    lenth = len(lis)
    print('读取课程列表成功！')

    while True:
        for i in lis:
            s_name = i['activity_name']
            s_id = i['activity_id']
            s_time = i['activity_start_time']
            print('正在选课：{}'.format(s_name))
            if single_speech(s_id):
                lis.remove(i)
            

if __name__ == '__main__':
    main()