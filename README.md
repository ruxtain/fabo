# fabo
法宝·仿知乎便捷法条查询工具<br>
项目地址：https://github.com/ruxtain/fabo

配置
===
首先创建虚拟环境并添加依赖：
```
$ virtualenv your-env
$ source your-env/bin/activate
$ pip -r install requirements.txt
```

elasticsearch
===
```
brew install elasticsearch
# 安装后命令行启动，该文本搜索服务将会监听 9200 端口
elasticsearch
```
以上是 macOS 的安装方式，其他安装方式请看 [这里](http://django-haystack.readthedocs.io/en/master/installing_search_engines.html#elasticsearch)。

启动
===
```
python manage.py runserver
```

demo
===
![demo image](https://github.com/ruxtain/fabo/blob/master/demo.png)
