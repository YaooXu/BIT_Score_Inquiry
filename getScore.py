import time
from bs4 import BeautifulSoup
import requests
import argparse

parser = argparse.ArgumentParser(description='添加学号以及密码')
parser.add_argument('--ID', type=str, required=True,
                    help='学号')
parser.add_argument('--password', type=str, required=False,
                    help='密码')
parser.add_argument('--freq', type=int, default=-1,
                    help='查询频率，默认为-1，即只查询一次')
args = parser.parse_args()

url = 'https://webvpn.bit.edu.cn/login?cas_login=true'
prefix = "https://webvpn.bit.edu.cn"

datas = {
    'username': args.ID,
    'password': args.password,
    '_eventId': 'submit',
    'rmShown': '1'
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0',
}  # 定义头文件，伪装成浏览器


def getAvg(Dict: dict):
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
response_login = sessions.get(url)

# 重定向后的url
url = response_login.url
soup_login = BeautifulSoup(response_login.text, 'lxml')

# 这两个是隐藏的post参数
lt = soup_login.find('input', {'name': 'lt'}).get('value')
execution = soup_login.find('input', {'name': 'execution'}).get('value')
datas['lt'] = lt
datas['execution'] = execution

print(lt, execution)
response = sessions.post(url, data=datas)  # 登录

# 登录后的主页面
soup_main = BeautifulSoup(response.text, 'lxml')

jwc_redirect = prefix + soup_main.find('div', {"data-detail": "jwc.bit.edu.cn"}).get(
    'data-redirect')

response_jwc = sessions.get(jwc_redirect)
soup_jwc = BeautifulSoup(response_jwc.text, 'lxml')

# 学生综合中心
student_personal_center_url = soup_jwc.find('div', {'class': 'link'}).find_all('a')[0].get('href')
student_personal_center = sessions.get(student_personal_center_url)
soup_student_personal_center = BeautifulSoup(student_personal_center.text, 'lxml')

# 课程成绩查询
score_query_url = prefix + soup_student_personal_center.find('div', {'class': 'wap'}).find_all('a')[5].get('href')
score_query = sessions.get(score_query_url)
soup_score_query = BeautifulSoup(score_query.text, 'lxml')

score_list_url = score_query_url[:score_query_url.rfind('/')] + '/cjcx_list'
score_query_data = {
    "kksj": "",
    "kcxz": "",
    "kcmc": "",
    "xsfs": "all"
}

name2info = {}
subjects = []
times = 1
while (True):
    flag = 0  # 是否有更新
    response_score_list = sessions.post(score_list_url, data=score_query_data)
    soup_score_list = BeautifulSoup(response_score_list.text, 'lxml')
    print('第{:d}次查询 状态: {:d}'.format(times, response_score_list.status_code))
    # print(soup_login)

    tr_tags = soup_score_list.find_all('tr')
    for tr_tag in tr_tags[2:]:
        try:
            score_text = tr_tag.find('a').text

            score = None
            if score_text.isdigit():
                # 成绩可能为浮点数
                score = float(score_text)
            else:
                # 可能是等级制
                level2score = {
                    '优秀': 95,
                    '良好': 85,
                    '中等': 75,
                    '合格': 65,
                    '不合格': 0
                }
                score = level2score[score_text]
                
            if score >= 0 and score <= 100:
                td_tags = tr_tag.find_all('td')
                semester, name, credit = td_tags[1].text, td_tags[3].text, float(
                    td_tags[6].text)
                if name not in subjects:
                    subjects.append(name)
                    flag = 1
                    print(semester, name, score, credit)
                    name2info[name] = {
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
        getAvg(name2info)

    times += 1
    if (args.freq != -1):
        time.sleep(args.freq)
    else:
        break
