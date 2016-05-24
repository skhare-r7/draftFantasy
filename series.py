import lxml.html
import re
import difflib
import json
import sys

class series:
  def __init__():
    self.finals = {}
    self.finals[57]='981013'
#    self.finals[58]=
#    self.finals[59]=
#    self.finals[60]=
  
  
  @staticmethod
  def get_live_url(matchId):
    base_url = "http://www.espncricinfo.com"
    suffix_url = "?view=scorecard"
    finals_url = "/indian-premier-league-2016/engine/match/"
    if matchId in self.finals.keys():
      return base_url+finals_url+self.finals[matchId]+'.html'

    SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
    def ordinal(num):
      if 10 <= num % 100 <= 20:
        suffix = 'th'
      else:
        # the second parameter is a default.
        suffix = SUFFIXES.get(num % 10, 'th')
      return str(num) + suffix

    lookFor = "'"+ ordinal(matchId) + " match'"
    seriesPage = "http://www.espncricinfo.com/indian-premier-league-2016/content/series/968923.html?template=fixtures"
    tree = lxml.html.parse(seriesPage)
    link = tree.xpath("//span[@class='play_team']/a[contains(text(),"+lookFor+")]/@href")[0]
    return base_url+link+suffix_url
