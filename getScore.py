import re
import bs4
import time
from bs4 import BeautifulSoup
import urllib
from functools import reduce
import lxml
import requests
import argparse

parser = argparse.ArgumentParser(description='添加学号以及密码')
parser.add_argument('--ID', type=str, required=True,
                    help='学号')
parser.add_argument('--password', type=str, required=True,
                    help='密码')
parser.add_argument('--freq', type=int, default=60,
                    help='查询频率，默认为60s')
args = parser.parse_args()

url = 'https://login.bit.edu.cn/cas/login?service=http%3A%2F%2Fjwms.bit.edu.cn%2F'
datas = {
    'username': args.ID,
    'password': args.password,
    # 'it'
    # 'execution'
    '_eventId': 'submit',
    'rmShown': '1'
}
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': 'https://login.bit.edu.cn/cas/login?service=http%3A%2F%2Fjwms.bit.edu.cn%2F',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0',
}  # 定义头文件，伪装成浏览器


def calAvg(Dict: dict):
    semestersGpa = {}
    for value in Dict.values():
        if value['semester'] not in semestersGpa:
            semestersGpa[value['semester']] = {}
            semestersGpa[value['semester']]['score_tot'] = 0
            semestersGpa[value['semester']]['credit_tot'] = 0

        semestersGpa[value['semester']]['score_tot'] += value['score'] * \
            value['credit']
        semestersGpa[value['semester']]['credit_tot'] += value['credit']
    print('\n')
    for key, value in semestersGpa.items():
        print('{:s}学期的加权平均分: {:f}'.format(
            key, value['score_tot'] / value['credit_tot']))

    score_tot = 0
    credit_tot = 0
    for value in Dict.values():
        score_tot += value['score'] * value['credit']
        credit_tot += value['credit']
    print('前{:d}学期加权平均分: {:f}\n'.format(
        len(semestersGpa), score_tot / credit_tot))


sessions = requests.session()
res = sessions.get(url, headers=headers)
soup = BeautifulSoup(res.text, 'lxml')
# 这两个是隐藏的post参数
lt = soup.find('input', {'name': 'lt'}).get('value')
execution = soup.find('input', {'name': 'execution'}).get('value')
datas['lt'] = lt
datas['execution'] = execution
print(lt, execution)
sessions.post(url, headers=headers, data=datas)  # 登录

semDicts = {}
subjects = []
times = 1
scoreList_url = 'http://jwms.bit.edu.cn/jsxsd/kscj/cjcx_list'
while (True):
    flag = 0  # 是否有更新
    response = sessions.get(scoreList_url)
    soup = BeautifulSoup(response.text, 'lxml')
    print('第{:d}次查询 状态: {:d}'.format(times, response.status_code))
    # print(soup)

    tr_tags = soup.find_all('tr')
    for tr_tag in tr_tags[2:]:
        try:
            score = int(tr_tag.find('a').text)
            if score >= 0 and score <= 100:
                td_tags = tr_tag.find_all('td')
                semester, name, credit = td_tags[1].text, td_tags[3].text, float(
                    td_tags[6].text)
                if name not in subjects:
                    subjects.append(name)
                    flag = 1
                    print(semester, name, score, credit)
                    semDicts[name] = {
                        'semester': semester,
                        'score': score,
                        'credit': credit
                    }
        except Exception as e:
            print(e)
            pass
    if flag == 1 and times != 1:
        print('有新变更')
    if times == 1 or flag == 1:
        calAvg(semDicts)

    times += 1
    time.sleep(args.freq)
