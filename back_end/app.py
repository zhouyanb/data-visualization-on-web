from flask import *
from flask_cors import *
from lxml import etree
import ssl
from urllib import request
import re

app = Flask(__name__)
CORS(app, supports_credentials=True)

# 建立一个不需要SSL验证的上下文
ssl._create_default_https_context = ssl._create_unverified_context

url = 'https://www.nowcoder.com/intern/center?recruitType=1&page='

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"}


# requests.DEFAULT_RETRIES = 5
# s = requests.session()
# s.keep_alive = False
# res = requests.get(url,headers=header,verify=False)
# time.sleep(5)

def crawler(url):
    work_num_pay = {}
    work_company = {}
    work_area = {}
    for i in range(1, 21):
        print('page : %d' % i)
        urlpg = url + str(i)
        rep = request.Request(url=urlpg, headers=header)
        res = request.urlopen(rep)
        html = etree.HTML(res.read())
        lis = html.xpath("//div[@class='module-body']/ul[@class='reco-job-list']/li")

        for li in lis:
            try:
                work = li.xpath(".//div[@class='reco-job-cont']/a/text()")[0]
                company = li.xpath(".//div[@class='reco-job-com']/a/text()")[0]
                pay = li.xpath(".//div[@class='reco-job-info']/div[1]/span[2]/text()")[0]
                try:
                    adder = li.xpath(".//div[@class='reco-job-info']/div[1]/span[1]/text()")[0].split(',')[0]
                except:
                    pass
                work_num_pay[work] = pay
                work_company[work] = company
                work_area[work] = adder
            except:
                pass
    # print(work_company)
    # print(work_area)
    return work_num_pay, work_company, work_area


def getWorkData(datadict, companydict, areadict):
    alldata = []
    companylist = []
    arealist = []

    class workdata:
        def __init__(self):
            self.num = 0
            self.pay = 0
            self.pay_num = 0

        def analysis_work(self, list):
            for i in list:
                if i != None:
                    self.num += 1
                    try:
                        if datadict[i.group()] != '薪酬面议':
                            # print(datadict[i.group()].split('-')[0])
                            self.pay += int(datadict[i.group()].split('-')[0])
                            self.pay_num += 1
                    except:
                        pass

        def getpay(self):
            if self.pay_num == 0:
                self.pay = 0
            else:
                self.pay = self.pay / self.pay_num * 30
            self.pay = int(self.pay)

    class companydata:
        def __init__(self):
            self.worklist = []
            self.count = 0

        def add(self):
            self.worklist.append(self.count)

        def clear(self):
            self.count = 0

    class areadata:
        def __init__(self):
            self.num = 0
            self.work_num_pay = []
            self.worklist = []
            self.back_end = []
            self.front_end = []
            self.java = []
            self.algorithm = []
            self.dataanalysis = []
            self.softwaretest = []

        def count(self):
            self.num += 1

        def addwork(self,work):
            self.worklist.append(work)

    huawei = companydata()
    tencent = companydata()
    alibaba = companydata()
    baidu = companydata()

    beijing = areadata()
    shanghai = areadata()
    shenzhen = areadata()
    hangzhou = areadata()

    def getnum(list):
        obj = workdata()
        obj.analysis_work(list)
        obj.getpay()
        return obj.num, obj.pay

    def selectecompany(worklist):
        def dataclear(obj):
            obj.add()
            obj.clear()

        def dataselect(name, work):
            try:
                if companydict[work] == name:
                    if name == '华为':
                        huawei.count += 1
                    elif name == '腾讯':
                        tencent.count += 1
                    elif name == '阿里巴巴':
                        alibaba.count += 1
                    elif name == '百度':
                        baidu.count += 1
            except:
                pass

        for work in worklist:
            if work != None:
                dataselect('华为', work.group())
                dataselect('腾讯', work.group())
                dataselect('阿里巴巴', work.group())
                dataselect('百度', work.group())
        dataclear(huawei)
        dataclear(tencent)
        dataclear(alibaba)
        dataclear(baidu)

    def selectarea(worklist):
        def getdata(work):
            try:
                if areadict[work] == '北京':
                    beijing.count()
                    beijing.addwork(work)
                elif areadict[work] == '上海':
                    shanghai.count()
                    shanghai.addwork(work)
                elif areadict[work] == '深圳':
                    shenzhen.count()
                    shenzhen.addwork(work)
                elif areadict[work] == '杭州':
                    hangzhou.count()
                    hangzhou.addwork(work)
            except:
                pass

        for work in worklist:
            if work != None:
                getdata(work.group())
    def find_data(datalist):
        back_end = []
        front_end = []
        java = []
        algorithm = []
        dataanalysis = []
        softwaretest = []
        for workitem in datalist:
            back_end.append(re.search(r'\S*后端\S*', workitem))
            front_end.append(re.search(r'\S*前端\S*', workitem))
            java.append(re.search(r'\S*java\S*', workitem, re.IGNORECASE))
            algorithm.append(re.search(r'\S*算法\S*', workitem))
            dataanalysis.append(re.search(r'\S*数据分析\S*', workitem))
            softwaretest.append(re.search(r'\S*测试\S*', workitem))
        return back_end,front_end,java,algorithm,dataanalysis,softwaretest

    def find_area_work(area):
        area.back_end,area.front_end,area.java,area.algorithm,area.dataanalysis,area.softwaretest = find_data(area.worklist)

    def create_area_work_num(area):
        area.work_num_pay.append(getnum(area.back_end))
        area.work_num_pay.append(getnum(area.front_end))
        area.work_num_pay.append(getnum(area.java))
        area.work_num_pay.append(getnum(area.algorithm))
        area.work_num_pay.append(getnum(area.dataanalysis))
        area.work_num_pay.append(getnum(softwaretest))

    worklist = []
    for i in datadict.keys():
        worklist.append(i)
    back_end, front_end, java, algorithm, dataanalysis, softwaretest = find_data(worklist)
    # print(java)
    alldata.append(getnum(back_end))
    alldata.append(getnum(front_end))
    alldata.append(getnum(java))
    alldata.append(getnum(algorithm))
    alldata.append(getnum(dataanalysis))
    alldata.append(getnum(softwaretest))

    selectecompany(back_end)
    selectecompany(front_end)
    selectecompany(java)
    selectecompany(algorithm)
    selectecompany(dataanalysis)
    selectecompany(softwaretest)

    companylist.append(huawei.worklist)
    companylist.append(tencent.worklist)
    companylist.append(alibaba.worklist)
    companylist.append(baidu.worklist)

    selectarea(back_end)
    selectarea(front_end)
    selectarea(java)
    selectarea(algorithm)
    selectarea(dataanalysis)
    selectarea(softwaretest)

    find_area_work(beijing)
    find_area_work(shanghai)
    find_area_work(shenzhen)
    find_area_work(hangzhou)

    create_area_work_num(beijing)
    create_area_work_num(shanghai)
    create_area_work_num(shenzhen)
    create_area_work_num(hangzhou)

    arealist.append(beijing)
    arealist.append(shanghai)
    arealist.append(shenzhen)
    arealist.append(hangzhou)

    return alldata, companylist, arealist


area_list = []
area_work_pay = []
work_pay_dict, work_company_dict, work_area_dict = crawler(url)
# print(datadict)
alldata, company_list, areadata = getWorkData(work_pay_dict, work_company_dict, work_area_dict)
for i in areadata:
    area_list.append(i.num)
    area_work_pay.append(i.work_num_pay)
    print(i.work_num_pay)

# print(area_work)
@app.route('/getdata', methods=['POST'])
def getdata():
    work_num_data = []
    work_pay_data = []
    for i in alldata:
        work_num_data.append(i[0])
        work_pay_data.append(i[1])
    return {'work_num': work_num_data, 'work_pay': work_pay_data, 'company_data': company_list, 'area_data': area_list,'area_detail': area_work_pay}

