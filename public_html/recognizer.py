#!/home/xbilek5/bakalarka/env/bin/python
# -*- coding: utf-8 -*-

__author__="Tomáš Bílek"

from boilerpipe.extract import Extractor
from bs4 import BeautifulSoup, Comment
import urllib
import re
import time


class Recognizer:

     def __init__(self, u_list = None):
          if u_list is None:
               self.u_list = []
          else:
               self.u_list = u_list

          self.processed_urls = None      #list of BS pages (trees)
          self.cleaned_urls = None        #list of cleaned BS pages
          self.divided_tagpaths = None    #list of cleaned BS pagelists[path in BS tags, text, counter]
          self.intersected_paths = None   #dict {common path in string : random text}
          self.short_full_string = None   #list of cleaned BS pagelists[short path instring, full path in string, text]



     def process_urls(self):
          """Converts inserted pages into BeautifulSoup trees
          
          @return: list of BeautifulSoup pages (trees)
          """ 
          results = []
          for url in self.u_list:
               inp = BeautifulSoup(urllib.urlopen(url).read())
               comments = inp.findAll(text=lambda text:isinstance(text, Comment))
               map( lambda x: x.extract(), comments )               
               results.append(inp)

          self.processed_urls = results	
          return self.processed_urls
     
     
     def clean_urls(self):
          """Cleans inserted pages from boilerplate
          
          @return: list of cleaned BeautifulSoup pages
          """ 		
          results = []
          for url in self.processed_urls:
               extracted_html = Extractor(extractor='ArticleExtractor', html=url.prettify()).getHTML()
               results.append(BeautifulSoup(extracted_html))
          self.cleaned_urls = results
          return self.cleaned_urls



     def divide_to_tagpaths(self, bs_pages):
          """Adds parent tags path for each text on a page
          for text <div><div>Autor:</div><p>Mirek</p></div>
          computes: 
          div div, Autor:
          div p, Mirek

          input: list of process_urls - list of BeautifulSoup pages (trees)
          @return: list of pages with divided tag paths where page [path in tags, text]
          """
          page_tokens = []
          for page in bs_pages:
               tags = []
               for t in page(text=re.compile(".")):
                    path = list(reversed([x for x in t.parentGenerator() if x]))
                    tags.append([path, t.strip()])
               page_tokens.append(tags)
               
          if self.divided_tagpaths == None:
               self.divided_tagpaths = page_tokens
          return page_tokens

     def count_paths(self):
          """Counts how many instances of the same path occurs in a page
          f.e.:
          div div p, Karel, 2
          div div p, Pepa, 2
          div div span p, 20.1., 1

          @return: list of page lists where page [path in tags, text, counter]
          """

          for page in self.divided_tagpaths:
               string_paths = []
               counters = []

               for tag_text in self.short_paths_to_string(page):
                    string_paths.append(tag_text[0])
               for path in string_paths:	
                    counter = 0
                    for path2 in string_paths:

                         if(path==path2):
                              counter+= 1

                    counters.append(counter)	
               for c in range(0, counters.__len__()):
                    page[c].append(counters[c])

          return self.divided_tagpaths	


     def intersect_pages(self):
          """"Performs intersection of paths of cleaned pages

          @return: dictionary {intersected path in string : counter}
          """
          dicts_for_intersection = [] #list of pages(dicts), dict{tags string : text}
          pages_keys = []
          intersect_dicts = []


          for page in self.divided_tagpaths:
               inter_dict = {}
               for tagtext in self.short_paths_to_string(page):
                    inter_dict.update({tagtext[0]:tagtext[1]})
               dicts_for_intersection.append(inter_dict)
               pages_keys.append(set(inter_dict.keys()))

          intersect_tags = set.intersection(*pages_keys)

          for dictio in dicts_for_intersection:
               for key in set(dictio.keys()).difference(intersect_tags):
                    dictio.pop(key)

          self.intersected_paths = dictio
          return self.intersected_paths



     def short_paths_to_string(self, page):
          """Converts tags in a path to string, where string is the name of a tag
          
          input: process_urls, divide_to_tagpaths [path in tags, text]
          @return: list [path string, text]
          """
          string_paths = []
          for tag_text in page:
               path = ' '.join(x.name for x in tag_text[0] )
               string_paths.append([path, tag_text[1]])
          return string_paths

     def short_full_paths_to_string(self, divided_tagpaths):
          """Converts tag in a path to  two strings, where first string is the name of a tag
          second string is name of a tag + tags attributes
          
          input: process_urls, divide_to_tagpaths [path in tags, text]
          @return: list [short path string, full path string, text]
          """
          group_string_paths = []
          for page in divided_tagpaths:
               string_paths = []
               for tag_text in page:
                    tagpath = []
                    for tag in tag_text[0]:
                         tagatrib = []
                         for attribute in tag.attrs:
                              if attribute != ('onload' or 'onchange' or'onclick'):
                                   tagatrib.append('@' + attribute +'='+ tag[attribute].__repr__())

                         atrs ='&'.join(tagatrib)

                         if tagatrib != []:

                              tagpath.append(tag.name + '['+atrs+']')
                         else:
                              tagpath.append(tag.name)

                    pathfull = '/'.join(tagpath)[10:]

                    pathshort = ' '.join(x.name for x in tag_text[0] )
                    string_paths.append([pathshort, pathfull, tag_text[1]])
               group_string_paths.append(string_paths)
          if self.short_full_string == None:
               self.short_full_string = group_string_paths
          return group_string_paths

     def find_date(self):
          """Tries to find dates of all inserted pages
          Output is list of dates for each page
          
          @return: list [path string, date]
          """	
          date_tag_re = re.compile(r"date|datum", re.IGNORECASE)

          months = '''led(?:en|na)|únor(?:a)?|břez(?:en|na)|dub(?:en|na)|
		květ(?:en|na)|červ(?:en|na)|červen(?:ce|ec)|srp(?:en|na)|září|
		říj(?:en|na)|listopad(?:u)?|prosin(?:ec|ce)'''

          date_text_re = re.compile(r"""\b\d{{1,2}}\s{{0,4}}[.]\s{{0,4}}(?:\b\d{{1,2}}|{0})
                                     (?:\s{{1,4}}|[.])\s{{0,4}}(?:(?:20|19)\d{{2}}\b)?""".format(months), re.IGNORECASE|re.VERBOSE)	

          page_counter = -1
          result = []
          
          for shortfull_path_page in self.short_full_string:	
               found = 0
               page_counter += 1
               page_result = []
               for key_path in self.intersected_paths:	
                    for shortfull_path in shortfull_path_page:
                         if key_path == shortfull_path[0]:
                              match = date_tag_re.search(shortfull_path[1])
                              if match != None:
                                   match2 = date_text_re.search(shortfull_path[2].encode('utf-8'))
                                   if match2 != None:
                                        found = 1
                                        #print shortfull_path[1] + '/' + shortfull_path[2] + ' | score 10 of 10'
                                        page_result.append(shortfull_path[1] + '/' + shortfull_path[2] + ' | score 50 of 50')
                                        self.short_full_string[page_counter].remove(shortfull_path)



               if found == 0:
                    for shortfull_path in shortfull_path_page:
                         match = date_tag_re.search(shortfull_path[1])
                         if match != None:
                              match2 = date_text_re.search(shortfull_path[2].encode('utf-8'))
                              if match2 != None:
                                   found = 1
                                   #print shortfull_path[1] + '/' + shortfull_path[2] + ' | score 9 of 10'
                                   page_result.append(shortfull_path[1] + '/' + shortfull_path[2] + ' | score 40 of 50')                                  
                                   self.short_full_string[page_counter].remove(shortfull_path)


               if found == 0:
                    for shortfull_path in shortfull_path_page:
                         if shortfull_path[2].__len__() < 40:                           
                              match2 = date_text_re.search(shortfull_path[2].encode('utf-8'))
                              if match2 != None:
                                   found = 1
                                   #print shortfull_path[1] + '/' + shortfull_path[2] + ' | score 7 of 10'
                                   page_result.append(shortfull_path[1] + '/' + shortfull_path[2] + ' | score 30 of 500')                                   
                                   self.short_full_string[page_counter].remove(shortfull_path)




               if found == 0:
                    for shortfull_path in self.short_full_paths_to_string(self.divide_to_tagpaths(self.processed_urls))[page_counter]:
                         tags = [shortfull_path[1], shortfull_path[2]]
                         match = date_tag_re.search(tags[0])
                         if match != None:
                              match2 = date_text_re.search(tags[1].encode('utf-8'))
                              if match2 != None:
                                   #print tags[0] + '/' + tags[1]  + ' | score 5 of 10'
                                   page_result.append(tags[0] + '/' + tags[1]  + ' | score 20 of 50')
                                  
               result.append(page_result)
          return result
                                  



     def find_author(self):	
          """Tries to find authors of all inserted pages
          Output is list of authors for each page
          
          @return: list [path string, author]
          """          

          photo_re = re.compile(r"photo", re.IGNORECASE)
          woman_re = re.compile(ur"ová\b", re.UNICODE)
          capital_re = re.compile(ur"([A-Z]|Á|Č|Ď|É|Í|Ň|Ó|Ř|Š|Ť|Ú|Ý|Ž)", re.UNICODE)
          author_tag_re = re.compile(r"(author(:?s)?|autor)", re.IGNORECASE)
          autor_re = re.compile(ur"\AAuto(r|ři):\Z", re.IGNORECASE|re.UNICODE)

          page_counter = -1
          result = []
          
          for shortfull_path_page in self.short_full_string:	
               
               found = 0
               page_counter += 1
               page_result = []
               for key_path in self.intersected_paths:	
                    for shortfull_path in shortfull_path_page:
                         if key_path == shortfull_path[0]:
                              match = author_tag_re.search(shortfull_path[1])
                              if match != None:
                                   prob = 37
                                   if (shortfull_path[2].__len__() < 30) and (shortfull_path[2].__len__() > 1):
                                        prob += 1
                                        f_match = capital_re.search(shortfull_path[2][0])
                                        if f_match != None:
                                             prob += 1                                        
                                   w_match = woman_re.search(shortfull_path[2])
                                   if w_match != None:
                                        prob += 1

                                   if prob > 37:
                                        p_match = photo_re.search(shortfull_path[1])
                                        a_match = autor_re.search(shortfull_path[2])
                                        if p_match == None and a_match == None:
                                             found = 1
                                             #print shortfull_path[1].encode('utf-8') + '/' + shortfull_path[2].encode('utf-8') +' | score '+ prob.__repr__() + ' of 13'
                                             page_result.append(shortfull_path[1] + '/' + shortfull_path[2] +' | score '+ prob.__repr__() + ' of 40')
                                             self.short_full_string[page_counter].remove(shortfull_path)
               
               for shortfull_path in shortfull_path_page:
                    match = author_tag_re.search(shortfull_path[1])
                    if match != None:
                         prob = 27
                         if (shortfull_path[2].__len__() < 30) and (shortfull_path[2].__len__() > 1):
                              prob += 1
                              f_match = capital_re.search(shortfull_path[2][0])
                              if f_match != None:
                                   prob += 1                                    
                         w_match = woman_re.search(shortfull_path[2])
                         if w_match != None:
                              prob += 1
                        
                         if prob > 27:
                              p_match = photo_re.search(shortfull_path[1])
                              a_match = autor_re.search(shortfull_path[2])
                              if p_match == None and a_match == None:
                                   found = 1
                                   #print shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 13'
                                   page_result.append(shortfull_path[1] + '/' + shortfull_path[2] +' | score '+ prob.__repr__() + ' of 40')
                                   self.short_full_string[page_counter].remove(shortfull_path)




               if found == 0:
                    for shortfull_path in self.short_full_paths_to_string(self.divide_to_tagpaths(self.processed_urls))[page_counter]:
                         tags = [shortfull_path[1], shortfull_path[2]]
                         match = author_tag_re.search(tags[0])
                         if match != None:
                              prob = 17
                              if (tags[1].__len__() < 30) and (tags[1].__len__() > 1):
                                   prob += 1
                                   f_match = capital_re.search(tags[1][0])
                                   if f_match != None:
                                        prob += 1                                   
                              w_match = woman_re.search(tags[1])
                              if w_match != None:
                                   prob += 1
                              
                              if prob > 17:
                                   p_match = photo_re.search(tags[0])
                                   a_match = autor_re.search(tags[1])
                                   if p_match == None and a_match == None:
                                        found = 1  
                                        #print tags[0] + '/' + tags[1] + ' | score '+ prob.__repr__() + ' of 13'
                                        page_result.append(tags[0] + '/' + tags[1] + ' | score '+ prob.__repr__() + ' of 40')


               result.append(page_result)
          return result

     def find_title(self):
          """Tries to find titles of all inserted pages
          Output is list of titles for each page
          
          @return: list [path string, title]
          """          
          
          h2_re = re.compile(r"\bh2\b")
          h1_re = re.compile(r"\bh1\b")
          logo_re = re.compile(r"\blogo\b")
          capital_re = re.compile(ur"([A-Z]|Á|Č|Ď|É|Í|Ň|Ó|Ř|Š|Ť|Ú|Ý|Ž)", re.UNICODE)
          page_counter = -1
          result = []
          
          for shortfull_path_page in self.short_full_string:
               page_counter += 1
               found = 0
               page_result = []
               for key_path in self.intersected_paths:	
                    for shortfull_path in shortfull_path_page:
                         if key_path == shortfull_path[0]:               
                              match = h1_re.search(shortfull_path[1])
                              if match != None:
                                   prob = 96
                                   if shortfull_path[2].__len__() > 1:
                                        prob += 1
                                        if shortfull_path[2].__len__() > 20:
                                             prob += 1
                                        if shortfull_path[2][-1] != '.':
                                             prob += 1                                        
                                        match2 = capital_re.search(shortfull_path[2][0])
                                        if match2 != None:
                                             prob += 1   
                                   if prob > 96:
                                        match3 = logo_re.search(shortfull_path[1])
                                        if match3 == None:
                                             found = 1
                                             #print shortfull_path[1].encode('utf-8') + '/' + shortfull_path[2].encode('utf-8') + ' | score '+ prob.__repr__() + ' of 14'
                                             page_result.append(shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 100')
                                             self.short_full_string[page_counter].remove(shortfull_path)
                                        
               if found == 0:                    
                    for shortfull_path in shortfull_path_page:
                         match = h1_re.search(shortfull_path[1])
                         if match != None:
                              prob = 86
                              if shortfull_path[2].__len__() > 1:
                                   prob += 1
                                   if shortfull_path[2].__len__() > 20:
                                        prob += 1                                   
                                   if shortfull_path[2][-1] != '.':
                                        prob += 1                                   
                                   match2 = capital_re.search(shortfull_path[2][0])
                                   if match2 != None:
                                        prob += 1   
                              if prob > 86:
                                   match3 = logo_re.search(shortfull_path[1])
                                   if match3 == None:                                   
                                        found = 1
                                        #print shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 14'
                                        page_result.append(shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 100')
                                        self.short_full_string[page_counter].remove(shortfull_path)
                                   
               if found == 0:
                    for shortfull_path in self.short_full_paths_to_string(self.divide_to_tagpaths(self.processed_urls))[page_counter]:
                         match = h1_re.search(shortfull_path[1])
                         if match != None:
                              prob = 66
                              if shortfull_path[2].__len__() > 1:
                                   prob += 1
                                   if shortfull_path[2].__len__() > 20:
                                        prob += 1                                   
                                   if shortfull_path[2][-1] != '.':
                                        prob += 1                                 
                                   match2 = capital_re.search(shortfull_path[2][0])
                                   if match2 != None:
                                        prob += 1   
                              if prob > 66:
                                   match3 = logo_re.search(shortfull_path[1])
                                   if match3 == None:                                   
                                        found = 1
                                        #print shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 14'
                                        page_result.append(shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 100')
                                        

               if found == 0:
                    for shortfull_path in self.short_full_paths_to_string(self.divide_to_tagpaths(self.processed_urls))[page_counter]:
                         if shortfull_path[0][:26] == '[document] html head title':
                              prob = 56
                              if shortfull_path[2].__len__() > 1:
                                   prob += 1
                                   if shortfull_path[2].__len__() > 20:
                                        prob += 1                                   
                                   if shortfull_path[2][-1] != '.':
                                        prob += 1                                 
                                   match2 = capital_re.search(shortfull_path[2][0])
                                   if match2 != None:
                                        prob += 1   
                              if prob > 56:                                  
                                   found = 1
                                   #print shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 14'
                                   page_result.append(shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 100')
                                   
               if found == 0:
                    for shortfull_path in self.short_full_paths_to_string(self.divide_to_tagpaths(self.processed_urls))[page_counter]:
                         match = h2_re.search(shortfull_path[1])
                         if match != None:
                              prob = 40
                              if shortfull_path[2].__len__() > 1:
                                   prob += 1
                                   if shortfull_path[2].__len__() > 20:
                                        prob += 1                                   
                                   if shortfull_path[2][-1] != '.':
                                        prob += 1                                 
                                   match2 = capital_re.search(shortfull_path[2][0])
                                   if match2 != None:
                                        prob += 1   
                              if prob > 40:
                                   match3 = logo_re.search(shortfull_path[1])
                                   if match3 == None:                                   
                                        found = 1
                                        #print shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 14'
                                        page_result.append(shortfull_path[1] + '/' + shortfull_path[2] + ' | score '+ prob.__repr__() + ' of 100')                         
                    
                                   
               result.append(page_result)
          return result
     def find_article(self):
          """Tries to find an article of all inserted pages
          Output is list of article sentences for each page
          
          @return: list [path string, article sentence]
          """          
          page_counter = -1
          result = []
          
          for page in self.divided_tagpaths:
               
               page_counter += 1
               page_result = []
               maxtag = max(page, key=lambda t: t[2])
               path = ' '.join(x.name for x in maxtag[0])
               alter_strings = page
               while path not in self.intersected_paths:
                    for shortfull_path in alter_strings:
                         if shortfull_path[2] == maxtag[2]:
                              alter_strings.remove(shortfull_path)                    
                    maxtag = max(alter_strings, key=lambda t: t[2])
                    path = ' '.join(x.name for x in maxtag[0])


               article = []
               counters = []
               for shortfull_path in self.short_full_string[page_counter]:
                    if shortfull_path[0] == path:
                         article.append(shortfull_path)
                         
               for shortfull_path in article:	
                    counter = 0
                    for shortfull_path2 in article:

                         if(shortfull_path[1]==shortfull_path2[1]):
                              counter+= 1

                    counters.append(counter)	
               for c in range(0, counters.__len__()):
                    article[c].append(counters[c])      
                    
               maxpath = max(article, key=lambda t: t[3])
               maxpath_a = maxpath[1] + '/a'
               maxpath_b = maxpath[1] + '/b'
               maxpath_span = maxpath[1] + '/span'
               maxpath_strong = maxpath[1] + '/strong'
               maxpath_h2 = maxpath[1] + '/h2'
               maxpath_h3 = maxpath[1] + '/h3'
               maxpath_h4 = maxpath[1] + '/h4'
               
               for shortfull_path in self.short_full_string[page_counter]:               
                    if ((shortfull_path[1] == maxpath[1]) 
                    or (shortfull_path[1][:maxpath_a.__len__()] == maxpath_a)
                    or (shortfull_path[1][:maxpath_b.__len__()] == maxpath_b)
                    or (shortfull_path[1][:maxpath_span.__len__()] == maxpath_span)
                    or (shortfull_path[1][:maxpath_strong.__len__()] == maxpath_strong)
                    or (shortfull_path[1][:maxpath_h2.__len__()] == maxpath_h2)
                    or (shortfull_path[1][:maxpath_h3.__len__()] == maxpath_h3)
                    or (shortfull_path[1][:maxpath_h4.__len__()] == maxpath_h4)
                    or (shortfull_path[0] == maxpath[0])
                    ):
                         #print shortfull_path[1] + '/' + shortfull_path[2]
                         page_result.append(shortfull_path[1] + '/' + shortfull_path[2])
               result.append(page_result)
          return result
                         
                         
     def start(self):
          """Starts the application
          @return: list of results 
          """          
          self.process_urls()                         
          self.short_full_paths_to_string(self.divide_to_tagpaths(self.clean_urls()))     
          self.count_paths()               
          self.intersect_pages()          
          date = self.find_date()     
          author = self.find_author()          
          title = self.find_title()     
          article = self.find_article()  
          
          result = [date, author, title, article]
          return result


if __name__ == "__main__":
     start_time = time.time()
     u_list = []
     #url1 = 'http://zpravy.idnes.cz/dve-exploze-v-cily-bostonskeho-maratonu-fd6-/zahranicni.aspx?c=A130415_212700_zahranicni_ert'
     #url2 = 'http://zpravy.idnes.cz/krize-na-korejskem-poloostrove-dnf-/zahranicni.aspx?c=A130404_125630_zahranicni_tp'
     #url3 = 'http://zpravy.idnes.cz/demonstrace-7-dubna-na-vaclavskem-namesti-fpo-/domaci.aspx?c=A130404_134414_domaci_jw'
     #url4 = 'http://zpravy.idnes.cz/ods-zrusila-bunku-ve-frantiskovych-laznich-fe5-/domaci.aspx?c=A130401_210628_vary-zpravy_brm'
     #url5 = 'http://zpravy.idnes.cz/poutak-na-rozhovor-se-svedkem-vrazdy-petry-v-jihlave-p0o-/krimi.aspx?c=A130404_141110_jihlava-zpravy_mv'

     #url1 = 'http://www.novinky.cz/domaci/299493-kalousek-poslancum-penize-na-fotbal-neda.html'
     #url2 = 'http://www.novinky.cz/domaci/299498-komunistickeho-namestka-sloupa-opet-neodvolali.html'
     #url3 = 'http://www.novinky.cz/domaci/299488-zemanovy-kandidaty-na-ustavni-soudce-podporil-dalsi-senatni-vybor.html'
     #url4 = 'http://www.novinky.cz/domaci/299475-heger-oznamil-ktere-ustavy-a-nemocnice-slouci.html'
     #url5 = 'http://www.novinky.cz/domaci/299458-rozhodnuti-o-korekcich-za-chyby-v-rop-karlovarsti-zastupitele-opet-odlozili.html'

     #url1 = 'http://aktualne.centrum.cz/zahranici/amerika/clanek.phtml?id=777304'
     #url2 = 'http://aktualne.centrum.cz/ekonomika/nakupy/clanek.phtml?id=777727#utm_source=aktualne.centrum.cz&utm_medium=article-hint&utm_content=zahranici'
     #url3 = 'http://aktualne.centrum.cz/domaci/politika/clanek.phtml?id=777347'
     #url4 = 'http://aktualne.centrum.cz/domaci/regiony/praha/clanek.phtml?id=777266'
     #url5 = 'http://aktualne.centrum.cz/zahranici/evropska-unie/clanek.phtml?id=777684#utm_source=aktualne.centrum.cz&utm_medium=article-hint&utm_content=domaci'

     #url1 = 'http://zpravy.ihned.cz/cesko/c1-59716080-exekuce-dluh-ustavni-soud'
     #url2 = 'http://zpravy.ihned.cz/svet-usa/c1-59715110-exploze-v-texasu-si-vyzadala-pres-sto-zranenych-zasahla-i-komunitu-ceskych-pristehovalcu'
     #url3 = 'http://zpravy.ihned.cz/cesko/c1-59716790-policie-zatkla-tri-manazery-na-podvodech-s-dotacemi-meli-vydelat-315-milionu'
     #url4 = 'http://zpravy.ihned.cz/cesko-zdravotnictvi/c1-59406110-dotace-krajska-zdravotni-rop-severozapad'
     #url5 = 'http://zpravy.ihned.cz/svet-usa/c1-59711980-vysetrovatele-asi-znaji-podobu-podezreleho-z-utoku-v-bostonu-odhalily-ho-zaznamy-kamer'	

     url3 = 'http://www.lidovky.cz/svet-podle-gorbacova-potrebuje-trvale-udrzitelnou-perestrojku-p8k-/zpravy-svet.aspx?c=A130418_162918_ln_zahranici_hm'
     url2 = 'http://www.lidovky.cz/policejni-razie-v-hernach-provozovatele-prchali-s-cernymi-automaty-116-/zpravy-domov.aspx?c=A130426_164318_ln_domov_spa'
     url4 = 'http://www.lidovky.cz/gorbacov-poprel-twitterove-zpravy-o-sve-smrti-flr-/media.aspx?c=A120522_193434_ln-media_ape'
     url1 = 'http://www.lidovky.cz/jakou-roli-hral-pri-puci-gorbacov-byl-jsem-poloidiot-rika-pzj-/zpravy-svet.aspx?c=A110819_095343_ln_zahranici_mtr'
     url5 = 'http://www.lidovky.cz/michailu-gorbacovovi-vysly-v-rusku-pameti-fjy-/lide.aspx?c=A121113_202109_lide_jkz'	

     #url1 = 'http://blog.aktualne.centrum.cz/blogy/jiri-dolejs.php?itemid=19947'
     #url2 = 'http://blog.aktualne.centrum.cz/blogy/jiri-dolejs.php?itemid=19891'
     #url3 = 'http://stastny.blog.denik.cz/c/217918/Slovensko-kdo-koho-vydiral-pri-hlasovani-o-eurovalu.html'
     #url4 = 'http://stastny.blog.denik.cz/c/209530/Cesko-jadernou-velmoci-Blabol-nebo-realna-vize.html'
     #url5 = 'http://stastny.blog.denik.cz/c/208048/Chomutovsky-zimni-stadion-presunut-do-horske-obce-Krimov.html'	

     
     
     u_list.append(url1)
     u_list.append(url2)
     u_list.append(url3)
     u_list.append(url4)
     u_list.append(url5)	



     rec = Recognizer(u_list)
     rec.start()
     
     

     

     print time.time() - start_time, "seconds"	





