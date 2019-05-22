from flask import Flask, request, abort, render_template
import hashlib
import xmltodict, time

# 常量
# 微信的token令牌
WECHAT_TOKEN = "cxsj16272202"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return "index page."

@app.route("/wx", methods=["GET", "POST"])
def wechat():
    """对接微信公众号服务器"""
    # 接收微信服务器发送的参数
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")

    if not all([signature, timestamp, nonce]):
        abort(400)

    # 按照微信的流程进行计算签名
    li = [WECHAT_TOKEN, timestamp, nonce]
    # 排序
    li.sort()
    # 拼接字符串
    tmp_str = ''.join(li)
    # 进行sha1加密, 得到正确的签名值
    sign = hashlib.sha1(tmp_str).hexdigest()
    # 将自己计算的签名值与请求的签名参数进行对比，如果相同，则证明请求来自微信服务器
    if sign != signature:
        # 表示请求不是微信发的
        abort(403)
    else:
        # 表示是微信发送的请求
        if request.method == "GET":
            # 表示是第一次接入微信服务器的验证
            echostr = request.args.get("echostr")
            if not echostr:
                abort(404)
            return echostr
        elif request.method == "POST":
            # 表示微信服务器转发消息过来
            xml_str = request.data
            if not xml_str:
                abort(400)

            # 对xml字符串进行解析
            xml_dict = xmltodict.parse(xml_str)
            xml_dict = xml_dict.get("xml")

            # 提取消息类型
            msg_type = xml_dict.get("MsgType")

            if msg_type == "text":
                # 表示发送的是文本消息
                # 构造返回值，经由微信服务器回复给用户的消息内容
                resp_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": "taogang say:" + xml_dict.get("Content")
                    }
                }
            else:
                resp_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": "Dear I Love you so much"
                    }
                }
            # 将字典转换为xml字符串
            resp_xml_str = xmltodict.unparse(resp_dict)
            # 返回消息数据给微信服务器
            return resp_xml_str


if __name__ == '__main__':
    app.run(port=8007, debug=True)
