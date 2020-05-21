#-*- coding: utf-8 -*-

# byte to Human Readable convert - MAX : TB
def hbytes(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.2f%s" % (num, x)
        num /= 1024.0
    return "%3.2f%s" % (num, 'TB')


def dequote(text):
    if (text[0] == text[-1]) and text.startswith(("'", '"')):
        return text[1:-1]
    return text


def GetDSMMajorVersion():
    parseVars = {}
    with open("/etc/VERSION") as versionFile:
         for line in versionFile:
             key, value = line.partition("=")[::2]
             parseVars[key.strip()] = dequote(value.strip())

    return parseVars['majorversion']


