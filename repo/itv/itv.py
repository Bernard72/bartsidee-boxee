from default import *
from library import *
import tools

sys.path.append(os.path.join(CWD, 'external'))

from BeautifulSoup import BeautifulSoup
from urllib import quote_plus, quote
import simplejson as json

class Module(BARTSIDEE_MODULE):
    def __init__(self, app):
        self.app            =   app
        BARTSIDEE_MODULE.__init__(self, app)

        self.name           = "ITV Player"                      #Name of the channel
        self.type           = ['search', 'genre']               #Choose between 'search', 'list', 'genre'
        self.episode        = True                              #True if the list has episodes
        self.filter         = ['itv1','itv2','itv3','itv4']     #Option to set a filter to the list
        self.genre          = ['today', 'yesterday']            #Array to add a genres to the genre section [type genre must be enabled]
        self.content_type   = 'video/x-flv'                     #Mime type of the content to be played
        self.country        = 'UK'                              #2 character country id code

        self.url_base       = 'http://www.itv.com'

    def Search(self, search):
        url     = 'http://mercury.itv.com/api/json/dotcom/Programme/Search/' + quote(search)
        data    = tools.urlopen(self.app, url)
        json_data = json.loads(data)

        streamlist = list()
        for info in json_data['Result']:
            stream = CreateList()
            stream.name     =   info['Details'][0]['Programme']['Programme']['Title']
            stream.id       =   info['Details'][0]['Programme']['MostRecentEpisodeId']
            streamlist.append(stream)

        return streamlist

    def Episode(self, stream_name, stream_id, page, totalpage):
        url = 'http://mercury.itv.com/api/html/dotcom/Episode/Programme/' + quote(stream_id)
        data = tools.urlopen(self.app, url, {'cache':3600})
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")

        if len(data) < 10:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            return []
        table = soup.find('tbody')

        episodelist = list()
        for info in table.findAll('tr'):
            time = info.find('td',{'class':'t_time'})
            duration = info.find('td',{'class':'t_duration'})
            details = info.find('td',{'class':'t_details'})

            episode             =   CreateEpisode()
            episode.name        =   stream_name
            episode.id          =   self.url_base + details.a['href']
            episode.description =   duration.contents[0] +' - '+ details.span.contents[0]
            episode.thumbnails  =   details.a.img['src']
            episode.date        =   time.contents[2]
            episode.page        =   page
            episode.totalpage   =   totalpage
            episodelist.append(episode)
        return episodelist

    def Genre(self, genre, filter, page, totalpage):
        url = 'http://mercury.itv.com/api/html/dotcom/Schedule/'
        data = tools.urlopen(self.app, url, {'cache':3600})
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES, smartQuotesTo="xml")

        if len(data) < 10:
            mc.ShowDialogNotification("No episode found for " + str(stream_name))
            return []

        day = soup.find('li',{'class':re.compile("^"+genre)})

        net = []

        if filter and filter != 'None':
            net.append(filter)
        else:
            for id in self.filter:
                net.append(id)
        if 'None' in net: net.remove('None')
        
        data = {}
        data_sorted = []
        for i in net:
            netdata = day.find('li',{'class':re.compile("^"+i)})
            for info in netdata.findAll(attrs={'class' : re.compile("^whatsOnTime")}):
                if info.a:
                    title = info.find('span',{'class':'title'})
                    time = info.find('span',{'class':'time'})
                    #date:[name,id,filter]
                    data[time.contents[0]] = [title.contents[0],self.url_base + info.a['href'],i]
        date = data.keys()
        date.sort(reverse=True)
        for i in date:
            data_sorted.append({'name':data[i][0],'id':data[i][1],'filter':data[i][2],'date':i})

        genrelist = list()
        for info_sorted in data_sorted:
            genreitem           =   CreateEpisode()
            genreitem.name      =   info_sorted['name']
            genreitem.id        =   info_sorted['id']
            genreitem.date      =   info_sorted['date']
            genreitem.filter    =   info_sorted['filter']
            genreitem.page      =   page
            genreitem.totalpage =   totalpage
            genrelist.append(genreitem)

        return genrelist

    def Play(self, stream_name, stream_id, subtitle):

        play            =   CreatePlay()
        play.path       =   quote_plus(stream_id)
        play.domain     =   'itv.com'
        play.jsactions  =   quote_plus('http://boxee.bartsidee.nl/js/itv.js')

        return play