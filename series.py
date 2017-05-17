import lxml.html
import re
import difflib
import json
import sys

class series:
  finals = {}
  finals[57]='1082647'
  finals[58]='1082648'
  finals[59]='1082649'
  finals[60]='1082650'
  
  @staticmethod
  def get_live_url(matchId):
    base_url = "http://www.espncricinfo.com"
    suffix_url = "?view=scorecard"
    finals_url = "/indian-premier-league-2017/engine/match/"
#todo: fix before finals
    if matchId in series.finals.keys():
      return base_url+finals_url+series.finals[matchId]+'.html'+suffix_url

    SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
    def ordinal(num):
      if 10 <= num % 100 <= 20:
        suffix = 'th'
      else:
        # the second parameter is a default.
        suffix = SUFFIXES.get(num % 10, 'th')
      return str(num) + suffix

    lookFor = "'"+ ordinal(matchId) + " match'"
    seriesPage = "http://www.espncricinfo.com/indian-premier-league-2017/content/series/1078425.html?template=fixtures"
    tree = lxml.html.parse(seriesPage)
    link = tree.xpath("//span[@class='play_team']/a[contains(text(),"+lookFor+")]/@href")[0]
    return base_url+link+suffix_url
