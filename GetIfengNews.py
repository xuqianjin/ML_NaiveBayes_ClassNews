# coding:utf-8
import requests
import json
import pymongo
import time

page = 20  # 每项数据抓取页数
sleeptime = 0.2  # 每页抓取间隔时间


def getMap():
    map = {'娱乐': 1, '社会': 2, '体育': 3, '科技': 4, '军事': 5, '历史': 6, '财经': 7}
    return map


def getProject():
    title = {'社会': 'http://i.ifeng.com/idyn/inews/0/7720/_pagekey/10/data.shtml',
             '军事': 'http://imil.ifeng.com/20_pagekey/data.shtml',
             '体育': 'http://isports.ifeng.com/tjwData/pagekey/data.shtml',
             '娱乐': 'http://ient.ifeng.com/14_pagekey/data.shtml',
             '财经': 'http://ifinance.ifeng.com/1_pagekey/data.shtml',
             '历史': 'http://ihistory.ifeng.com/21_pagekey/data.shtml',
             '科技': 'http://itech.ifeng.com/7_pagekey/data.shtml'
             }
    return title


def getNewsData(url, title):
    res = requests.get(url)
    static = 'getListDatacallback('
    text = res.text.strip()
    text = res.text[len(static):(len(text) - 2)]
    text = json.loads(text)
    for item in text:
        item['tag'] = title
    text = [{'title': item['title'], 'tag': item['tag']} for item in text]
    return text


def getNewsDataAll(title, pages):
    alldata = []
    for i in range(pages):
        url = getProject()[title]
        url = url.replace('pagekey', str(i))
        onepage = getNewsData(url, title)
        print(title, url, len(onepage))
        alldata.extend(onepage)
        time.sleep(sleeptime)
    return alldata


# list 去重
def unique(list):
    newlist = []
    for x in list:
        if x not in newlist:
            newlist.append(x)
    return newlist


if __name__ == '__main__':
    client = pymongo.MongoClient("localhost", 27017)
    db = client.python_data
    collection = db.data_collection
    source = getProject()
    collection.remove({})
    for key, value in source.items():
        data = getNewsDataAll(key, page)
        data = unique(data)
        collection.insert(data)
