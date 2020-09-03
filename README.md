# BIT_Score_Inquiry

- 2020/9/3更新：修复了遇到等级制成绩(如'优秀')和浮点数成绩无法正常处理的bug

- 2020/8/26更新：现可支持webvpn，不用校园网可以直接查询。
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

## 注意事项
- 校园网环境似乎无法正常访问webvpn，使用非校园网即可

- 按学生手册，优秀、良好、中等、合格、不合格时，分别折算为95分、85分、75分、65分、0分

## 效果截图

<img src="https://gitee.com/yaooxu/image-bed/raw/master/img/image-20200826154450793.png" alt="image-20200826154450793" style="zoom: 67%;" />