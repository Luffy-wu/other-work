import os
import sys
import inspect


def getdir():
    path = sys.path[0]
    if os.path.isdir(path):
       return path
    elif os.path.isfile(path):
       return os.path.dirname(path)
    return '/home/weibospider/SinaCrawler'


def printinfo(value):
    print "call from " + inspect.stack()[1][1] + "'s function " + inspect.stack()[1][3] + " at line " +\
          str(inspect.stack()[1][2]) + ":" + str(value)


HOME_DIR = getdir()

ATTRS={
    "CURRENT_ITEM_INDEX": 0,
    "CURRENT_GU8_INDEX": 0
}

SINA_USERS = {
    "qiao8miku@sina.cn": "qiao1rui",
    "hqdandan1@163.com": "Q1w2e3r4"
}

GU8_USERS = {
    '13469981619': 'qiao1rui'
}


def get_user():
    if ATTRS["CURRENT_ITEM_INDEX"] < len(SINA_USERS):
        result = [SINA_USERS.keys()[ATTRS["CURRENT_ITEM_INDEX"]], SINA_USERS.get(SINA_USERS.keys()[ATTRS["CURRENT_ITEM_INDEX"]])]
        ATTRS["CURRENT_ITEM_INDEX"] = divmod(ATTRS["CURRENT_ITEM_INDEX"] + 1, len(SINA_USERS))[1]
        return result



def get_gu8_user():
    if ATTRS["CURRENT_GU8_INDEX"] < len(GU8_USERS):
        return [GU8_USERS.keys()[ATTRS["CURRENT_GU8_INDEX"]], GU8_USERS.get(GU8_USERS.keys()[ATTRS["CURRENT_GU8_INDEX"]])]
    ATTRS["CURRENT_GU8_INDEX"] = divmod(ATTRS["CURRENT_GU8_INDEX"] + 1, len(GU8_USERS))[1]
