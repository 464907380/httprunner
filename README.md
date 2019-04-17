环境部署
前提条件：已安装python3.6版本
关注：安装后可能出现python2和python并存的情况，部署步骤中python3 及 pip3开头的命令需替换为当前机器的python3版本执行关键字。
1、安装mysql数据库服务端(推荐5.7+),并设置为utf-8编码，创建相应HttpRunner数据库，设置好相应用户名、密码，启动mysql

2、修改:HttpRunnerManager/HttpRunnerManager/settings.py里DATABASES字典和邮件发送账号相关配置
 
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
 'NAME': 'HttpRunner', # 新建数据库名
 'USER': 'root', # 数据库登录名
 'PASSWORD': 'root1234', # 数据库登录密码
 'HOST': '127.0.0.1', # 数据库所在服务器ip地址
 'PORT': '3306', # 监听端口 默认3306即可
 }
}
……
EMAIL_SEND_USERNAME = '123@163.com' # 定时任务报告发送邮箱，支持163,qq,sina,企业qq邮箱等，注意需要开通smtp服务
EMAIL_SEND_PASSWORD = '123' # 邮箱密码

3、123，启动服务，访问：http://host:15672/#/ host即为你部署rabbitmq的服务器ip地址 username：guest、Password：guest, 成功登陆即可
service rabbitmq-server start

4、修改:HttpRunnerManager/HttpRunnerManager/settings.py里worker相关配置
 
djcelery.setup_loader()
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'
BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672//' if DEBUG else 'amqp://guest:guest@127.0.0.1:5672//'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TASK_RESULT_EXPIRES = 7200 # celery任务执行结果的超时时间，
CELERYD_CONCURRENCY = 1 if DEBUG else 10 # celery worker的并发数 也是命令行-c指定的数目 根据服务器配置实际更改 一般25即可
CELERYD_MAX_TASKS_PER_CHILD = 100 # 每个worker执行了多少任务就会死掉，我建议数量可以大一些，比如200

5、命令行窗口执行pip3 install -r requirements.txt 安装工程所依赖的库文件

6、命令行窗口切换到HttpRunnerManager目录 生成数据库迁移脚本,并生成表结构
python3 manage.py makemigrations ApiManager #生成数据迁移脚本 
python3 manage.py migrate #应用到db生成数据表

7、启动服务
python3 manage.py runserver 0.0.0.0:8000

8、启动worker, 如果选择同步执行并确保不会使用到定时任务，那么此步骤可忽略
nohup python3 manage.py celery -A HttpRunnerManager worker --loglevel=info > logs/worker.log & #启动worker 
 nohup python3 manage.py celery beat --loglevel=info > logs/beat.log &#启动定时任务监听器 
 nohup celery flower > /usr/local/httprunnerm_test/logs/flower.log &#启动任务监控后台

9、访问：http://localhost:5555/dashboard 即可查看任务列表和状态

10、浏览器输入：
    http://12.1.28.225:8000/api/register/  注册用户
    http://12.1.28.225:8000/api/login/   使用注册用户登录平台