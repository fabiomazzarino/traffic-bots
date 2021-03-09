from html.parser import HTMLParser
from unicodedata import normalize
from unidecode import unidecode


class CGE (HTMLParser) : 
    def __init__(self) : 
        super(CGE, self).__init__()
        self.status = 'START'
        self.local = ''
        self.direction = ''
        self.reference = ''
        self.floodtype = ''

        self.totalativos = 0
        self.floodings = []

    def getTotalAtivos(self) : 
        return self.totalativos

    def getFloodings(self) : 
        return self.floodings

    def handle_starttag(self, tag, attrs) :
        attrs = dict(attrs)

        if self.status == 'START' : 
            if tag == 'span' and 'class' in attrs and attrs['class'] == 'num-ativos' : 
                self.status = 'SPAN.NUMATIVOS'

            if tag == 'li' and 'class' in attrs : 
                if attrs['class'] == 'ativo-transitavel' : 
                    self.floodtype = 'TRANSITAVEL'
                elif attrs['class'] == 'ativo-intransitavel' : 
                    self.floodtype = 'INTRANSITAVEL'
                elif attrs['class'] == 'arial-descr-alag col-local' :
                    self.status = 'LI.LOCAL'
                elif attrs['class'] == 'arial-descr-alag' : 
                    self.status = 'LI.DESCR'


    def handle_endtag(self, tag) :
        if self.status == 'SPAN.NUMATIVOS' and tag == 'span' : 
            self.status = 'END'

        if self.status == 'LI.LOCAL' and tag == 'li' : 
            self.status = 'START'

        if self.status == 'LI.DESCR' and tag == 'li' : 
            self.status = 'START'

    def handle_data(self, data) : 
        if self.status == 'SPAN.NUMATIVOS' : 
            self.totalativos = int(data.strip())

        if self.status == 'LI.LOCAL' : 
            self.local = unidecode(data)

        if self.status == 'LI.DESCR' : 
            if data.find('Sentido:') != -1 : 
                self.direction = unidecode(data.split(':')[1].strip())

            elif data.find('Referência:') != -1 : 
                self.reference = unidecode(data.split(':')[1].strip())

                if self.floodtype == 'TRANSITAVEL' or self.floodtype == 'INTRANSITAVEL' : 
                    self.ref = data.split(':')[1].strip()
                    flooding = {}
                    flooding['local']= unidecode(self.local)
                    flooding['direction'] = unidecode(self.direction)
                    flooding['reference'] = unidecode(self.reference)
                    flooding['type'] = unidecode(self.floodtype)
                    self.floodings.append(flooding)

                    self.local = ''
                    self.direction = ''
                    self.reference = ''
                    self.floodtype = ''

if __name__ == '__main__' : 
    pass

