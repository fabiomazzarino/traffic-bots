from html.parser import HTMLParser
from unicodedata import normalize


class SAISP (HTMLParser) : 
    def __init__(self) : 
        super(SAISP, self).__init__()
        self.status = 'START'

        self.pluvnow = 0
        self.pluvprev = 0
        self.umidity = 0

    def getPluv(self) : 
        return round(self.pluvnow - self.pluvprev, 1)

    def getUmidity(self) : 
        return self.umidity


    def handle_starttag(self, tag, attrs) :
        attrs = dict(attrs)

        if self.status == 'START' : 
            if tag == 'tbody' and 'id' in attrs and attrs['id'] == 'tbTelemBody' : 
                self.status = 'TBODY#TELEM'

        elif self.status == 'TBODY#TELEM' : 
            if tag == 'table' : 
                self.status = 'TBODY#TELEM TABLENOW'

        elif self.status == 'TBODY#TELEM TABLENOW' : 
            if tag == 'td' :
                self.status = 'TBODY#TELEM TABLENOW TD'

        elif self.status == 'TBODY#TELEM SEARCHTR' : 
            if tag == 'tr' and 'class' in attrs and attrs['class'] == 'linhaEscura' : 
                self.status = 'TBODY#TELEM SEARCHTABLE'

        elif self.status == 'TBODY#TELEM SEARCHTABLE' : 
            if tag == 'table' : 
                self.status = 'TBODY#TELEM TABLEPREV' 

        elif self.status == 'TBODY#TELEM TABLEPREV' : 
            if tag == 'td' : 
                self.status = 'TBODY#TELEM TABLEPREV TD'


    def handle_endtag(self, tag) :
        if self.status == 'TBODY#TELEM TABLENOW TD' : 
            if tag == 'td' : 
                self.status = 'TBODY#TELEM SEARCHTR'

        if self.status == 'TBODY#TELEM TABLEPREV TD' : 
            if tag == 'td' : 
                self.status = 'END'

    def handle_data(self, data) : 
        if self.status == 'TBODY#TELEM TABLENOW TD' : 
            self.pluvnow = round(float(data), 1)

        elif self.status == 'TBODY#TELEM TABLEPREV TD' : 
            self.pluvprev = round(float(data), 1)


if __name__ == '__main__' : 
    pass

