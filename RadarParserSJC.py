

from html.parser import HTMLParser
from unicodedata import normalize


class RadarParserSJC (HTMLParser) : 
    def __init__(self) : 
        super(RadarParserSJC, self).__init__()
        self.status = 'START'

        self.ctdates = 0
        self.ctlocations = 0

        self.dates = []
        self.locations = []

        self.radars = dict()

    def getRadars(self) : 
        return self.radars

    def handle_starttag(self, tag, attrs) :
        attrs = dict(attrs)

        if self.status == 'START' : 
            if tag == 'div' and 'id' in attrs and attrs['id'] == 'corpo' : 
                self.status = 'DIV#CORPO'

        elif self.status == 'DIV#CORPO' : 
            if tag == 'td' : 
                self.status = 'TD'

        elif self.status == 'TD' : 
            if tag == 'span' and 'class' in attrs and attrs['class'] == 'texto' : 
                self.status = 'SPAN.TEXTO'
                if len(attrs['id'].split('_')) == 18 : 
                    self.status = 'SPAN.TEXTO-DATE'
                    self.date = ''
                else : 
                    self.status = 'SPAN.TEXTO-LOCATIONS'
                    self.locations = []


    def handle_endtag(self, tag) :
        if self.status == 'SPAN.TEXTO-DATE' and tag == 'span' : 
            self.dates.append(self.date)
            self.ctdates += 1
            self.status = 'TD'

        elif self.status == 'SPAN.TEXTO-LOCATIONS' and tag == 'span' :
            thisdate = self.dates[self.ctlocations]
            self.radars[thisdate] = self.locations 
            self.ctlocations += 1
            self.status = 'TD'

        elif self.status == 'TD' and tag == 'td' : 
            self.status = 'DIV#CORPO'

        elif self.status == 'DIV#CORPO' and tag == 'div' : 
            self.status = 'FINISH'

    def handle_data(self, data) : 
        if self.status == 'SPAN.TEXTO-DATE' : 
            self.date = data.strip()

        elif self.status == 'SPAN.TEXTO-LOCATIONS' :
            data = data.strip().replace('\t', ' ')
            location = {
                'street': data.split('(')[0].strip(), 
                'area': data.split(')')[1].strip(), 
                'speed': data.split('(')[1].split(')')[0].strip()  
            }
            self.locations.append(location)

if __name__ == '__main__' : 
    pass
