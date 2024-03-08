# coding=utf-8

import sys
import json
import base64
import requests
# import uuid
import time
from time import sleep
import os
import yaml

# 先实例化一个对象 保持请求的session
session = requests.Session()
header = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
    'Referer':'http://mobilereserve.cqu.edu.cn/',
    'Host':'mobilereserve.cqu.edu.cn',
    'Origin': 'http://mobilereserve.cqu.edu.cn',
    'Proxy-Connection':'keep-alive',
    'Accept':'application/json, text/plain, */*',
    'Authorization':'null',
    'Accept-Encoding':'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}
session.headers.update(header)

# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# 防止https证书校验不正确
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

API_KEY = ''

SECRET_KEY = ''


OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"


"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'




"""
    获取token
"""
def fetch_token():
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()


    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

"""
    读取文件
"""
def read_file(image_path):
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()


"""
    调用远程服务
"""
def request_baidu(url, data):
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)

"""
1.1 获取验证码的图片
"""
def getCAPTCHA_img():
    try:
        response = session.get('http://mobilereserve.cqu.edu.cn/mobapi/phoneLogin/getKaptcha')
        json_data = json.loads(response.text)
        # print(json_data)
        if (json_data['code']==200):
            return json_data['data']
    except:
        print("获取验证码失败")

"""
1.2 获取验证码的文字
"""
def getCAPTCHA_code_4Baidu(img_base64):
    
    # 获取access token
    token = fetch_token()
    # 拼接通用文字识别高精度url
    image_url = OCR_URL + "?access_token=" + token
    text = ""
    # 读取测试图片
    # file_content = read_file('./text.jpg')
    img_data = img_base64
    # 调用文字识别服务
    # result = request(image_url, urlencode({'image': base64.b64encode(file_content)}))
    result = request_baidu(image_url, urlencode({'image': img_data}))
    # 解析返回结果
    result_json = json.loads(result)
    # 返回结果
    print(result_json)
    # 转换小写
    code_lower = 'aaaa'
    try:
        code_lower = result_json['words_result'][0]['words'].lower()
    except Exception as e:
        print(e)

    print(code_lower)
    return code_lower


"""
2.1 发送短信验证码
"""
def send_shortMsg(phone_num, CAPTCHA_code, uuId):

    URLbase = "http://mobilereserve.cqu.edu.cn/mobapi/phoneLogin/getCode/"
    # uuid4_data = uuid.uuid4().hex
    URL = URLbase + phone_num + '/' + CAPTCHA_code + '/' + uuId
    response = session.get(url=URL)
    json_data = json.loads(response.text)
    print(json_data)
    print(session.cookies)
    return json_data



"""
2.2 webhook 等待接受验证码

"""
import json
from flask import Flask,request
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

"""3. 登录
"""
def login(six_code,phone_num):
    URL = "http://mobilereserve.cqu.edu.cn/mobapi/phoneLogin/login"
    # req_data = {"code":{six_code},"phoneNumber":{phone_num}}
    # 查看申请头信息
    dict_test = {}
    dict_test['code']=six_code
    dict_test['phoneNumber']=phone_num
    app.logger.info(session.headers)
    re = session.post(url=URL,json=dict_test)
    re_json = json.loads(re.text)
    app.logger.info("登录返回信息：")
    app.logger.info(re_json)
    app.logger.info(session.cookies)
    # 更新头信息
    # {"code":200,"msg":"成功","data":{"userName":"12312341234","userAuthenticationNumber":"18057686814","token":"Bearer eyJhbGciOiJIUzUxMiJ9.eyJqdGkiOiI5ODE0YmZkZTIwNDQ0YWZiOTIxZjg0Zjk0Njg0YzBlZiIsImF1dGhvcml0aWVzIjpbXX0.9aNpK6kOv801ZWMRhoMErhJ-V2vNVLNemURiBNW_3bGeKMg8mAWCJMq3UwmLUJr43_IPXSAPfUzTjnIhpii2cQ","permissions":["outSchool:add","/outSchoolAppointment","/admissionappointment"],"amongSet":[],"loginIdentify":"1","channel":["0","1","2"],"sflbdm":null}}
    session.headers.update({'Authorization':re_json['data']['token']})
    app.logger.info(session.headers)
    
    if (re_json['code']==200):
        app.logger.info("登录成功!")
        notice_re = session.get(url="http://mobilereserve.cqu.edu.cn/mobapi/noticeApi/noticeOneQuery")
        if (json.loads(notice_re.text)['code']==200):
            app.logger.info("更换JSESSIONID成功!")
            return True
        else:
            app.logger.info("更换JSESSIONID失败!")
    else:
        app.logger.info("登录失败!")

"""4.申请
"""
def apply():
    # 总申请信息 校区为AB校区    
    apply_data = {
        "outSchoolInfoAddDtos":[
            {
                "ooiCarNumber":"",
                "ooiIdNumber":{IdNumber},
                "ooiName":{name},
                "ooiPhone":{phone_num},
                "ooiSort":1,
                "vehicleTypeId":"null",
                "vehicleType":"",
                "documentType":"居民身份证",
                "documentTypeMark":"1"
            }
        ],
        "oospCampus":[
            "A",
            "B"
        ],
        "oospChannel":"2",
        "oospIntoSchoolReason":{into_reason},
        "oospIntoSchoolTime":{into_time},
        "oospLeaveSchoolTime":{leave_time},
        "oospUserCode":{phone_num}
    }
    # 序列化必需品
    apply_data['oospIntoSchoolTime'] = into_time
    apply_data['oospLeaveSchoolTime'] = leave_time
    apply_data['oospIntoSchoolReason'] = into_reason
    apply_data['oospUserCode'] = phone_num
    apply_data['outSchoolInfoAddDtos'][0]['ooiPhone'] = phone_num
    apply_data['outSchoolInfoAddDtos'][0]['ooiIdNumber'] = IdNumber
    apply_data['outSchoolInfoAddDtos'][0]['ooiName'] = name
    
    URL = "http://mobilereserve.cqu.edu.cn/mobapi/reserveOutSchoolPersonal/add"
    re = session.post(url=URL, json=apply_data)
    re_json = json.loads(re.text)
    app.logger.info("申请返回信息：")
    app.logger.info(re_json)
    app.logger.info(session.cookies)

    if (re_json['code']==200):
        app.logger.info("申请成功!关闭程序")
        print("申请成功!关闭程序")
        sys.exit()  # 添加退出语句
        raise SystemExit()
        os.kill()
    else:
        app.logger.info("申请失败!")

@app.route("/cqusms",methods=['POST'])
def event():
    json_data = json.loads(request.data,)
    # print(request.data)
    # 程序收到验证码就会来到这
    # print(json_data)
    app.logger.info(json_data)
    # text = "【重庆大学】您登录重庆大学入校预约系统的验证码是:539918,请妥善保管!"
    text = json_data['text']
    # print(text.find(':'))
    index = text.index(':')
    six_code = text[index+1:index+7]

    # 输出测试

    print(six_code)
    app.logger.info("验证码:" + six_code)

    # 3.登录
    login(six_code=six_code,phone_num=phone_num)
    
    # 4.申请
    apply()

    return json_data

def wait_short_6code():
    app.run(port = config['port'],host="0.0.0.0",debug=True,use_reloader=False)




def read_yaml_config(file_path):
    with open(file_path, 'r') as stream:
        try:
            config_data = yaml.safe_load(stream)
            return config_data
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")



if __name__ == '__main__':
    CAPTCHA_code = ''   # 验证码4位
    shortMsg_code = ''  # 短信验证码

    # 例子：读取配置文件，默认 config.yml，可以修改成自己的文件名或者直接改config.yml
    config_path = 'config.yml'
    config = read_yaml_config(config_path) # 配置文件字典输出

    # 百度验证码识别
    API_KEY = config['API_KEY']
    SECRET_KEY = config['SECRET_KEY']

    # 配置电话号码
    phone_num = config['phone_num']

    if config['time']['today'] == True:
        # 设置时间为现在开始的完整一天
        one_date_sec = 24*60*60
        into_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        current_date = time.strftime('%Y-%m-%d', time.localtime())
        leave_time = current_date + ' 23:59:59'
    else:
        # 进入时间
        into_time = config['time']['into_time']
        # 出校时间
        leave_time = config['time']['leave_time']

    # 入校理由
    into_reason = config['into_reason']
    # 个人信息
        # 身份证号
    IdNumber = config['IdNumber']
        # 姓名
    name = config['name']

    # 1. 获取正确的4位验证码并发送短信
    counter = 0

    ### TODO 短信验证码每天只能发5次
    shortMsg_limitted = 5
    while counter < shortMsg_limitted:
        counter = counter + 1
        # 尝试5次获取验证码        
        CAPTCHA_img_data = getCAPTCHA_img()
        CAPTCHA_code = getCAPTCHA_code_4Baidu(CAPTCHA_img_data['imgCode'])
        status = send_shortMsg(phone_num = phone_num, CAPTCHA_code=CAPTCHA_code, uuId=CAPTCHA_img_data['uuId'])
        if (status['code']==500):
            print("短信验证码识别发送失败")
            sleep(5)
            continue
        elif (status['code']==200):
            print("短信验证码识别发送成功")
            break

    # 2. 获取短信验证码(阻塞，收到码后不会停止运行。。)
    wait_short_6code()
