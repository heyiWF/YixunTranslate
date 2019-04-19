# -*- coding: utf-8 -*-
# 此脚本依赖Chrome driver，selenium、requests和googletrans库


from selenium import webdriver
from googletrans import Translator
import time
import requests
import re

number = 0
SubmitCounter = 0
SaveCounter = 0

def login():
    # 改成自己的账号密码
    username = "username"
    password = "password"
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

# iteration用于指定遍历的条数
def Translate(driver,cookie,iteration):
    # 点击“规则翻译”
    driver.find_element_by_class_name("layui-nav-child").find_element_by_tag_name("dd").click()
    # 声明全局变量
    global number,SubmitCounter,SaveCounter
    # 初始化计数器
    number = 0
    SubmitCounter = 0
    SaveCounter = 0
    
    while number<iteration:
        DoTranslate(cookie)
        number = number + 1
        print("进度：{0}/{1}".format(str(number),iteration))
        # 设置访问频率
        time.sleep(2)

    print("本次共翻译{0}条，其中{1}条已提交，还有{2}条未提交内容在“翻译列表”栏内".format
        (iteration,SubmitCounter,SaveCounter))

# 针对解决方案的预设文字翻译
def TransSolu(translator,solu):
    rep1 = "自从该漏洞被公布后至少一年时间，还未有已知可行的解决方案。并且可能以后也不会再提供。一般的解决方案是升级到较新版本，禁用相应功能，删除产品或用另一个替换产品。"
    rep2 = "软件厂商已经发布修复补丁，请阅读参考链接安装相关补丁。"
    rep3 = "应用安全公告中发布的补丁。"
    rep4 = "运行Windows Update并更新列出的修补程序或从发布的公告中下载并安装修补程序。"
    rep5 = "更新受影响的软件包至最新可用版本。"
    rep6 = "该产品有相关更新可用，请升级产品。有关更多信息，请参阅参考链接。"
    rep7 = "请安装软件升级包，详细操作请阅读参考网页。"
    rep8 = "暂无解决方案，请阅读参考网页或者使用铱迅安全防护设备。"
    rep9 = "应用参考公告中的补丁。"
    rep10 = "请参阅引用的供应商公告以获取解决方案。"
    rep11 = "运行Windows更新并更新列出的修补程序或下载并更新公告中提到的修补程序。"
    
    if "Mitigation" in solu:
        solu = "NONE"
    elif "for at least one year" in solu:
        solu = rep1
    elif "VendorFix" in solu:
        solu = rep2
    elif "Apply the patch from the referenced advisory." in solu:
        solu = rep3
    elif "Windows Update" in solu:
        solu = rep4
    elif "Update the affected packages to" in solu:
        solu = rep5
    elif "Updates are available" in solu:
        solu = rep6
    elif "Please install the updated" in solu:
        solu = rep7
    elif "Please Install the Updated" in solu:
        solu = rep7
    elif solu == "None" or solu == "WillNotFix" or solu == "Workaround":
        solu = rep8
    elif "Run yum update" in solu:
        solu = solu.replace("Run ","运行命令")
        solu = solu.replace(" to update your system. ","更新该软件包。")
    elif solu == "Apply the patch from the referenced advisory.":
        solu = rep9
    elif solu == "See the referenced vendor advisory for a solution.":
        solu = rep10
    elif "update mentioned hotfixes" in solu:
        solu = rep11
    elif "http" in solu:
        sitestart = solu.find("http")                #找到http开头的位置
        siteend = solu.find(" ",sitestart+1)         #找到网址结尾的位置，如果返回值为-1则未找到
        webline = solu[sitestart:siteend]            #把网址切出来
        if sitestart == 0 :
            solu = webline
        elif siteend == -1 :                           #网址在末尾
            solu = solu[0:sitestart]
            solu = translator.translate(solu,dest='zh-cn').text + webline
        else :                                       #网址在中间
            solu_1 = solu[0:sitestart]
            solu_2 = solu[siteend:]
            solu = translator.translate(solu_1,dest='zh-cn').text + webline +translator.translate(solu_2,dest='zh-cn').text        
    else :
        if "distribution" in solu:
            solu = solu.replace("oldstable","old stable")
        else:
            pass
        solu = translator.translate(solu,dest='zh-CN').text
        # 去除\n和\/输出，以及修改一些不恰当的翻译
    solu = solu.replace("有关更新，请参阅参考链接。","可使用提供的参考链接进行更新。")
    solu = fix(solu,0)
    solu = solu.replace(" + ","+")
    solu = solu.replace("：",":")
    
    return solu
        
# 对翻译结果进行修正，通用于各个栏目的替换方法写在这个函数里
def fix(txt,isname):
    txt = txt.replace("\\ n","\n")
    txt = txt.replace(" \\ / ","/")
    txt = txt.replace(" \\ /","/")
    txt = txt.replace("\\ / ","/")
    txt = txt.replace("\\ /","/")
    txt = txt.replace("\\/","/")
    txt = txt.replace("拒绝服务条件","拒绝服务攻击") 
    txt = txt.replace("拉伸","stretch") 
    txt = txt.replace("挤压","squeeze") 
    txt = txt.replace("喘息","wheezy") 
    txt = txt.replace("将结果设置为KB","将结果保存到知识库中") 
    txt = txt.replace("将结果保存为KB","将结果保存到知识库中") 
    txt = txt.replace("分布","发行版")
    txt = txt.replace("的分发","发行版")
    txt = txt.replace("咨询","公告")
    txt = txt.replace("清理用户提供的","验证用户提供的")
    txt = txt.replace("精心设计","特定构造")
    txt = txt.replace("拒绝服务漏洞","拒绝服务攻击漏洞")
    txt = txt.replace("上载","上传")
    txt = txt.replace("XSS","跨站脚本攻击")                             # 临时解决小于号输出异常，原因未知
    txt = txt.replace("DoS","拒绝服务攻击")
    txt = txt.replace("权限提升","提权")
    txt = txt.replace("RCE","远程命令执行")
    txt = txt.replace("SSRF","服务器端请求伪造")
    txt = txt.replace("CSRF","跨站请求伪造")
    txt = txt.replace("XXE","XML外部实体")
    txt = txt.replace("并且容易出现","容易出现")
    txt = txt.replace("NVT","漏洞规则")
    if isname:
        txt = re.sub(r"- \d年\d月\d日","",txt)
        txt = re.sub(r"- \d月\d日","",txt)
        txt = re.sub(r"\d年\d月\d日","",txt)
        txt = re.sub(r"\d月\d日","",txt)
    if "主机随" in txt:
        tmp = re.findall("主机随(.*?)一起安装.*?",txt)[0]
        tmp = "该主机安装了"+tmp
        txt = re.sub(r".*?主机随.*?安装",tmp,txt)
    elif "主机与" in txt:
        tmp = re.findall("主机与(.*?)一起安装.*?",txt)[0]
        tmp = "该主机安装了"+tmp
        txt = re.sub(r".*?主机与.*?安装",tmp,txt)
    # 去除英文句号
    txt = txt.strip(".")
    if txt == "" or txt.endswith('。') or isname:
        pass
    else:
        txt = txt+'。'
        
    return txt
        
# 返回字符串的第一个单词，用于判断Ubuntu/RedHat(/Mandriva)
def first_word(text: str) -> str:
    return re.search("([\w']+)", text).group(1)

# 翻译主体函数
def DoTranslate(cookie):
    # 声明全局变量
    global number,SubmitCounter,SaveCounter
    # 获取数据的url，网站源代码上没有数据
    info_url = "http://218.94.157.126:9328/translate/get_vul"
    translator = Translator(service_urls=['translate.google.cn'])
    # 获取数据并转成str类型
    data = requests.get(info_url, cookies=cookie).content
    data = str(data,'utf-8')
    
    
    #1 Fedora
    if "Fedora Update for" in data:
        # 找到漏洞ID、影响的包、影响的系统
        ref = "FEDORA-"+re.findall(r"FEDORA-(.*?)\"",data)[0]
        affected_app = re.findall(r"Fedora Update for (.*?) FEDORA",data)[0]
        system = re.findall(r"\"desc_affected\":\".*? on (.*?)\"",data)[0]
        # 构造提交的信息 
        cn_vul_name = "Fedora 安全更新 "+ref+"（"+affected_app+"）"
        cn_vul_desc = "Fedora发布了"+affected_app+"相关安全更新，" + ref + "。"
        cn_affected_version = system + "上的" + affected_app+"软件。"
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
        SubmitCounter = SubmitCounter + 1
        print("成功提交一条！已经成功提交 "+str(SubmitCounter)+" 条已适配格式。")


    #2 CentOS
    elif "CentOS Update for" in data:

        APPandID = re.findall(r"\"CentOS Update for (.*?)\"",data)[0]

        affected_app = APPandID.split(" ",1)[0]
        ref = APPandID.split(" ",1)[1]
        system = re.findall(r" on (.*?)\"",data)[0]



        cn_vul_name = "CentOS 安全更新 "+ref+"（"+affected_app+"）"
        cn_vul_desc = "CentOS发布了"+affected_app+"相关安全更新，" + ref + "。"
        cn_affected_version = system + "上的" + affected_app+"软件。"

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
        SubmitCounter = SubmitCounter + 1
        print("成功提交一条！已经成功提交 "+str(SubmitCounter)+" 条已适配格式。")
        
        
    #3 德文>>配置核查
    # 也可以用googletrans的detect识别语言，但这里遇到的都是固定格式没必要了
    elif "IT-Grundschutz" in data:
        name = driver.find_element_by_name("vul_name_cn")
        summary = driver.find_element_by_name("desc_cn_summary")

        line = "配置核查"

        name.clear()
        summary.clear()
        name.send_keys(line)
        summary.send_keys(line)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-lg']").click()
        SubmitCounter = SubmitCounter + 1
        print("成功提交一条！已经成功提交 "+str(SubmitCounter)+" 条已适配格式。")
        
        
    #4 SuSE
    elif "SuSE Update for" in data:
        APPandID = re.findall(r"\"SuSE Update for (.*?)\"",data)[0]

        affected_app = APPandID.split(" ",1)[0]
        ref = APPandID.split(" ",1)[1]
        cn_vul_name = "SuSE 安全更新 "+ref

        en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
        en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
        system = re.findall(r"\"desc_affected\":\".*? on (.*?)\"",data)[0]
        en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]

        name = driver.find_element_by_name("vul_name_cn")
        summary = driver.find_element_by_name("desc_cn_summary")
        affected = driver.find_element_by_name("desc_cn_affected")
        solu = driver.find_element_by_name("solu_cn")

        name.clear()
        name.send_keys(cn_vul_name)

        cn_summary = "远程主机缺失"+affected_app+"软件包的更新版本。"
        # fix修改翻译不当的文字，下同
        cn_summary = fix(cn_summary,0)
        summary.clear()
        summary.send_keys(cn_summary)
        time.sleep(0.2)
    
        cn_affected = system+"上的"+affected_app+"软件。"
        cn_affected = fix(cn_affected,0)
        affected.clear()
        affected.send_keys(cn_affected)

        cn_solu = TransSolu(translator,en_solu)
        solu.clear()
        solu.send_keys(cn_solu)
        time.sleep(0.2)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-lg']").click()
        SubmitCounter = SubmitCounter + 1
        print("成功提交一条！已经成功提交 "+str(SubmitCounter)+" 条已适配格式。")
        
        
    #5 Ubuntu/RedHat
    elif "Ubuntu Update for " in data or "RedHat Update for" in data:
        APPandID = re.findall(r" Update for (.*?)\"",data)[0]
        sys = re.findall(r"\"vul_name\":\"(.*?) Update for .*?\"",data)[0]
        system = re.findall(r"\"desc_affected\":\".*? on (.*?)\"",data)[0]

        affected_app = APPandID.split(" ",1)[0]
        ref = APPandID.split(" ",1)[1]
        cn_vul_name = (first_word(sys))+" 安全更新 "+ref+"（"+affected_app+"）"

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

        # Ubuntu的两种情况
        if "The remote host" in en_summary:
            cn_summary = "远程主机缺失"+affected_app+"软件包的更新版本。"
        elif "Linux kernel vulnerabilities" in en_summary:
            cn_summary = "Ubuntu Linux 内核漏洞更新 "+ref+"。"
        else:
            cn_summary = translator.translate(en_summary,dest='zh-CN').text
        cn_summary = fix(cn_summary,0)
        summary.clear()
        summary.send_keys(cn_summary)
        time.sleep(0.2)
    
        cn_affected = system+"上的"+affected_app+"软件。"
        cn_affected = fix(cn_affected,0)
        cn_impact = translator.translate(en_impact,dest='zh-CN').text
        # 改成汉语语序
        cn_impact = re.sub(r"成功利用.*?远程攻击者","远程攻击者可能利用此漏洞",cn_impact)
        cn_impact = re.sub(r"成功利用.*?攻击者","攻击者可能利用此漏洞",cn_impact)
        cn_impact = fix(cn_impact,0)
        affected.clear()
        impact.clear()
        affected.send_keys(cn_affected)
        impact.send_keys(cn_impact)

        #en_solu = en_solu.strip('\n')
        #en_solu = en_solu.replace("/","")
        cn_solu = TransSolu(translator,en_solu)
        solu.clear()
        solu.send_keys(cn_solu)
        time.sleep(0.2)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-lg']").click()
        SubmitCounter = SubmitCounter + 1
        print("成功提交一条！已经成功提交 "+str(SubmitCounter)+" 条已适配格式。")
    
    
    #6 Local Check
    elif "Local Check" in data:
        en_name = re.findall(r"\"vul_name\":\"(.*?)\"",data)[0]
        
        name = driver.find_element_by_name("vul_name_cn")
        solu = driver.find_element_by_name("solu_cn")
        summary = driver.find_element_by_name("desc_cn_summary")

        name.clear()
        cn_name = en_name.replace("Local Check:","本地安全检查：")
        name.send_keys(cn_name)

        cn_summary = cn_name+"。"
        summary.clear()
        summary.send_keys(cn_summary)
        time.sleep(0.2)

        cn_solu = "更新受影响的软件包至最新可用版本。"
        solu.clear()
        solu.send_keys(cn_solu)
        time.sleep(0.2)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-lg']").click()
        SubmitCounter = SubmitCounter + 1
        print("成功提交一条！已经成功提交 "+str(SubmitCounter)+" 条已适配格式。")
        
        
    #7 Debian LTS
    elif "Debian LTS Advisory" in data:
        en_name = re.findall(r"\"vul_name\":\"(.*?)\"",data)[0]
        en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
        en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
        en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]
        affected_app = re.findall(r"(.*?) on Debian",en_affected)[0]

        cn_name = translator.translate(en_name,dest='zh-CN').text
        cn_name = cn_name.replace("Advisory","安全公告")
        cn_summary = translator.translate(en_summary,dest='zh-CN').text
        cn_summary = fix(cn_summary,0)
        cn_affected = "Debian Linux上的"+affected_app+"软件。"
        cn_affected = fix(cn_affected,0)
        cn_solu = TransSolu(translator,en_solu)

        name = driver.find_element_by_name("vul_name_cn")
        summary = driver.find_element_by_name("desc_cn_summary")
        affected = driver.find_element_by_name("desc_cn_affected")
        solu = driver.find_element_by_name("solu_cn")

        name.clear()
        summary.clear()
        affected.clear()
        solu.clear()

        name.send_keys(cn_name)
        summary.send_keys(cn_summary)
        affected.send_keys(cn_affected)
        solu.send_keys(cn_solu)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
        SaveCounter = SaveCounter + 1
        print("成功保存一条！已经成功保存 "+str(SaveCounter)+" 条。")
    
    
    #8 Debian
    elif "Debian Security Advisory" in data:
        en_name = re.findall(r"\"vul_name\":\"(.*?)\"",data)[0]
        en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
        en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
        en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]
        if " - security update" in en_name:
            affected_app = re.findall(r"(.*?) on .*?",en_affected)[0]
        else:
            affected_app = re.findall(r"\((.*?)\)",en_name)[0]

        cn_name = translator.translate(en_name,dest='zh-CN').text
        cn_name = cn_name.replace("安全咨询"," 安全公告 ")
        cn_name = cn_name.replace("安全通报"," 安全公告 ")
        cn_summary = translator.translate(en_summary,dest='zh-CN').text
        cn_summary = fix(cn_summary,0)
        #if "crafted" in en_summary:
		#	cn_summary = cn_summary.replace("特制的","特定构造的")
        cn_affected = "Debian Linux上的"+affected_app+"软件。"
        cn_affected = fix(cn_affected,0)
        cn_solu = TransSolu(translator,en_solu)

        name = driver.find_element_by_name("vul_name_cn")
        summary = driver.find_element_by_name("desc_cn_summary")
        affected = driver.find_element_by_name("desc_cn_affected")
        solu = driver.find_element_by_name("solu_cn")

        name.clear()
        summary.clear()
        affected.clear()
        solu.clear()

        name.send_keys(cn_name)
        summary.send_keys(cn_summary)
        affected.send_keys(cn_affected)
        solu.send_keys(cn_solu)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
        SaveCounter = SaveCounter + 1
        print("成功保存一条！已经成功保存 "+str(SaveCounter)+" 条。")
    
    
    #9 FreeBSD Ports
    elif "FreeBSD Ports" in data:
        en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]

        cn_summary = "远程主机缺少参考公告中公布的系统更新。"
        if "VendorFix" in en_solu:
            cn_solu = "软件厂商已经发布修复补丁，请阅读参考链接安装相关补丁。"
        elif "Update your system with" in en_solu:
            cn_solu = "安装适当的补丁或升级软件来更新你的系统。"
        else:
            pass

        summary = driver.find_element_by_name("desc_cn_summary")
        solu = driver.find_element_by_name("solu_cn")

        summary.clear()
        solu.clear()

        summary.send_keys(cn_summary)
        solu.send_keys(cn_solu)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-lg']").click()
        SubmitCounter = SubmitCounter + 1
        print("成功提交一条！已经成功提交 "+str(SubmitCounter)+" 条已适配格式。")
    
    
    #10 Gentoo
    elif "Gentoo Security Advisory" in data:
        en_name = re.findall(r"\"vul_name\":\"(.*?)\"",data)[0]
        en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
        en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]

        cn_name = en_name.replace("Security Advisory"," 安全公告 ")
        if "Local Security Checks" in en_summary:
            cn_summary = en_summary.replace("Local Security Checks","本地安全检查")
        elif "The remote host" in en_summary:
            affected_app = re.findall(r"\((.*?)\)",en_name)[0]
            cn_summary = "远程主机缺失"+affected_app+"软件包的更新版本。"
        else:
            pass
        cn_summary = fix(cn_summary,0)
        if "users should upgrade" in en_solu:
            affected_app = re.findall(r"\((.*?)\)",en_name)[0]
            line = "所有"+affected_app+"用户须升级至最新版本："
            cn_solu = re.sub(r"All .*?:",line,en_solu)
        elif "Update the affected" in en_solu:
            cn_solu = "更新受影响的软件包至最新可用版本。"
        else:
            pass

        name = driver.find_element_by_name("vul_name_cn")
        summary = driver.find_element_by_name("desc_cn_summary")
        solu = driver.find_element_by_name("solu_cn")

        name.clear()
        summary.clear()
        solu.clear()

        name.send_keys(cn_name)
        summary.send_keys(cn_summary)
        solu.send_keys(cn_solu)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
        SaveCounter = SaveCounter + 1
        print("成功保存一条！已经成功保存 "+str(SaveCounter)+" 条。")
        
        
    #11 Mandriva
    elif "Mandriva Update for" in data:
        APPandID = re.findall(r"\"Mandriva Update for (.*?)\"",data)[0]

        affected_app = APPandID.split(" ",1)[0]
        ref = APPandID.split(" ",1)[1]
        cn_vul_name = "Mandriva 安全更新 "+ref

        en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
        en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
        system = re.findall(r"\"desc_affected\":\".*? on (.*?)\"",data)[0]
        en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]

        name = driver.find_element_by_name("vul_name_cn")
        summary = driver.find_element_by_name("desc_cn_summary")
        affected = driver.find_element_by_name("desc_cn_affected")
        solu = driver.find_element_by_name("solu_cn")

        name.clear()
        name.send_keys(cn_vul_name)

        cn_summary = "远程主机缺失"+affected_app+"软件包的更新版本。"
        cn_summary = fix(cn_summary,0)
        summary.clear()
        summary.send_keys(cn_summary)
        time.sleep(0.2)
    
        cn_affected = system+"上的"+affected_app+"软件。"
        cn_affected = fix(cn_affected,0)
        affected.clear()
        affected.send_keys(cn_affected)

        cn_solu = TransSolu(translator,en_solu)
        solu.clear()
        solu.send_keys(cn_solu)
        time.sleep(0.2)
        
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
        SaveCounter = SaveCounter + 1
        print("成功保存一条！已经成功保存 "+str(SaveCounter)+" 条。")
        

    # 未适配
    else:
        en_name = re.findall(r"\"vul_name\":\"(.*?)\"",data)[0]
        en_summary = re.findall(r"\"desc_summary\":\"(.*?)\"",data)[0]
        en_affected = re.findall(r"\"desc_affected\":\"(.*?)\"",data)[0]
        en_impact = re.findall(r"\"desc_impact\":\"(.*?)\"",data)[0]
        en_solu = re.findall(r"\"solu\":\"(.*?)\"",data)[0]

        # Service Pack改SP
        en_name = re.sub(r"Service Pack ","SP",en_name)
        # 尝试从en_name中去除漏洞名称里的日期
        en_name = re.sub(r" - .*?\d+","",en_name)
        en_affected = re.sub(r"Service Pack ","SP",en_affected)
        cn_name = translator.translate(en_name,dest='zh-CN').text
        # 尝试从cn_name中去除漏洞名称里的日期（日期格式太乱了，多加一层过滤）
        cn_name = fix(cn_name,1)
        cn_summary = translator.translate(en_summary,dest='zh-CN').text
        cn_summary = fix(cn_summary,0)
        cn_affected = translator.translate(en_affected,dest='zh-CN').text
        cn_affected = fix(cn_affected,0)
        cn_impact = translator.translate(en_impact,dest='zh-CN').text
        cn_impact = re.sub(r"成功利用.*?远程攻击者","远程攻击者可能利用此漏洞",cn_impact)
        cn_impact = re.sub(r"成功利用.*?攻击者","攻击者可能利用此漏洞",cn_impact)
        cn_impact = fix(cn_impact,0)
        cn_solu = TransSolu(translator,en_solu)

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

        # 点击保存按钮，打印成功信息
        driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()
        SaveCounter = SaveCounter + 1
        print("这一条由Google Translate翻译。")
        print("成功保存一条！已经成功保存 "+str(SaveCounter)+" 条。")


if __name__ == "__main__":
    print("Waiting for user")
    driver = login()
    cookie = get_cookie(driver)
    print("User logged in. Begin translation.")
    # 第三个参数是循环次数，可手动修改
    Translate(driver,cookie,100)
