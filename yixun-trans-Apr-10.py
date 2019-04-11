# 下载对应版本的Chrome driver并将其.exe文件复制到chrome.exe同文件夹下，重启电脑，并安装python的selenium、requests库即可使用

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

appid = '**********' #你的appid
secretKey = '***********' #你的密钥

httpClient = None

def login():
    username = "*********"
    password = "*******"
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
            cn_vul_name = "Fedora安全更新"+ref+"（"+affected_app+"）"
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

        #德文>>配置核查
        elif "IT-Grundschutz" in data:
            name = driver.find_element_by_name("vul_name_cn")
            summary = driver.find_element_by_name("desc_cn_summary")

            line = "配置核查"

            name.clear()
            summary.clear()
            name.send_keys(line)
            summary.send_keys(line)
            OtherCounter = OtherCounter + 1
            driver.find_element_by_css_selector("[class='layui-btn layui-btn-lg']").click()
            print("成功提交一条！已经成功更改德文"+str(OtherCounter)+"条。")



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

        #SuSE漏洞
        elif "SuSE Update for" in data:
            APPandID = re.findall(r"\"SuSE Update for (.*?)\"",data)[0]

            affected_app = APPandID.split(" ",1)[0]
            ref = APPandID.split(" ",1)[1]
            cn_vul_name = "SuSE安全更新"+ref+"（"+affected_app+"）"

            en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
            en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
            en_impact = re.findall(r"\"desc_impact\":\"(.*?)\"",data)[0]
            en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]
    
            name = driver.find_element_by_name("vul_name_cn")
            summary = driver.find_element_by_name("desc_cn_summary")
            affected = driver.find_element_by_name("desc_cn_affected")
            impact = driver.find_element_by_name("desc_cn_impact")
            solu = driver.find_element_by_name("solu_cn")

            name.clear()
            name.send_keys(cn_vul_name)

            cn_summary = baidu_fanyi(en_summary)
            summary.clear()
            summary.send_keys(cn_summary)
            time.sleep(0.2)
        
            if en_affected == "":
                pass
            else:
                cn_affected = baidu_fanyi(en_affected)
                affected.clear()    
                affected.send_keys(cn_affected) 
                time.sleep(0.2)
            
            if en_impact == "":
                pass
            else:
                cn_impact = baidu_fanyi(en_impact)
                impact.clear()    
                impact.send_keys(cn_impact) 
                time.sleep(0.2)

            en_solu = en_solu.strip('\n')
            en_solu = en_solu.replace("/","")
            if "oldstable" in en_solu:
                en_solu = en_solu.replace("oldstable","old stable")
                cn_solu = baidu_fanyi(en_solu)
                cn_solu = cn_solu.replace("分发","发行版")
            elif "Mitigation" in en_solu:
                cn_solu = "NONE"
            solu.clear()
            solu.send_keys(cn_solu)
            time.sleep(0.2)

            driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
            CenCounter = CenCounter + 1
            print("已经成功翻译CentOS或SuSE "+str(CenCounter)+"条。")
        

        #Ubuntu Update for 漏洞
        elif "Ubuntu Update for " in data:
            APPandID = re.findall(r"\"Ubuntu Update for (.*?)\"",data)[0]

            affected_app = APPandID.split(" ",1)[0]
            ref = APPandID.split(" ",1)[1]
            cn_vul_name = "Ubuntu安全更新"+ref+"（"+affected_app+"）"

            en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
            en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
            en_impact = re.findall(r"\"desc_impact\":\"(.*?)\"",data)[0]
            en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]
    
            name = driver.find_element_by_name("vul_name_cn")
            summary = driver.find_element_by_name("desc_cn_summary")
            affected = driver.find_element_by_name("desc_cn_affected")
            impact = driver.find_element_by_name("desc_cn_impact")
            solu = driver.find_element_by_name("solu_cn")

            name.clear()
            name.send_keys(cn_vul_name)

            cn_summary = baidu_fanyi(en_summary)
            cn_summary = cn_summary.replace('“',"")
            cn_summary = cn_summary.replace('”',"")
            summary.clear()
            summary.send_keys(cn_summary)
            time.sleep(0.2)
        
            if en_affected == "":
                pass
            else:
                cn_affected = baidu_fanyi(en_affected)
                affected.clear()    
                affected.send_keys(cn_affected) 
                time.sleep(0.2)
            
            if en_impact == "":
                pass
            else:
                cn_impact = baidu_fanyi(en_impact)
                impact.clear()    
                impact.send_keys(cn_impact) 
                time.sleep(0.2)

            en_solu = en_solu.strip('\n')
            en_solu = en_solu.replace("/","")
            if "oldstable" in en_solu:
                en_solu = en_solu.replace("oldstable","old stable")
                if "distribution" in en_solu:
                    en_solu = en_solu.replace("distribution ","发行版")
                cn_solu = baidu_fanyi(en_solu)
            elif "Mitigation" in en_solu:
                cn_solu = "NONE"
            solu.clear()
            solu.send_keys(cn_solu)
            time.sleep(0.2)

            driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
            CenCounter = CenCounter + 1
            print("已经成功翻译CentOS或SuSE或UBT"+str(CenCounter)+"条。")


        #本地安全检查
        elif "Local Check" in data:
            en_name = re.findall(r"\"vul_name\":\"(.*?)\"",data)[0]
            en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
            
            name = driver.find_element_by_name("vul_name_cn")
            summary = driver.find_element_by_name("desc_cn_summary")
            solu = driver.find_element_by_name("solu_cn")

            name.clear()
            cn_name = en_name.replace("Local Check:","本地安全检查：")
            name.send_keys(cn_name)

            cn_summary = en_summary.replace(" Local Security Checks ","本地安全检查")
            summary.clear()
            summary.send_keys(cn_summary)
            time.sleep(0.2)

            line_solu = "将受影响的包更新到最新的可用版本。"
            solu.clear()
            solu.send_keys(line_solu)
            time.sleep(0.2)

            driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
            CenCounter = CenCounter + 1
            print("已经成功翻译CentOS或SuSE或RedHat或LSC "+str(CenCounter)+"条。")

        #RedHat Update for漏洞
        elif "RedHat Update for" in data:
            APPandID = re.findall(r"\"RedHat Update for (.*?)\"",data)[0]

            affected_app = APPandID.split(" ",1)[0]
            ref = APPandID.split(" ",1)[1]
            cn_vul_name = "RedHat安全更新"+ref+"（"+affected_app+"）"

            en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
            en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
            en_impact = re.findall(r"\"desc_impact\":\"(.*?)\"",data)[0]
            en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]
    
            name = driver.find_element_by_name("vul_name_cn")
            summary = driver.find_element_by_name("desc_cn_summary")
            affected = driver.find_element_by_name("desc_cn_affected")
            impact = driver.find_element_by_name("desc_cn_impact")
            solu = driver.find_element_by_name("solu_cn")

            name.clear()
            name.send_keys(cn_vul_name)

            if "The remote host" in en_summary:
                cn_summary = "远程主机缺少"+affected_app+"软件包的更新"
            else :
                cn_summary = baidu_fanyi(en_summary)
            summary.clear()
            summary.send_keys(cn_summary)
            time.sleep(0.2)
        
            if en_affected == "":
                pass
            else:
                cn_affected = baidu_fanyi(en_affected)
                affected.clear()    
                affected.send_keys(cn_affected) 
                time.sleep(0.2)
            
            if en_impact == "":
                pass
            else:
                cn_impact = baidu_fanyi(en_impact)
                impact.clear()    
                impact.send_keys(cn_impact) 
                time.sleep(0.2)

            en_solu = en_solu.strip('\n')
            en_solu = en_solu.replace("/","")
            if "oldstable" in en_solu:
                en_solu = en_solu.replace("oldstable","old stable")
                if "distribution" in en_solu:
                    en_solu = en_solu.replace("distribution ","发行版")
                cn_solu = baidu_fanyi(en_solu)
            elif "Mitigation" in en_solu:
                cn_solu = "NONE"
            solu.clear()
            solu.send_keys(cn_solu)
            time.sleep(0.2)

            driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
            CenCounter = CenCounter + 1
            print("已经成功翻译CentOS或SuSE或RedHat "+str(CenCounter)+"条。")

        else:
            en_name = re.findall(r"\"vul_name\":\"(.*?)\"",data)[0]
            en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
            en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
            en_impact = re.findall(r"\"desc_impact\":\"(.*?)\"",data)[0]
            en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]
            
            name = driver.find_element_by_name("vul_name_cn")
            summary = driver.find_element_by_name("desc_cn_summary")
            affected = driver.find_element_by_name("desc_cn_affected")
            impact = driver.find_element_by_name("desc_cn_impact")
            solu = driver.find_element_by_name("solu_cn")

            if "Vulnerabilities" in en_name:
                if "Multiple Vulnerabilities" in en_name:
                    cn_name = en_name.replace(" Multiple Vulnerabilities","多个漏洞")
                else:
                    cn_name = baidu_fanyi(en_name)
                name.clear()
                name.send_keys(cn_name)

            elif "Vulnerability" in en_name:
                cn_name = baidu_fanyi(en_name)
                name.clear()
                name.send_keys(cn_name)

            elif "Update for" in en_name:
                cn_name = en_name.replace(" Update for ","安全更新")
                name.clear()
                name.send_keys(cn_name)

            elif "Information Disclosure" in en_name:
                cn_name = en_name.replace("Information Disclosure","信息泄露漏洞")
                name.clear()
                name.send_keys(cn_name)
            
            elif "Security Bypass Vulnerability" in en_name:
                cn_name = en_name.replace("Security Bypass Vulnerability","安全绕过漏洞")
                name.clear()
                name.send_keys(cn_name)

            elif "Security Advisory" in en_name:
                cn_name = en_name.replace(" Security Advisory ","安全公告")
                if "security update" in cn_name:
                    cn_name = cn_name.replace(" security update","安全更新")
                name.clear()
                name.send_keys(cn_name)
            
            elif "Security Updates" in en_name:
                cn_name = en_name.replace("Security Updates","安全更新")
                name.clear()
                name.send_keys(cn_name)
            
            elif "Detection" in en_name:
                cn_name = en_name.replace(" Detection","检测")
                name.clear()
                name.send_keys(cn_name)

            time.sleep(0.2)
            
            cn_summary = baidu_fanyi(en_summary)
            summary.clear()
            summary.send_keys(cn_summary)
            time.sleep(0.2)
     
            en_affected = en_affected.replace("\/","/")
            if en_affected == "":
                pass
            else:
                cn_affected = baidu_fanyi(en_affected)
                #cn_affected = cn_affected.replace(" \u ","_")
                affected.clear()    
                affected.send_keys(cn_affected) 
                time.sleep(0.2)
            
            if en_impact == "":
                pass
            else:
                cn_impact = baidu_fanyi(en_impact)
                impact.clear()    
                impact.send_keys(cn_impact) 
                time.sleep(0.2)
            
            en_solu = en_solu.strip('\n')
            en_solu = en_solu.replace("\/","/")
            line_long1 = "从漏洞公布以来，超过一年时间没有解决方案或者补丁程序。可能不再提供任何解决方式。一般的解决方案选项是升级到新版本，禁用该功能，删除产品或用其他应用替换当前应用。"
            line_long2 = "软件厂商已经发布修复补丁，请阅读参考链接安装相关补丁。"
            line_long3 = "应用安全公告中发布的补丁。"
            line_long4 = "运行Windows Update并更新列出的修补程序或从发布的公告中下载并安装修补程序。"
            line_long5 = "请安装升级后的安装包。"

            if "distribution" in en_solu:
                en_solu = en_solu.replace("oldstable","old stable")
                cn_solu = baidu_fanyi(en_solu)
                cn_solu = cn_solu.replace("分发","发行版")
            elif "Mitigation" in en_solu:
                cn_solu = "NONE"
            elif "No solution or patch was made " in en_solu:
                cn_solu = line_long1
            elif "VendorFix" in en_solu:
                cn_solu = line_long2
            elif "Apply the patch from the referenced advisory." in en_solu:
                cn_solu =line_long3
            elif "Windows Update" in en_solu:
                cn_solu = line_long4
            elif "Please install the updated" in en_solu:
                cn_solu = line_long5
            else :
                cn_solu = baidu_fanyi(en_solu)
            cn_solu = cn_solu.replace("\n","")
            solu.clear()
            solu.send_keys(cn_solu)
            time.sleep(0.2)

            driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
            OtherCounter = OtherCounter + 1
            print("不是Fedora条目,也不是CentOS条目。调用@baidu-trans-API，请提交前在翻译列表中再审阅一遍！进度：{0}/{1}".format(str(number+1),iteraction))
            print("成功保存"+str(OtherCounter)+"条其他格式。")

        number = number + 1

        # 设置访问频率
        time.sleep(2)
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
