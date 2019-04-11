# 下载对应版本的Chrome driver并将其.exe文件复制到chrome.exe同文件夹下，重启电脑，并安装python的selenium、requests库即可使用

#appid = '20190327000281816' #你的appid
#secretKey = 'TYuW81MhXvezOI7dBziS' #你的密钥

import http.client
import hashlib
import urllib.request
import random
import json
import datetime
from selenium import webdriver
import time
import requests
import re
# from googletrans import Translator

appid = '20190327000281816' #你的appid
secretKey = 'TYuW81MhXvezOI7dBziS' #你的密钥

httpClient = None

def login():
    username = "xuzhaoyang"
    password = "1113"
    url = "http://218.94.157.126:9328"
    driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
    driver.get(url)
    driver.find_element_by_id("cam-user-login-username").clear()
    driver.find_element_by_id("cam-user-login-username").send_keys(username)
    driver.find_element_by_id("LAY-user-login-password").clear()
    driver.find_element_by_id("LAY-user-login-password").send_keys(password)
    # 输入验证码的时长，输入完成后点击登录即可，脚本将自动完成遍历翻译
    time.sleep(10)
    print("user login.")
    return driver

def baidu_fanyi(q):
    myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    fromLang = 'en'
    toLang = 'zh'
    salt = random.randint(32768, 65536)
    sign = appid+q+str(salt)+secretKey
    m1 = hashlib.new('md5')
    m1.update(sign.encode('utf-8'))
    sign=m1.hexdigest()
    myurl = myurl +'?q='+urllib.request.quote(q)+'&from='+fromLang+'&to='+toLang+'&appid='+appid+'&salt='+str(salt)+'&sign='+sign
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        #response是HTTPResponse对象
        response = httpClient.getresponse()
        result=response.read()
    
        data = json.loads(result)
        wordMean=data['trans_result'][0]['dst']
        return wordMean
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()


# selenium的cookie和requests所需的cookie不一样（selenium的cookie中有不必要的信息），因此需要重新设置格式。
def get_cookie(driver):
    raw_cookie = driver.get_cookies()[0]
    cookie = {}
    cookie[raw_cookie['name']] = raw_cookie['value']
    return cookie

# 目前设计了Fedora和CentOS
# interaction用于指定遍历的条数
def Translate(driver,cooki,iteraction):
    # 点击“规则翻译”
    driver.find_element_by_class_name("layui-nav-child").find_element_by_tag_name("dd").click()
    number = 0
    FedCounter = 0
    CenCounter = 0
    OtherCounter = 0
    sum = 0
    # 获取数据的url，网站源代码上没有数据
    info_url = "http://218.94.157.126:9328/translate/get_vul"
    while number<iteraction:
        # 获取数据并转成str类型
        data = requests.get(info_url, cookies=cookie).content
        data = str(data,'utf-8')
        if "Fedora Update for" in data:
            # 找到漏洞ID、影响的包、影响的系统
            ref = "FEDORA-"+re.findall(r"FEDORA-(.*?)\"",data)[0]
            affected_app = re.findall(r"Fedora Update for (.*?) FEDORA",data)[0]
            system = re.findall(r"\"desc_affected\":\".*? on (.*?)\"",data)[0]
            # 构造提交的信息 
            cn_vul_name = "Fedora 安全更新 "+ref+"（"+affected_app+"）"
            cn_vul_desc = "Fedora发布了"+affected_app+"相关安全更新 " + ref + "。"
            cn_affected_version = system + "上的" + affected_app+"。"
            # 找到对于的输入框
            name = driver.find_element_by_name("vul_name_cn")
            desc = driver.find_element_by_name("desc_cn_summary")
            version = driver.find_element_by_name("desc_cn_affected")
            # 清除输入框，并填入数据
            name.clear()
            desc.clear()
            version.clear()

            name.send_keys(cn_vul_name)
            desc.send_keys(cn_vul_desc)
            version.send_keys(cn_affected_version)
            # 点击提交按钮，打印成功信息
            driver.find_element_by_css_selector("[class='layui-btn layui-btn-lg']").click()
            FedCounter = FedCounter + 1
            print("成功提交一条！已经成功翻译FEDORA "+str(FedCounter)+"条。")

        elif "CentOS Update for" in data:

            APPandID = re.findall(r"\"CentOS Update for (.*?)\"",data)[0]

            affected_app = APPandID.split(" ",1)[0]
            ref = APPandID.split(" ",1)[1]
            system = re.findall(r" on (.*?)\"",data)[0]



            cn_vul_name = "CentOS 安全更新 "+ref+"（"+affected_app+"）"
            cn_vul_desc = "CentOS发布了"+affected_app+"相关安全更新 " + ref + "。"
            cn_affected_version = system + "上的" + affected_app+"。"

            name = driver.find_element_by_name("vul_name_cn")
            desc = driver.find_element_by_name("desc_cn_summary")
            version = driver.find_element_by_name("desc_cn_affected")

            name.clear()
            desc.clear()
            version.clear()

            name.send_keys(cn_vul_name)
            desc.send_keys(cn_vul_desc)
            version.send_keys(cn_affected_version)

            driver.find_element_by_css_selector("[class='layui-btn layui-btn-lg']").click()
            CenCounter = CenCounter + 1
            print("成功提交一条！已经成功翻译CentOS "+str(CenCounter)+"条。")
        else:
            en_name = re.findall(r"\"vul_name\":\"(.*?)\"",data)[0]
            en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
            en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
            en_impact = re.findall(r"\"desc_impact\":\"(.*?)\"",data)[0]
            en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]
            sum = len(en_affected) + len(en_impact) + len(en_name) + len(en_solu) + len(en_summary)         
            print("已翻译：{}字符".format(sum))
           
            cn_name = baidu_fanyi(en_name)
            cn_summary = baidu_fanyi(en_summary)
            cn_affected = baidu_fanyi(en_affected)
            cn_impact = baidu_fanyi(en_impact)
            cn_solu = baidu_fanyi(en_solu)

            name = driver.find_element_by_name("vul_name_cn")
            summary = driver.find_element_by_name("desc_cn_summary")
            affected = driver.find_element_by_name("desc_cn_affected")
            impact = driver.find_element_by_name("desc_cn_impact")
            solu = driver.find_element_by_name("solu_cn")

            name.clear()
            name.send_keys(cn_name)
            
            summary.clear()
            time.sleep(0.2)
            summary.send_keys(cn_summary)
            time.sleep(0.2)
            affected.clear()
            time.sleep(0.2)
            affected.send_keys(cn_affected)
            time.sleep(0.2)
            impact.clear()
            time.sleep(0.2)
            if cn_impact == "":
                cn_impact = " "
            impact.send_keys(cn_impact)
            time.sleep(0.2)
            solu.clear()
            time.sleep(0.2)
            solu.send_keys(cn_solu)

            driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
            OtherCounter = OtherCounter + 1
            print("不是Fedora条目,也不是CentOS条目。调用@baidu-trans-API，请提交前在翻译列表中再审阅一遍！进度：{0}/{1}".format(str(number+1),iteraction))
            print("成功保存"+str(OtherCounter)+"条其他格式。")

        number = number + 1

        # 设置访问频率
        time.sleep(1)
    print("任务完成啦，本次共翻译{0}条FEDORA，{1}条CentOS，还有{2}条未翻译的内容在“翻译列表”栏内".format
        (FedCounter,CenCounter,(iteraction-FedCounter-CenCounter)))


if __name__ == "__main__":
    start = datetime.datetime.now()
    print("开始翻译...")
    driver = login()
    cookie = get_cookie(driver)
    Translate(driver,cookie,10)
    print("翻译完成!!")
    end = datetime.datetime.now()
    print ("共运行时间：{}".format(end-start))
