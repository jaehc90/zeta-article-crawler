
# coding: utf-8

# In[1]:


import datetime
import urllib.request
import argparse
import time
import urllib.parse
import re
import signal
import sys
import os
from bs4 import BeautifulSoup
from random import shuffle
import random


def find_url_from_youtube_desc(desc):
    begin = desc.find('http:')
    t = desc[begin:]
    end = t.find('\n')
    return desc[begin:begin+end]

# queryURL = "http://www.ytn.co.kr/_ln/0101_201711080903269081"
def find_text_ytn(queryURL):
    req = urllib.request.Request(queryURL, data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'})

    res = urllib.request.urlopen(req)
    webpage = res.read().decode(res.headers.get_content_charset(), errors='ignore')
    soup = BeautifulSoup(webpage,'html.parser')
    try:
        div = soup.find_all('div', class_="article_paragraph")[0]
        span = div.find_all('span')[0]
    except Exception as e:
        print("error querying {} : {}".format(queryURL, e))
        return "no article_paragraph"
    return span.text


def get_path_url_from_hash (hash):
    headers =     {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
     "cookie" : "YSC=f7Nn85R0uvY; VISITOR_INFO1_LIVE=R4dd4kfRgRc; PREF=f1=50000000; dkv=ffe50b58a9f7a803a60dd3098efb138de3QEAAAAdGxpcGnErgtaMA=="
     }
    queryURL = "https://www.youtube.com/watch?v=" + hash

    req = urllib.request.Request(queryURL, data=None,
                                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'})
    res = urllib.request.urlopen(req)
    webpage = res.read().decode(res.headers.get_content_charset(), errors='ignore')
    print(res)
    import pdb;pdb.set_trace();
    soup = BeautifulSoup(webpage,'html.parser')
    a_list = soup.find_all('a')
    for a in a_list:
        print(a)
        if 'ytn.co.kr' in str(a):
            print (a['href'])
            redirect_path = a['href']
            unquoted_str = urllib.parse.unquote(redirect_path, encoding='utf-8', errors='replace')
            begin = unquoted_str.find('http:')
            end = unquoted_str[begin:].find('&')
            unquoted_str[begin:begin+end]
            return unquoted_str[begin:begin+end]

    return ""


def get_url_from_hash(hash, debug=False):
    import requests
    q_url = "https://www.youtube.com/watch?v=" + hash
    r = requests.get(q_url)
    content = r.content.decode('utf-8')
    soup = BeautifulSoup(content,'html.parser')
    # div = soup.find_all('div', class_="article_paragraph")[0]
    a_list = soup.find_all('a')
    for a in a_list:
        print(a) if debug else {}
        if 'ytn.co.kr' in str(a):
            redirect_path = a['href']
            unquoted_str = urllib.parse.unquote(redirect_path, encoding='utf-8', errors='replace')
            begin = unquoted_str.find('http:')
            end = unquoted_str[begin:].find('&')
            unquoted_str[begin:begin+end]
            return unquoted_str[begin:begin+end]

    return ""


# In[31]:


# get_url_from_hash('brGC-kfR-gQ')


# In[32]:


def dump_ytn_original_scripts(dirname):
    files = os.listdir(dirname)
    no_url_counts = 0
    for i, file in enumerate(files):
        if 'description' in file:
            prefix = file.split('.')[0]

            f = open(os.path.join(dirname,file), "r")
            text = f.read()
            f.close()

            queryURL = find_url_from_youtube_desc(text)
            if queryURL != "":
                _text = find_text_ytn(queryURL)
            else:
                no_url_counts += 1
                _text = "No URL Found:\n\n\n" + text
                print(_text)
                prefix += ".incomplete"

            f = open(os.path.join(dirname, prefix + '.txt'), "w")
            print("saving {} ...".format(prefix + '.txt'))
            f.write(_text)
            f.close()

    return no_url_counts


# In[11]:

import sys
dirname = sys.argv[1]

if len(dirname) == 0:
    print("error")

print("number of files converted: {}".format(dump_ytn_original_scripts(dirname)))
