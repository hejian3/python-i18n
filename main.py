# coding:utf-8

import os.path
import sys

import threading
import time
import traceback
import json
import tornado.ioloop
import tornado.web
from tornado.web import Finish, MissingArgumentError, RequestHandler
from tornado.locale import CSVLocale, load_translations, set_default_locale, get_supported_locales


class BaseHandler(RequestHandler):
    """
       调用顺序
       set_default_headers()
       initialize()
       prepare()
       HTTP方法,get,post
       set_default_headers()
       write_error()
       on_finish()
   """

    def translate(self, msg: str):
        try:
            return CSVLocale.get_closest(self.request.headers.get("Accept-Language")).translate(msg)
        except Exception:
            return msg

    def success(self, chunk=""):
        """
        success和error方法是用来格式化返回的
        :param chunk: str, dict, list, int
        """
        data = {
            "success": True,
            "code": 0,
            "msg": self.translate("成功"),
            "data": chunk,
        }
        self.request.response = data
        self.write(data)

    def error(self, promt: str = "", code: str = "0"):
        """
        :param code: 错误类型
        :param promt: 错误提示语句
        :return:
        """
        self.request.response = {
            "success": True,
            "code": code,
            "msg": self.translate(promt),
            "data": {}
        }  # 用于性能日志统计
        self.write({
            "success": False,
            "code": code,
            "msg": self.translate(promt),
            "data": {}
        })

    def error_false(self, promt: str = "", code: str = "0"):
        """
        :param code: 错误类型
        :param promt: 错误提示语句
        :return:
        """
        self.request.response = {
            "success": False,
            "code": code,
            "msg": self.translate(promt),
            "data": {}
        }  # 用于性能日志统计
        self.write({
            "success": False,
            "code": code,
            "msg": self.translate(promt),
            "data": {}
        })

    def write_error(self, status_code, **kwargs) -> None:
        """
        全局捕获异常的地方,一般不修改
        """
        self.set_status(200)
        etype, value, _ = kwargs.get("exc_info")
        if etype == tornado.web.HTTPError:
            promt, code = json.dumps(value.messages["json"]), "-1"
            data = {
                "success": False,
                "code": code,
                "msg": self.translate(promt),
                "data": {}
            }
            self.request.response = data
            self.finish(data)
        else:
            error_list = traceback.format_exception(*kwargs.get("exc_info"))
            error_str = "\n".join(error_list)
            data = {
                "success": False,
                "code": "-1",
                "msg": self.translate("请求接口失败"),
                "data": error_str
            }
            self.request.response = data
            self.finish(data)


class HelloHandler1(BaseHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument('name', 'World')
        self.success(self.translate("你好") +" " +  name)


class HelloHandler2(BaseHandler):
    def get(self, *args, **kwargs):
        name = self.get_argument('name', 'World')
        self.success(self.translate("你好{0}").format(name))


class ErrorHandler(BaseHandler):
    def get(self, *args, **kwargs):
        raise Exception('error')


if __name__ == "__main__":
    load_translations("./i18n")
    set_default_locale("zh_CN")  # 默认语言, 它不需要翻译文件, 也就是说代码语言
    print("支持的国际化语言:", get_supported_locales())
    loop = tornado.ioloop.IOLoop.current()
    app = tornado.web.Application([(r'/hello1', HelloHandler1),
                                   (r'/hello2', HelloHandler2),
                                   (r'/error', ErrorHandler)])
    app.listen(8080)
    loop.start()
