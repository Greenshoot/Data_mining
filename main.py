# -*- coding: utf-8 -*-
"""

"""

# 目标爬取店铺的评论

import requests
from bs4 import BeautifulSoup
import time, random
import mysqls
import re
from fake_useragent import UserAgent
import os

ua = UserAgent()

# 设置cookies
cookie = "_lxsdk_cuid=16994cd3090c8-0512967d8a87ce-57b153d-100200-16994cd309021; _lxsdk=16994cd3090c8-0512967d8a87ce-57b153d-100200-16994cd309021; _hc.v=00b5e701-a43a-7a3d-1e3a-88b7a2c3e1f5.1552979669; _dp.ac.v=14ed9cbb-58cf-4142-872d-81306cf1edcf; ua=dpuser_7129941458; ctu=d82ecef6e4eb821d82c5645cae0c68cc097946494f708a842956b830c6a317ab; s_ViewType=10; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; lgtoken=02a547f11-cf06-4d4f-8b75-6a2515a333d9; dper=1d2044754caea8674acf61379d3955db5ea31b3247fe2d43ed9a2fc69c51eb996daf55cc2933aa352c4dd47164452f16c7dfb68af25968316efffcc0ab341103920a446f813b98579de17068720621d741fc64a355de4360c55a53ce018c34d2; ll=7fd06e815b796be3df069dec7836c3df; uamo=13397503836; dplet=a9f7c747df2d1e8db765e301d31aa7ab; cy=2; cye=beijing; _lxsdk_s=170d9bd3e7c-7a2-278-335%7C%7C119"

# 修改请求头
headers = {
    'User-Agent': ua.random,
    'Cookie': cookie,
    'Connection': 'keep-alive',
    'Host': 'www.dianping.com',
    'Referer': 'http://www.dianping.com/shop/521698/review_all/p6'
}


# 从ip代理池中随机获取ip
# ips = open('proxies.txt','r').read().split('\n')
#
# def get_random_ip():
#    ip = random.choice(ips)
#    pxs = {ip.split(':')[0]:ip}
#    return pxs

# 获取html页面
def getHTMLText(url, code="utf-8"):
    try:
        time.sleep(random.random() * 6 + 2)
        r = requests.get(url, timeout=5, headers=headers,
                         #                       proxies=get_random_ip()
                         )
        r.raise_for_status()
        r.encoding = code
        return r.text
    except:
        print("产生异常")
        return "产生异常"


# 因为评论中带有emoji表情，是4个字符长度的，mysql数据库不支持4个字符长度，因此要进行过滤
def remove_emoji(text):
    try:
        highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return highpoints.sub(u'', text)


# 从html中提起所需字段信息
def parsePage(html, shpoID):
    infoList = []  # 用于存储提取后的信息，列表的每一项都是一个字典
    soup = BeautifulSoup(html, "html.parser")

    for item in soup('div', 'main-review'):
        cus_id = item.find('a', 'name').text.strip()
        comment_time = item.find('span', 'time').text.strip()
        try:
            comment_star = item.find('span', re.compile('sml-rank-stars')).get('class')[1]
        except:
            comment_star = 'NAN'
        cus_comment = item.find('div', "review-words").text.strip()
        scores = str(item.find('span', 'score'))
        try:
            kouwei = re.findall(r'口味：([\u4e00-\u9fa5]*)', scores)[0]
            huanjing = re.findall(r'环境：([\u4e00-\u9fa5]*)', scores)[0]
            fuwu = re.findall(r'服务：([\u4e00-\u9fa5]*)', scores)[0]
        except:
            kouwei = huanjing = fuwu = '无'

        infoList.append({'cus_id': cus_id,
                         'comment_time': comment_time,
                         'comment_star': comment_star,
                         'cus_comment': remove_emoji(cus_comment),
                         'kouwei': kouwei,
                         'huanjing': huanjing,
                         'fuwu': fuwu,
                         'shopID': shpoID})
    return infoList


# 构造每一页的url，并且对爬取的信息进行存储
def getCommentinfo(shop_url, shpoID, page_begin, page_end):
    for i in range(page_begin, page_end):
        try:
            url = shop_url + 'p' + str(i)
            html = getHTMLText(url)
            infoList = parsePage(html, shpoID)
            print('成功爬取第{}页数据,有评论{}条'.format(i, len(infoList)))
            for info in infoList:
                mysqls.save_data(info)
            # 断点续传中的断点
            if (html != "产生异常") and (len(infoList) != 0):
                with open('xuchuan.txt', 'a') as file:
                    duandian = str(i) + '\n'
                    file.write(duandian)
            else:
                print('休息60s...')
                time.sleep(60)
        except:
            print('跳过本次')
            continue
    return


def xuchuan():
    if os.path.exists('xuchuan.txt'):
        file = open('xuchuan.txt', 'r')
        nowpage = int(file.readlines()[-1])
        file.close()
    else:
        nowpage = 0
    return nowpage


# 根据店铺id，店铺页码进行爬取
def craw_comment(shopID='521698', page=10):
    shop_url = "http://www.dianping.com/shop/" + shopID + "/review_all/"
    # 读取断点续传中的续传断点
    nowpage = xuchuan()
    getCommentinfo(shop_url, shopID, page_begin=nowpage + 1, page_end=page + 1)
    mysqls.close_sql()
    return


if __name__ == "__main__":
    craw_comment()
