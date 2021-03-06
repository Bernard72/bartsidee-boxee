#===============================================================================
# LICENSE Bartsidee Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================
import mc, bz2, binascii, os
from time import time
from urllib import FancyURLopener

#===============================================================================
# Global Variables
#===============================================================================
http = mc.Http()
http.SetUserAgent("Mozilla/5.0 (Windows; U; Windows NT 6.1; nl; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13")
http.SetHttpHeader('Accept', 'text/javascript, text/html, application/xml, text/xml, */*')

config = mc.GetApp().GetLocalConfig()

#===============================================================================
# Function to Retrieve and Cache a Http request
# Input:
# url - reqest url
# cacheTime - amount of time to keep the http result in the cache (seconds)
# xhr - make a xhr ajax request (boolean)
# params - parameters to POST if empty a GET request is executed
#===============================================================================


class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'

def FetchUrl(url, cacheTime=0):
    dbid = "cache_" + url
    if Cache(dbid+'{0}', cacheTime): return bz2.decompress(binascii.unhexlify(config.GetValue(dbid+'{1}')))
    myopener = MyOpener()
    page = myopener.open(url)
    data = page.read()

    if cacheTime != 0:
        config.Reset(dbid)
        config.Reset(dbid)
        config.PushBackValue(dbid, str(time()).split('.')[0])
        config.PushBackValue(dbid, binascii.hexlify(bz2.compress(data)))
    return data

#===============================================================================
# Function to determine if a cache is expired, returns a boolean
# Input:
# var - user agent variable as string
#===============================================================================
def UserAgent(var):
    http.SetUserAgent(var)

#===============================================================================
# Function to determine if a cache is expired, returns a boolean
# Input:
# dbid - variable ame id in database to check
# cacheTime - amount of time to keep the variable in the cache (seconds)
#===============================================================================
def Cache(dbid, cacheTime):
    if cacheTime == 0: return False
    urltime = config.GetValue(dbid)
    if urltime == "": urltime = 0
    expiresAt = int(urltime) + int(cacheTime)
    if time() < expiresAt:
        return True
    else:
        return False

#===============================================================================
# Function to clean the app database: speeds it up and saves storage space
# Input:
# interval - amount of time before a new cleanup (seconds)
# save - array containing the variable names to exclude from deleting
#===============================================================================
def CleanDb(interval, save=[]):
    latest = config.GetValue('clean')
    if latest == "": latest = 0
    expiresAt = int(latest) + int(interval)
    if time() > expiresAt:
        var_save = []
        for i in range(len(save)):
            var_save.append(config.GetValue(save[i]))
        config.ResetAll()
        config.SetValue('clean', str(time()).split('.')[0])
        for i in range(len(save)):
            config.SetValue(str(save[i]), str(var_save[i]))
