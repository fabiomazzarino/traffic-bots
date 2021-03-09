from html.parser import HTMLParser
from unicodedata import normalize


class CPTM (HTMLParser) : 
    def __init__(self) : 
        super(CPTM, self).__init__()
        self.status = 'START'
        self.lines = {}
        self.numbers = {'RUBI': 7, 'DIAMANTE': 8, 'ESMERALDA': 9, 'TURQUESA': 10, 'CORAL': 11, 'SAFIRA': 12, 'JADE': 13}


    def getLines(self) : 
        return self.lines

    def handle_starttag(self, tag, attrs) :
        attrs = dict(attrs)

        if self.status == 'START' : 
            if tag == 'div' and 'class' in attrs and attrs['class'].find(' situacao_linhas') != -1 : 
                self.status = 'DIV.SITUACAO'

        elif self.status == 'DIV.SITUACAO' : 
            if tag == 'span' and 'class' in attrs : 
                if attrs['class'] == 'nome_linha' : 
                    self.status = 'DIV.SITUACAO SPAN.NOME'

                elif attrs['class'].find('status') == 0 : 
                    self.status = 'DIV.SITUACAO SPAN.STATUS'


    def handle_endtag(self, tag) :
        if self.status in ['DIV.SITUACAO SPAN.NOME', 'DIV.SITUACAO SPAN.STATUS'] : 
            if tag == 'span' : 
                self.status = 'DIV.SITUACAO'

    def handle_data(self, data) : 
        if self.status == 'DIV.SITUACAO SPAN.NOME' : 
            self.linename = data.strip()

        elif self.status == 'DIV.SITUACAO SPAN.STATUS' : 
            linenumb = int(self.numbers[self.linename])
            linecolor = self.linename.capitalize()
            linestatus = data.strip()
            self.lines[linenumb] = {'color': linecolor, 'status': linestatus, 'operator': 'CPTM'}



if __name__ == '__main__' : 
    pass

