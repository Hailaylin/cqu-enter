
# cqu-enter v1

一个能够简化入校预约的小程序，思路是模拟“平安重大”里面入校预约登录、填写信息、提交申请的流程，验证码用手机程序“通知滤盒”进行Webhook转发短信内容。

经试验，运行较长时间可用。缺点是每次都要手动ctrl+c结束程序，不够自动化。
验证码用百度的


## 1 配置
编辑```config.yml```文件，然后填写个人信息，配置服务器端口，默认```999```。

配置收验证码的手机号，建议双卡用户用1卡或者主卡，个人使用的话2卡的短信进不了通知滤盒，很奇怪。

默认打卡时间是当天，设置time下的today为false后自定义入校时间和出校时间

### 百度验证码识别API配置
1. https://ai.baidu.com/ 注册登录
2. 到应用列表创建AI应用 https://console.bce.baidu.com/ai/#/ai/ocr/app/list
选应用类别选```文字识别```，文档看 https://cloud.baidu.com/doc/OCR/s/1k3h7y3db
3. 拿到应用的```API_KEY```和```SECRET_KEY```
4. 写入配置文件


## 2. 部署地点
1. 部署在云服务器上，一台一年也就61rmb
2. 本地部署，需要frp把本地端口进行内网穿透到公网ip
总之，需要一个端口能被公网访问到，收验证码

## 3. 配置手机收码转发
1. 下载```通知滤盒```，初体验免费，一个月收费，丰俭由人
2. 设置通知内容，过滤APP为“信息”，然后关键字为```验证码是:```，```,请妥善保存```一共两个。
3. 添加webhook规则，设置```Request method```为```POTST```
4. 设置Body为
````json
{
	"title": "{android.title}",
 	"text": "{android.text}",
 	"app": "{filterbox.field.PACKAGE_NAME}"
}
````
重要的是```"text": "{android.text}",```这一行，其余可以省略。

然后可以点模拟测试，如果以前接收过预约短信，应该能显示出来
5. 配置URL
```http://[IP]:[PORT]/cqusms```
IP和PPORT换成自己的服务器IP和端口PORT，例如
```http://hailay.site:999/cqusms```

## 4. 运行
clone本项目后，进入项目文件夹执行

````shell
sudo apt install python3
python3 --version
pip3 install flask
python3 cqu-enter.py
````
运行后会出现```TypeError: 'NoneType' object is not subscriptable```，但是日志往上拉出现```INFO in cqu-enter: 申请成功!关闭程序```就是申请成功了。

## 注意事项
1. 默认只预约了AB校区，要加的话在apply_data的oospCampus里面添加"C"校区。
2. 本程序只用于方便个人入校预约使用，请勿滥用，仅供学习Python使用，侵删。
3. 本程序可用多线程技术改进，解决关闭不了flask的问题，只是没心神改了，能用就行。
4. 可进一步改进成定时自动预约。
5. 有问题提issue
5. 欢迎大神改进程序呜呜呜，自己能用就不想改了
