# YixunTranslate

=====Thank all contributors to this script!=====

## Changelog:

### 1.1

1. 适配Fedora和CentOS；

2. while循环等待用户登入。


### 2.0.2

1. 新增Google翻译插件，依赖于googletrans库，用于通用翻译；

2. 有效适配Fedora和CentOS。


### 3.10.5-alpha

1. 翻译单独写一个函数，模块化；

2. 目前适配Ubuntu、SUSE、Local Check等10种格式；

3. 去除名称中的日期（测试中）；

4. 防止输出“\n”；

5. 其他的bug修复。


### 3.10.6-alpha

1. 修复了fix()函数中的一些错误，现在可以替换部分"installed with"翻译成“主机随……安装”的句子了；

2. （部分）修复了输出"\\/"或"\n"的问题；

3. 修复了SUSE模块影响版本输出异常的问题。


### 3.10.7-alpha

1. “将结果设置为KB”替换为“将结果保存到知识库”；

2. 德文“配置核查”条目保存改为直接提交；

3. SUSE条目保存改为直接提交；

4. Ubuntu/RedHat条目保存改为直接提交；

5. FreeBSD条目保存改为直接提交；

6. 修复了FreeBSD条目的判断条件错误；

7. 修复了区分Ubuntu与RedHat的变量判断错误；

8. 修复了Gentoo条目影响版本的正则表达式错误；

9. 修复了Debian条目影响版本的正则表达式错误；

10. "Please Install the Updated Packages"替换为预设字符串；

11. "xxx发行版(stretch)"保持不翻译（测试中）。

*运行了一遍，100条里直接提交的有54条，保存的有46条，基本都是看一眼或者一些小修改就可以提交的~*


### 3.11.0-alpha

1. 适配Mandriva条目；

2. "installed with"识别方式优化；

3. 可能会在之后的版本增加一些注释，提高代码可读性。


### 3.11.1-alpha

1. 修改了一些在终端的输出信息，优化输出视觉效果；

2. 搜索cn_name，进一步过滤日期（测试中）；

3. 修复了Mandriva条目判断条件错误；

4. 代码中增加了一些注释（陆续完善）；

5. 优化了fix函数，包括但不限于：

> "squeeze"和"stretch"正则表达式修改；
>
> "crafted"翻译为“特定构造的”（覆盖不完全）；
>
> "sanitize"翻译为“验证”（覆盖不完全）；
>
> "\\n"和"\\ /"过滤。


### 3.11.2-alpha

1. 修改了一些注释；

2. 修复了末尾添加句号功能的严重错误；

3. （似乎）彻底解决了"\\n"不换行的问题，是代码有个小错误。


### 3.11.3-alpha

1. fix函数增加了一个参数，用于防止在名称后面加上句号；

2. fix函数新增将以英文句号结尾的文字替换为中文句号；

3. TransSolu函数对翻译结果进行了进一步修正；

4. 现在才发现Debian条目也包含了两种格式，这个版本修复了这两种不同格式会导致affected_app获取错误的问题；

5. 修复了Gentoo条目的affected_app获取失败的问题。


### 3.11.4-alpha

1. 翻译API改成谷歌翻译国内版以解决众所周知的问题；

2. TransSolu函数替换"Workaround"字段；

3. 修复了Gentoo条目的一些小错误；

4. 增加了一些注释；

5. TransSolu函数忽略对网址的翻译（测试中）。


### 4.0-alpha

1. 以全新的json代替字符串解析，有望解决大量输出异常问题，后续逐步改进；

2. **注意：由于修改了字符串匹配语句，该版本所有条目均设为保存，后续代码检查无错误后恢复提交** ；

3. 其他的一些小修复；

4. 本来想有个4.1版本，通过OCR直接识别验证码输入，无需手动登录的，但是实测识别失败，而且就算做出来了也要依赖大量图像处理相关的第三方Python库（Tesseract，DIL等），还耗费大量精力，得不偿失，所以还是放弃了。

祝使用愉快~


### 3.11.5-alpha

1. fix函数新增了一些替换文字；

2. 优化了Fedora和CentOS条目的输出格式；

3. TransSolu函数修改了一些替换文字；

4. “特制的”替换成“特定构造的”（测试中）；

5. 其他一些已知问题的修复和改进。


### 3.11.5-beta

1. 第一个公测版，现支持7种固定格式的完全翻译（提交）、4种固定格式的不完全翻译（保存）和其他格式的谷歌翻译（保存）。


### 3.12.0-beta

1. 第一个公测版，现支持7种固定格式的完全翻译（提交）、4种固定格式的不完全翻译（保存）和其他格式的谷歌翻译（保存）；

2. 后台发送统计数据到MySql数据库，以便统计各个用户使用脚本翻译的条目数。


## 目前存在的问题

1. 日期格式太乱，很多没办法去掉；

2. ~~"\n"输出是去掉了，但是该换行的地方没换行；~~ 已解决！

3. 网址会翻译出来；

4. “[系统]上[版本]之前的[软件]版本”希望翻译成“[系统]上的[软件] [版本]之前的版本”。

## Hopefully... 

**fix：**

1. 英文逗号和英文括号改成中文的；

2. Common Vulnerabilities and Exposures projects翻译成CVE项目；

---

**DoTranslate：**

1. CentOS 安全更新 后面带具体版本的翻译写在前面，例：

> EN_NAME - *CentOS Update for thunderbird CESA-2015:1682 centos7* 
> 
> 现在的CN_NAME - *CentOS 安全更新 CESA-2015:1682 centos7（thunderbird）* 
> 
> 希望的CN_NAME - *CentOS7 安全更新 CESA-2015:1682（thunderbird）*

3. xxx Detection翻译成检测到xxx;

4. 

> EN_SUMMARY - *This host is missing an important security   update according to Microsoft KB3213630* 
> 
> 现在的CN_SUMMARY - *根据Microsoft KB3213630，此主机缺少重要的安全更新。* 
> 
> 希望的CN_SUMMARY - *根据Microsoft KB3213630，此主机缺少xxx软件的重要安全更新。* 
