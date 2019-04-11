from selenium import webdriver
import time
import requests
import re


def login():

    username = "mou mou mou"
    password = "6666"
    url = "http://218.94.157.126:9328"
    driver = webdriver.Chrome()
    driver.get(url)
    driver.find_element_by_id("cam-user-login-username").clear()
    driver.find_element_by_id("cam-user-login-username").send_keys(username)
    driver.find_element_by_id("LAY-user-login-password").clear()
    driver.find_element_by_id("LAY-user-login-password").send_keys(password)

    # 输入验证码的时长，输入完成后点击登录即可，脚本将自动完成遍历翻译
    # time.sleep(10)
    # 根据刘骐彰的建议，改成当driver识别到当前url发生变化时，程序即可开始。
    while driver.current_url == "http://218.94.157.126:9328/login":
    # 空循环，起等待的效果
    	pass
    	
    return driver

# selenium的cookie和requests所需的cookie不一样（selenium的cookie中有不必要的信息），因此需要重新设置格式。
def get_cookie(driver):
    raw_cookie = driver.get_cookies()[0]
    cookie = {}
    cookie[raw_cookie['name']] = raw_cookie['value']
    return cookie

# 目前设计了Fedora和CentOS
# interaction用于指定遍历的条数，自行按需要输入值
def Translate(driver,cooki,iteraction):
    # 点击“规则翻译”
    driver.find_element_by_class_name("layui-nav-child").find_element_by_tag_name("dd").click()
    number = 0
    FedCounter = 0
    CenCounter = 0
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
        	# 从data里面找到"vul_name":"CentOS Update for xxx CESA-2009:0420 centos4 i386"并取出xxx CESA-2009:0420 centos4 i386"，存入APPandID
            APPandID = re.findall(r"\"CentOS Update for (.*?)\"",data)[0]
            # 将APPandID里的内容按空格分成两段，取第一段为affected_app，即xxx，后面的就是版本号了，存在ref里面
            affected_app = APPandID.split(" ",1)[0]
            ref = APPandID.split(" ",1)[1]
            # 这里跟上面的FEDORA是一样的，虽然前面没有加匹配识别字段"desc_affected"，但是还是能靠"on"找到了影响的系统。
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
            print("不是FEDORA条目,也不是CentOS条目。进度：{0}/{1}".format(str(number+1),iteraction))
            driver.find_element_by_css_selector("[class='layui-btn layui-btn-normal layui-btn-lg']").click()

        number = number + 1

        # 设置访问周期，之前设置成1因为频率太大被服务器禁ip了
        time.sleep(2)
    print("任务完成啦，本次共翻译{0}条FEDORA，{1}条CentOS，还有{2}条未翻译的内容在“翻译列表”栏内".format
        (FedCounter,CenCounter,(iteraction-FedCounter-CenCounter)))


if __name__ == "__main__":
    driver = login()
    cookie = get_cookie(driver)
    Translate(driver,cookie,100)