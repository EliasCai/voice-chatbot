import urllib
import urllib.request

# import  urllib2, sys
import ssl

# client_id 为官网获取的AK， client_secret 为官网获取的SK


# document
API_KEY = 'rhZwpGKWrGyA6bSCGjdqxVoO'
SECRET_KEY = 'mHPam5b4GtgFKPITraiFxxzLU7S5ONuX'


host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s' % (API_KEY, SECRET_KEY)
request = urllib.request.Request(host)
request.add_header('Content-Type', 'application/json; charset=UTF-8')
response = urllib.request.urlopen(request)
content = response.read()
if (content):
    print(type(content))#<class 'bytes'>
    print(content)
content_str=str(content, encoding="utf-8")
###eval将字符串转换成字典
content_dir = eval(content_str)
access_token = content_dir['access_token']
print(access_token)
