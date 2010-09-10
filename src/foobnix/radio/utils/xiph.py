'''
Created on Sep 10, 2010

@author: ivan
'''
import site
import urllib2
def load_urls_name_page():    
    file = open("XIPH_ORG.fpl", "w")
    for i in xrange(5):    
        print "begin"
        connect = urllib2.urlopen("http://dir.xiph.org/by_format/MP3?search=MP3&page="+str(i))
        data = connect.read()
        print "end"  
        
        name=""
        link="" 
        description="" 
        genre =""
        genres=[]
        
        for line in data.split("\n"):
            if line.find("('/stream/website');") >= 0:
                if name:            
                    all =  name + " ("+description +") "+  ", ".join(genres) + "="+link +"\n"
                    all = all.replace("&#039;","")
                    all = all.replace("&amp;","&")
                    print all
                    file.write(all)          
                    genres=[]
                                
                name =  line[line.find("('/stream/website');")+len("('/stream/website');")+2:line.find("</a>")]
                #print "RADIO:- "+name.replace("&#039;","'")
            
            
            """href="/listen/1003756/listen.m3u">M3U</a>"""
            if line.find("M3U</a>") >= 0:
                link = line[line.find('href="/listen/')+len('href="'):line.find('title="')-2]
                link = "http://dir.xiph.org/"+link
                #print link
    
            """<p class="stream-description">Jazz, Soul und Blues rund um die Uhr</p>"""    
            if line.find('stream-description">')>= 0:
                description = line[line.find('stream-description">')+len("stream-description'>"):line.find("</p>")]
                #print "description:- "+description.replace("&#039;","'")
            
            """<a title="Music radios" href="/by_genre/Music">Music</a>"""
            if line.find(' href="/by_genre/')>= 0 and line.find("dir.xiph.org")<0:
                genre = line[line.find('>')+len('href="/by_genre/')+4:line.find('</a>')]
                if genre.find('" title') >0:
                    genre = genre[:genre.find('" title')]
                #print "genre:- "+genre
                genres.append(genre)
            
    file.close();
load_urls_name_page()   