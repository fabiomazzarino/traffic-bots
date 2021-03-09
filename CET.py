from html.parser import HTMLParser
from unicodedata import normalize


class CET (HTMLParser) : 
    def __init__(self) : 
        super(CET, self).__init__()
        self.status = 'START'

        self.north = 0
        self.south = 0
        self.east = 0
        self.west = 0
        self.downtown = 0

    def getTotal(self) : 
        return self.north + self.south + self.east + self.west + self.downtown

    def getNorth(self) : 
        return self.north

    def getSouth(self) : 
        return self.south

    def getEast(self) : 
        return self.east

    def getWest(self) : 
        return self.west

    def getDowntown(self) : 
        return self.downtown

    def handle_starttag(self, tag, attrs) :
        attrs = dict(attrs)

        if self.status == 'START' : 
            if tag == 'div' and 'class' in attrs : 
                if attrs['class'] == 'info norte' : 
                    self.status = 'DIV.NORTE'
                elif attrs['class'] == 'info sul' : 
                    self.status = 'DIV.SUL'
                elif attrs['class'] == 'info leste' : 
                    self.status = 'DIV.LESTE'
                elif attrs['class'] == 'info oeste' : 
                    self.status = 'DIV.OESTE'
                elif attrs['class'] == 'info centro' : 
                    self.status = 'DIV.CENTRO'

        elif self.status == 'DIV.NORTE' :
            if tag == 'h4' : 
                self.status = 'DIV.NORTE.H4'

        elif self.status == 'DIV.SUL' : 
            if tag == 'h4' : 
                self.status = 'DIV.SUL.H4'
  
        elif self.status == 'DIV.LESTE' : 
            if tag == 'h4' : 
                self.status = 'DIV.LESTE.H4'
        
        elif self.status == 'DIV.OESTE' : 
            if tag == 'h4' : 
                self.status = 'DIV.OESTE.H4'

        elif self.status == 'DIV.CENTRO' : 
            if tag == 'h4' : 
                self.status = 'DIV.CENTRO.H4'
 


    def handle_endtag(self, tag) :
        if self.status in ['DIV.NORTE', 'DIV.SUL', 'DIV.LESTE', 'DIV.OESTE', 'DIV.CENTRO'] : 
            if tag == 'div' : 
                self.status = 'START'

        elif self.status == 'DIV.NORTE.H4' :
            if tag == 'h4' : 
                self.status = 'DIV.NORTE'

        elif self.status == 'DIV.SUL.H4' :
            if tag == 'h4' : 
                self.status = 'DIV.SUL'

        elif self.status == 'DIV.LESTE.H4' :
            if tag == 'h4' : 
                self.status = 'DIV.LESTE'

        elif self.status == 'DIV.OESTE.H4' :
            if tag == 'h4' : 
                self.status = 'DIV.OESTE'

        elif self.status == 'DIV.CENTRO.H4' :
            if tag == 'h4' : 
                self.status = 'DIV.CENTRO'


    def handle_data(self, data) : 
        if self.status == 'DIV.NORTE.H4' : 
            self.north = int(data.split(' ')[0])

        if self.status == 'DIV.SUL.H4' : 
            self.south = int(data.split(' ')[0])

        if self.status == 'DIV.LESTE.H4' : 
            self.east= int(data.split(' ')[0])

        if self.status == 'DIV.OESTE.H4' : 
            self.west = int(data.split(' ')[0])

        if self.status == 'DIV.CENTRO.H4' : 
            self.downtown= int(data.split(' ')[0])


if __name__ == '__main__' : 
    pass

