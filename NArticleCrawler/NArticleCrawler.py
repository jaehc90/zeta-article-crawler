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

parser = argparse.ArgumentParser(description="Crawl Naver Articles html")
parser.add_argument('-i', help='Input file (overrides other options)')
parser.add_argument('-r', action="store_true", default=False, help="Randomize link downloads")
parser.add_argument('ss', help="Start Date e.g. 20170101")
parser.add_argument('to', help="End Date e.g. 20170103")
parser.add_argument('oids', nargs="+", help='Office IDs')
args = parser.parse_args()

all_article_links = []

if args.i is None:
  starting_date = datetime.date(int(args.ss[0:4]), int(args.ss[4:6]), int(args.ss[6:8]))
  end_date = datetime.date(int(args.to[0:4]), int(args.to[4:6]), int(args.to[6:8]))
  one_day = datetime.timedelta(1)
  date_string_list = []
  current_date = starting_date
  while (current_date <= end_date):
    date_string_list.append(str(current_date.year).zfill(4) + str(current_date.month).zfill(2) + str(current_date.day).zfill(2))
    current_date = current_date + one_day
  file = open("tmp-article_links.txt", "w")

  for current_date_string in date_string_list:
    for oid in args.oids:
      daily_article_links_set = set()
      last_page_links_set = set();
      for page_num in range(1, 10000): # for every page
        time.sleep(random.randint(0, 400) / 1000)
        current_page_links_set = set();
        queryURL = "http://news.naver.com/main/list.nhn?mode=LPOD&mid=sec&oid=" + oid + "&date=" + current_date_string + "&page=" + str(page_num)
        req = urllib.request.Request(queryURL, data=None, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'})
        res = urllib.request.urlopen(req)
        webpage = res.read().decode(res.headers.get_content_charset(), errors='ignore')
        soup = BeautifulSoup(webpage,'html.parser')
        article_ul = soup.find_all('ul', class_='type06_headline')[0]
        no_more_articles_for_the_day = False
        article_links = article_ul.find_all('a', class_='nclicks(fls.list)')
        for article_link in article_links:
          article_link = article_link['href']
          if article_link in last_page_links_set or article_link in current_page_links_set:
            continue
          else:
            current_page_links_set.add(article_link)
            print(current_date_string + ": " + oid + " - " + article_link)
        if len(current_page_links_set) == 0:
          break
        else:
          last_page_links_set = current_page_links_set
          daily_article_links_set = daily_article_links_set.union(current_page_links_set)
      for article_link in daily_article_links_set:
        file.write(current_date_string)
        file.write('\n')
        file.write(oid)
        file.write('\n')
        file.write(article_link)
        file.write('\n')
        all_article_links.append((current_date_string, oid, article_link))
    file.flush()
  file.close()
else:
  print("Importing " + args.i)
  file = open(args.i, mode='r', encoding="utf-8")
  lines = file.read().splitlines()
  file.close()
  for triple in zip(*[iter(lines)]*3):
    all_article_links.append(triple)

if args.r:
  shuffle(all_article_links)

regex_bracket = re.compile(r"\[(.*?)\]")
starting_time = time.time();
article_count = 1
for date_string, oid, article_link in all_article_links:
  try:
    current_time = time.time();
    time_per_item = (current_time - starting_time) / article_count
    remaining_time = (len(all_article_links) - article_count) * time_per_item
    article_count = article_count + 1
    print("{:0.2f}".format(remaining_time) + " seconds remaining: " + str(article_count) + "/" + str(len(all_article_links)) + " " + date_string + "_" + oid + "_" + article_link, end = '')
    encoded_file_name = urllib.parse.quote_plus(article_link)
    if os.path.isfile("output/original_html/NaverArticle_" + date_string + "_" + oid + "_" + encoded_file_name + ".html"):
      if os.path.isfile("output/extracted_txt/NaverArticle_" + date_string + "_" + oid + "_" + encoded_file_name + ".txt"):
        print(" - skip")
        continue

    #time.sleep(random.randint(0, 100) / 1000)
    req = urllib.request.Request(article_link, data=None, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36'})
    res = urllib.request.urlopen(req)
    webpage = res.read().decode(res.headers.get_content_charset(), errors='ignore')
 
    soup = BeautifulSoup(webpage,'html.parser')
    body_contents = soup.find_all('div', id='articleBodyContents')
    if len(body_contents) > 0:
      body_contents = body_contents[0]
    else:
      body_contents = soup.find_all('div', id='newsEndContents')
      if len(body_contents) > 0:
        body_contents = body_contents[0]
      else:
        body_contents = soup.find_all('div', id='articeBody')
        if len(body_contents) > 0:
          body_contents = body_contents[0]
        else:
          print(" - NO BODY FOUND")
          continue

    [s.extract() for s in body_contents('script')]
    text_raw = body_contents.text
    text = regex_bracket.sub(' ', text_raw)
    text = text.replace('\t', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('  ', ' ')
    text = text.strip()

    text = text.replace(".", ".\n")
    text = text.replace("!", "!\n")
    text = text.replace("?", "?\n")

    if len(text) == 0:
      print(" - No Text")
      continue
    lines = text.split('\n')
    lines = [line.strip() for line in lines if len(line.strip()) > 3]
    text = '\n'.join(lines)

    file = open("output/original_html/NaverArticle_" + date_string + "_" + oid + "_" + encoded_file_name + ".html", 'w', encoding=res.headers.get_content_charset())
    file.write(webpage)
    file.close()
    file = open("output/extracted_txt/NaverArticle_" + date_string + "_" + oid + "_" + encoded_file_name + ".txt", 'w', encoding='utf-8')
    file.write(text)
    file.close()
    print(" - Success!")
  except:
    print(" - Fail!")
    time.sleep(0.5)