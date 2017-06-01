import lxml.html
import re
import difflib
import json
import sys

class series:
  @staticmethod
  def get_live_url(matchId):
    base_url = "http://www.espncricinfo.com"
    suffix_url = "?view=scorecard"
#    finals_url = "/indian-premier-league-2017/engine/match/"
#todo: fix before finals
#    if matchId in series.finals.keys():
#      return base_url+finals_url+series.finals[matchId]+'.html'+suffix_url

    seriesPage = "http://www.espncricinfo.com/icc-champions-trophy-2017/content/series/1022345.html?template=fixtures"
    tree = lxml.html.parse(seriesPage)
    link = tree.xpath('//ul[@class="large-20 columns"]/li['+matchId.__str__()+']//a/@href')[0]
    return base_url+link+suffix_url
