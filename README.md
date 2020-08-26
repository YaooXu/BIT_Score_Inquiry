# BIT_Score_Inquiry

2020/8/26更新：现可支持webvpn，不用校园网可以直接查询。
## 依赖库
- python3
- bs4
- requests
- argparse

## 功能
- 成绩有更新时提醒
- 计算每个学期的加权平均分和总得加权平均分 ~~让您充满B TREE~~

## 参数说明
1. --ID: 学号
2. --password: 登录教务处的密码
3. --freq: 非必须，默认为-1，如果设置为整数，则以该频率反复查询(用于第一时间得到出分消息)

## 用法
1. python getScore.py --ID xxxxx --password xxxxx 

2. python getScore.py --ID xxxxx --password xxxxx --freq 60 

## 效果截图

<img src="https://gitee.com/yaooxu/image-bed/raw/master/img/image-20200826154450793.png" alt="image-20200826154450793" style="zoom: 67%;" />