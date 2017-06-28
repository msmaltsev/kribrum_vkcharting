# !usr/env/bin python3
# -*- coding: utf8 -*-

import datetime, time, json, sys
import requests as req


def writeFile(data, f='groupMembers.json'):
    try:
        print('trying to write into existing file')
        a = open(f, 'a', encoding='utf8')
        print('success')
    except:
        print('making new result file: %s'%f)
        a = open(f, 'w', encoding='utf8')
    print(data, file=a)
    a.close()


def loadVkCode(f):
    code = open(f, encoding='utf8').read()
    code = code.replace('+', '%20%2B')
    return code


def collectFromList(list_of_lists):
    ## берет на вход список списков
    ## возвращает сумму этих списков
    result = []
    for i in list_of_lists:
        if type(i) == list:
            result += collectFromList(i)
        else:
            result.append(i)
    return result


def vk_makeRequest(method, access_token, **kwargs):
    request = 'https://api.vk.com/method/%s'%method
    if kwargs:
        request += '?'
        for kwarg in kwargs:
            request += '%s=%s&'%(kwarg, kwargs[kwarg])
    request += 'access_token=%s'%access_token
    return request


def vk_callRequest(request):
    j = None
    while not j:
        try:
            r = req.get(request)
            t = r.text
            j = json.loads(t)
        except Exception as e:
            print('vk cll failed: %s'%e)
            continue
    return j


def getMembersFromReq(req):
    res = [req[0], []]
    for i in req[1]:
        res[1] += i['users']
    return res


def callVkApi(method, access_token, extra_process=True, **kwargs):
    request = vk_makeRequest(method, access_token, **kwargs)
    response = vk_callRequest(request)
    try:
        response = response['response']
    except:
        pass
    return response


def getGroupUsers(groupid, access_token):
    print('collecting users from http://vk.com/public%s'%groupid)
    fres = open('%s.txt'%groupid, 'w', encoding='utf8')
    members_gl = []
    members_spb_cnt = 0
    offset = 0 
    g = callVkApi('groups.getMembers', access_token, group_id=groupid,offset=offset)
    g = g['count']
    print('users to collect: %s'%g)
    strt = datetime.datetime.now()
    est = datetime.timedelta(seconds = 0.3333333) * g/25000 * 11/5
    if g == 0:
        print('api method returned no users. perhaps group is blocked')
        return []
    else:
        print('estimated time: %s'%est)
        while offset < g + 25000:
            code = loadVkCode('getAllUsersFromOneGroup.vkcode')
            code = code%(offset, groupid)
            returned = callVkApi('execute', access_token, code='%s'%code)
            try:
                offset_ = returned[0]
                members = returned[1]
                members = [i['users'] for i in members if i['users'] != []]
                members = collectFromList(members)
                members_spb = [i for i in members if 'city' in i.keys() and i['city'] == 2]
                members_spb_cnt += len(members_spb)
                members_gl += members
                for i in members_spb:
                    fres.write(repr(i) + '\n')
                offset = offset_
                time.sleep(0.3333333)
                users_all = len(collectFromList(members_gl))
                spb_perc = members_spb_cnt/users_all*100
                sys.stdout.write('\rcollected %s users out of %s; %s (%s%%) from spb'%(users_all, g, members_spb_cnt, round(spb_perc, 2)))
                sys.stdout.flush()
                
            except Exception as e:
                print(e)
                # print(returned)
                offset = offset
                continue
        fres.close()
        fnsh = datetime.datetime.now()
        # print('\n%s users from spb'%members_spb_cnt)
        print('spent time: %s'%(fnsh-strt))
        # return collectFromList(members_gl)


def main(access_token, groups_list_file):
    groups = open(groups_list_file, encoding='utf8').read().split('\n')
    g = [int(i.replace('https://vk.com/public', ''))  for i in groups]
    result = {}
    for group in g:
        u = getGroupUsers(group, access_token)
        # writeFile('{"group_id":%s, "count":%s, "users":%s}'%(group, len(u), u), f='%s.json'%group)
        print('')
    

if __name__ == '__main__':
    access_token = 'a892b0f1a6e8a8992e32c67a4d137996095c26329d474e0f5b549f05d245026fd1d36cbf28e0b4adaced4'
    main(access_token, 'spbgroups.txt')

