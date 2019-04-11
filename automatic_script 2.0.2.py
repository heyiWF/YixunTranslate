# -*- coding: utf-8 -*-
# 下载对应版本的Chrome driver并将其.exe文件复制到chrome.exe同文件夹下，重启电脑，并安装python的selenium、requests库即可使用


from selenium import webdriver
from googletrans import Translator
import time
import requests
import re


def login():

    #暴露密码了，尴尬=_=
    username = "yourname"
    password = "1234"
    url = "http://218.94.157.126:9328"
    driver = webdriver.Chrome()
    driver.get(url)
    driver.find_element_by_id("cam-user-login-username").clear()
    driver.find_element_by_id("cam-user-login-username").send_keys(username)
    driver.find_element_by_id("LAY-user-login-password").clear()
    driver.find_element_by_id("LAY-user-login-password").send_keys(password)
    # 等待用户输入验证码，登陆成功后才继续
    while driver.current_url == "http://218.94.157.126:9328/login": ...

    return driver

# selenium的cookie和requests所需的cookie不一样（selenium的cookie中有不必要的信息），因此需要重新设置格式。
def get_cookie(driver):
    raw_cookie = driver.get_cookies()[0]
    cookie = {}
    cookie[raw_cookie['name']] = raw_cookie['value']
    return cookie

# 目前设计了Fedora和CentOS
# iteration用于指定遍历的条数
def Translate(driver,cookie,iteration):
    # 点击“规则翻译”
    driver.find_element_by_class_name("layui-nav-child").find_element_by_tag_name("dd").click()
    number = 0
    FedCounter = 0
    CenCounter = 0
    OtherCounter = 0
    translator = Translator()
    # 如果上不了Google可以把上一行注释掉，用下面这条
    translator = Translator(service_urls=['translate.google.cn'])
    # 获取数据的url，网站源代码上没有数据
    info_url = "http://218.94.157.126:9328/translate/get_vul"
    while number<iteration:
        # 获取数据并转成str类型
        data = requests.get(info_url, cookies=cookie).content
        data = str(data,'utf-8')
        #print(data)
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

            cn_name = translator.translate(en_name,dest='zh-CN').text
            cn_summary = translator.translate(en_summary,dest='zh-CN').text
            cn_affected = translator.translate(en_affected,dest='zh-CN').text
            cn_impact = translator.translate(en_impact,dest='zh-CN').text
            cn_solu = translator.translate(en_solu,dest='zh-CN').text

            name = driver.find_element_by_name("vul_name_cn")
            summary = driver.find_element_by_name("desc_cn_summary")
            affected = driver.find_element_by_name("desc_cn_affected")
            impact = driver.find_element_by_name("desc_cn_impact")
            solu = driver.find_element_by_name("solu_cn")

            name.clear()
            summary.clear()
            affected.clear()
            impact.clear()
            solu.clear()

            name.send_keys(cn_name)
            summary.send_keys(cn_summary)
            affected.send_keys(cn_affected)
            impact.send_keys(cn_impact)
            solu.send_keys(cn_solu)

            driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
            OtherCounter = OtherCounter + 1
            print("不是Fedora条目,也不是CentOS条目。调用Google Translate API，请提交前在翻译列表中再审阅一遍！进度：{0}/{1}".format(str(number+1),iteration))
            print("成功保存"+str(OtherCounter)+"条其他格式。")

        number = number + 1

        # 设置访问频率
        time.sleep(2)
    print("任务完成啦，本次共翻译{0}条Fedora，{1}条CentOS，还有{2}条通过Google翻译的内容在“翻译列表”栏内".format
        (FedCounter,CenCounter,OtherCounter))


if __name__ == "__main__":
    driver = login()
    cookie = get_cookie(driver)
    print("user login.")
    Translate(driver,cookie,1)
