# !usr/env/bin python3
# -*- coding: utf8 -*-

import json, re, os
from datetime import date
import requests as req

def vk_makeRequest(method, access_token, **kwargs):
    request = 'https://api.vk.com/method/%s'%method
    if kwargs:
        request += '?'
        for kwarg in kwargs:
            request += '%s=%s&'%(kwarg, kwargs[kwarg])
    request += 'access_token=%s'%access_token
    return request


def vk_callRequest(request):
    r = req.get(request)
    t = r.text
    j = json.loads(t)
    return j


def callVkApi(method, access_token, **kwargs):
    request = vk_makeRequest(method, access_token, **kwargs)
    # print(request)
    response = vk_callRequest(request)
    # print(response)
    try:
        response = response['response']
    except:
        pass
    return response


def processFile(f, access_token):
    from_spb = 0
    g = f[:-4]
    ginf = callVkApi('groups.getById', access_token, group_id=g, fields='name,members_count')
    try:
        name = ginf[0]['name']
        cnt = ginf[0]['members_count']
    except:
        name, cnt = 'could not get name', 'could not get cnt'
    print(g, name, cnt)
    males = 0
    females = 0
    sex_notdefined = 0

    age_stated = 0
    youngest = 0
    fg = 0 #15-18
    sg = 0 #18-25
    tg = 0 #25-35
    qg = 0 #older


    mistakes = 0
    f = open(f, 'r', encoding='utf8')
    for line in f:

        from_spb += 1

        try:
            line = line.replace("'", '"')
            d = json.loads(line)
        except:
            mistakes += 1
            continue

        if d['sex'] == 1:
            females += 1
        elif d['sex'] == 2:
            males += 1
        else:
            sex_notdefined += 1

        try:
            bdate = d['bdate'].split('.')
            if len(bdate) == 3:
                age_stated += 1
                byear = int(bdate[2])
                age = date.today().year - byear
                if age in range(15,19):
                    fg += 1
                elif age in range(19,26):
                    sg += 1
                elif age in range(26,35):
                    tg += 1
                elif age > 35:
                    qg += 1
                else:
                    youngest += 1
        except:
            pass



    f.close()
    print('%s mistakes'%mistakes)
    return 'http://vk.com/public%s\%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'%(g, name,cnt,from_spb,males,females,sex_notdefined,mistakes,age_stated,youngest,fg,sg,tg,qg)

def main(access_token):
    result = open('meta.txt', 'w', encoding='utf8')
    result.write('link\tname\tusers\tfrom_spb\tboys\tgirls\tsexnotstated\tmistakes\tage_stated\tyoungest\t15-18\t19-25\t25-35\t35+\n')
    for f in os.listdir(os.getcwd()):
        if os.path.splitext(f)[-1] == '.txt':
            meta = processFile(f, access_token)
            result.write(meta + '\n')
    

if __name__ == '__main__':
    access_token = 'a892b0f1a6e8a8992e32c67a4d137996095c26329d474e0f5b549f05d245026fd1d36cbf28e0b4adaced4'
    main(access_token)
    