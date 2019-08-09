import re
import bs4
import time
from bs4 import BeautifulSoup
import urllib
from functools import reduce
import lxml
import requests
import argparse

parser = argparse.ArgumentParser(description='添加cookie信息以及选择查询频率')
parser.add_argument('--cookies', type=str, required=True,
                    help='在本地登录后复制cookie到此')
parser.add_argument('--freq', default=60,
                    help='查询的频率，默认为60(s)')
args = parser.parse_args()

url = 'http://jwms.bit.edu.cn/jsxsd/kscj/cjcx_list'
datas = {
    'username': 'XXX',
    'password': 'XXX',
    'lt': 'LT-253641-gCf6nTVLPnaoAsnOodClqJQFr9S1Ts-1565318482985',
    'execution': 'e1s2',
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
    'Cookie': args.cookies  # 需要更换为自己的cookie
}  # 定义头文件，伪装成浏览器


def calAvg(Dict):
    score_tot = 0
    credit_tot = 0
    for item in Dict:
        score_tot += Dict[item]['score'] * Dict[item]['credit']
        credit_tot += Dict[item]['credit']
    return score_tot / credit_tot


sessions = requests.session()
scoreDict = {}

times = 1
while (True):
    flag = 0
    response = sessions.post(url, headers=headers)
    print('第{:d}次查询 状态: {:d}'.format(times, response.status_code))

    soup = BeautifulSoup(response.text, 'lxml')

    tr_tags = soup.find_all('tr')
    for tr_tag in tr_tags[2:]:
        try:
            score = int(tr_tag.find('a').text)
            if score >= 0 and score <= 100:
                td_tags = tr_tag.find_all('td')
                name, credit = td_tags[3].text, float(td_tags[6].text)
                if name not in scoreDict:
                    flag = 1
                    print(name, score, credit)
                    scoreDict[name] = {
                        'score': score,
                        'credit': credit
                    }
        except Exception as e:
            print(e)
            pass
    if flag == 1 and times != 1:
        print('有新变更')
    if times == 1 or flag == 1:
        print('当前加权平均分: {:f}'.format(calAvg(scoreDict)))

    times += 1
    time.sleep(args.freq)
