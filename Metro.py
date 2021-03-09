from html.parser import HTMLParser
from unicodedata import normalize


class Metro (HTMLParser) : 
    def __init__(self) : 
        super(Metro, self).__init__()
        self.status = 'START'
        
        self.linename = ''
        self.lines = {}

    def getLines(self) : 
        return self.lines


    def handle_starttag(self, tag, attrs) :
        attrs = dict(attrs)

        if self.status == 'START' : 
            if tag == 'ul' and 'id' in attrs and attrs['id'] == 'statusLinhaMetro' : 
                self.status = 'UL#STATUS'

        elif self.status == 'UL#STATUS' : 
            if tag == 'div' and 'class' in attrs : 
                if attrs['class'] == 'nomeDaLinha' : 
                    self.status = 'UL#STATUS DIV.NOME'

                if attrs['class'] == 'statusDaLinha' : 
                    self.status = 'UL#STATUS DIV.STATUS'

        if self.status in ['UL#STATUS DIV.NOME', 'UL#STATUS DIV.STATUS'] : 
            if tag == 'span' : 
                self.status += ' SPAN'



    def handle_endtag(self, tag) :
        if self.status == 'UL#STATUS' : 
            if tag == 'ul' : 
                self.status = 'START'

        elif self.status in ['UL#STATUS DIV.NOME', 'UL#STATUS DIV.STATUS'] : 
            if tag == 'div' : 
                self.status = 'UL#STATUS'

        elif self.status == 'UL#STATUS DIV.NOME SPAN' : 
            if tag == 'span' : 
                self.status = 'UL#STATUS DIV.NOME'

        elif self.status == 'UL#STATUS DIV.STATUS SPAN' : 
            if tag == 'span' : 
                self.status = 'UL#STATUS DIV.STATUS'


    def handle_data(self, data) : 
        if self.status == 'UL#STATUS DIV.NOME SPAN' : 
            self.linename = data.strip()

        elif self.status == 'UL#STATUS DIV.STATUS SPAN' : 
            linenumb = int(self.linename.split(' ')[1].split('-')[0])
            linecolor = self.linename.split('-')[1]
            linestatus = data.strip()
            self.lines[linenumb] = {'color': linecolor, 'status': linestatus, 'operator': 'Metro'}

if __name__ == '__main__' : 
    pass

