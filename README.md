# YixunTranslate

=====Thank all contributors to this script!=====

##Changelog:

###1.1

1.适配Fedora和CentOS；

2.while循环等待用户登入。

---

###2.0.2

1.新增Google翻译插件，依赖于googletrans库，用于通用翻译；

2.有效适配Fedora和CentOS。

---

###3.10.5-alpha

1.翻译单独写一个函数，模块化；

2.目前适配Ubuntu、SUSE、Local Check等10种格式；

3.去除名称中的日期（测试中）；

4.防止输出“\n”；

5.其他的bug修复。

---

###3.10.6-alpha

1.修复了fix()函数中的一些错误，现在可以替换部分"installed with"翻译成“主机随……安装”的句子了；

2.（部分）修复了输出"\\/"或"\n"的问题；

3.修复了SUSE模块影响版本输出异常的问题。

---

###3.10.7-alpha

1.“将结果设置为KB”替换为“将结果保存到知识库”；

2.德文“配置核查”条目保存改为直接提交；

3.SUSE条目保存改为直接提交；

4.Ubuntu/RedHat条目保存改为直接提交；

5.FreeBSD条目保存改为直接提交；

6.修复了FreeBSD条目的判断条件错误；

7.修复了区分Ubuntu与RedHat的变量判断错误；

8.修复了Gentoo条目影响版本的正则表达式错误；

9.修复了Debian条目影响版本的正则表达式错误；

10."Please Install the Updated Packages"替换为预设字符串；

11."xxx发行版(stretch)"保持不翻译（测试中）。

*运行了一遍，100条里直接提交的有54条，保存的有46条，基本都是看一眼或者一些小修改就可以提交的~*



##目前存在的问题

日期格式太乱，很多没办法去掉

"\n"输出是去掉了，但是该换行的地方没换行
