import feedparser
import re
import notify
import requests
import json

def FCMpush(t,c,u):
    for k in push_config:
    if os.getenv(k):
        v = os.getenv(k)
        push_config[k] = v
    """
    Push Notification API 基于xdroid.net的接口 google play可下载
    """
    if not push_config.get("FCM_KEY"):
        print("FCM 服务的 FCM_KEY 未设置!!\n取消推送")
        return
    print("FCM 服务启动")
    
    url = 'http://xdroid.net/api/message'
    data = {"k": {push_config.get("FCM_KEY")},"title": t,"content": c,"u": u}
    response = requests.post(url, data=json.dumps(data)).json()

    if response.get("StatusCode") == 0:
        print("FCM 推送成功！")
    else:
        print("FCM 推送失败！错误信息如下：\n", response)
        
#删除多余html标签和超过2048字节数的字
def delhtml(t):
    pattern = re.compile(r'<[^>]+>',re.S)
    nohtml = pattern.sub('', t)

    #最大微信推送可传输字节数2048 太多信息导致信息流太长 一个汉字占2字节
    if len(nohtml) > 512:
        return '\n文章过长请查看原文'
    else:
        return '\n'+nohtml

#获取最新内容
def GetNewRSS(url):
    f=feedparser.parse(url)
    for post in f.entries:
        oldrss=open('oldrss',mode='a+')

        #读取之前的rss
        with open("oldrss") as file:
            old = file.read()
        #检查文章链接是否存在如果不存在则发送
        if not post.link in old:
            #打印文章标题
            print(f.feed.title,post.title)
            #<a 超链接套住标题 /a> 文章发布时间 删除html转义了的文章内容
            notify.send('<a href="'+post.link+'">'+f.feed.title+' - '+post.title+'</a>\n'+post.published,delhtml(post.description))
            #标题无链接notify.send(f.feed.title+post.title,delhtml(post.description),post.link)
            FCMpush(f.feed.title+post.title,delhtml(post.description),post.link)
            #写入oldrss记录
            oldrss.writelines([f.feed.title,'  ',post.link,'  ',post.title,'\n'])
        oldrss.close()

if __name__ == '__main__':
    #订阅地址在rss_sub文件，每行填一个网址。

    #读取rss_sub文件，获取订阅地址。并逐行订阅
    #无rss时更新记录 添加记录 保证action能通过
    oldrss=open('oldrss',mode='a+')
    oldrss.writelines(['1\n'])
    oldrss.close()
    
    for line in open("rss_sub"):
        GetNewRSS(line)
