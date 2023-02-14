#!/home/xbilek5/bakalarka/env/bin/python
# -*- coding: utf-8 -*-
import cgi, cgitb

print "Content-Type: text/html; charset=utf-8"
print

cgitb.enable()
form = cgi.FieldStorage() 

import recognizer

u_list = []

if "url1" in form:
    u_list.append(form["url1"].value)
    print form["url1"].value
    print "<br />"
if "url2" in form:
    u_list.append(form["url2"].value)
    print form["url2"].value
    print "<br />"
if "url3" in form:
    u_list.append(form["url3"].value)
    print form["url3"].value
    print "<br />"
if "url4" in form:
    u_list.append(form["url4"].value)
    print form["url4"].value
    print "<br />"
if "url5" in form:
    u_list.append(form["url5"].value)
    print form["url5"].value
    print "<br />"



print "<br />"
print "<br />"

import sys




    
rec = recognizer.Recognizer(u_list)
toprint = rec.start()
for info in toprint:
    print "<br />"
    for page in info:
        print "<br />"
        for line in page:
            print "<br />"
            print line.encode('utf-8')
            print "<p><input type='checkbox' checked class='hideParagraph'/></p>"




#<div onclick="this.style.display='none'">vysledek</div>

"""
print "<p>/html[@itemtype='http://schema.org/NewsArticle'&@itemscope='']/body/div[@id='main']/div[@class=['m-bg-1']]/div[@class=['m-bg-2']]/div[@class=['m-bg-3']]/div[@class=['m-bg-4']]/div[@class=['content']&@id='content']/div[@class=['col-a']]/div[@class=['art-full']]/div[@class=['art-info']]/span[@class=['time']]/span[@content='2013-04-15T21:24CET'&@class=['time-date']&@itemprop='datePublished']/15. dubna 2013 | score 10 of 10</p><input type='checkbox' checked class='hideParagraph'/>"
print "<p>/html[@itemtype='http://schema.org/NewsArticle'&@itemscope='']/body/div[@id='main']/div[@class=['m-bg-1']]/div[@class=['m-bg-2']]/div[@class=['m-bg-3']]/div[@class=['m-bg-4']]/div[@class=['content']&@id='content']/div[@class=['col-a']]/div[@class=['art-full']]/div[@class=['art-info']]/span[@class=['time']]/span[@content='2013-04-04T16:34CET'&@class=['time-date']&@itemprop='datePublished']/4. dubna 2013 | score 10 of 10</p><input type='checkbox' checked class='hideParagraph'/>"
print "<p>/html[@itemtype='http://schema.org/NewsArticle'&@itemscope='']/body/div[@id='main']/div[@class=['m-bg-1']]/div[@class=['m-bg-2']]/div[@class=['m-bg-3']]/div[@class=['m-bg-4']]/div[@class=['content']&@id='content']/div[@class=['col-a']]/div[@class=['art-full']]/div[@class=['art-info']]/span[@class=['time']]/span[@content='2013-04-04T18:55CET'&@class=['time-date']&@itemprop='datePublished']/4. dubna 2013 | score 10 of 10</p><input type='checkbox' checked class='hideParagraph'/>"
print "<p>/html[@itemtype='http://schema.org/NewsArticle'&@itemscope='']/body/div[@id='main']/div[@class=['m-bg-1']]/div[@class=['m-bg-2']]/div[@class=['m-bg-3']]/div[@class=['m-bg-4']]/div[@class=['content']&@id='content']/div[@class=['col-a']]/div[@class=['art-full']]/div[@class=['art-info']]/span[@class=['time']]/span[@content='2013-04-04T18:55CET'&@class=['time-date']&@itemprop='datePublished']/4. dubna 2013 | score 10 of 10</p><input type='checkbox' checked class='hideParagraph'/>"
print "<p>/html[@itemtype='http://schema.org/NewsArticle'&@itemscope='']/body/div[@id='main']/div[@class=['m-bg-1']]/div[@class=['m-bg-2']]/div[@class=['m-bg-3']]/div[@class=['m-bg-4']]/div[@class=['content']&@id='content']/div[@class=['col-a']]/div[@class=['art-full']]/div[@class=['art-info']]/span[@class=['time']]/span[@content='2013-04-02T01:16CET'&@class=['time-date']&@itemprop='datePublished']/2. dubna 2013 | score 10 of 10</p><input type='checkbox' checked class='hideParagraph'/>"
print "<p>/html[@itemtype='http://schema.org/NewsArticle'&@itemscope='']/body/div[@id='main']/div[@class=['m-bg-1']]/div[@class=['m-bg-2']]/div[@class=['m-bg-3']]/div[@class=['m-bg-4']]/div[@class=['content']&@id='content']/div[@class=['col-a']]/div[@class=['art-full']]/div[@class=['art-info']]/span[@class=['time']]/span[@content='2013-04-04T20:05CET'&@class=['time-date']&@itemprop='datePublished']/4. dubna 2013 | score 10 of 10</p><input type='checkbox' checked class='hideParagraph'/>"
"""

print "<script type='text/javascript' src='http://code.jquery.com/jquery-1.9.1.min.js'></script>"
print "<button class='export'>Save</button>"
print ("<script type='text/javascript'>"+
"$(document).ready(function(){"+
"$('.export').click(function(){"+
"data = '';" +
"$('p').each(function(){if($(this).next('input').is(':checked')){data+=$(this).html();}});"+
"uriContent = 'data:text/force-download;charset=utf-8,' +data; window.open(uriContent, 'myDocument.txt');" +
"});"+
"});"+
"</script>")





