from html.parser import HTMLParser
from unicodedata import normalize


class SPTrans (HTMLParser) : 
    def __init__(self) : 
        super(SPTrans, self).__init__()
        self.status = 'START'
        
        self.direction = ''
        self.speeddowntown = 0
        self.speeduptown = 0

    def getSpeedDowntown(self) : 
        return self.speeddowntown

    def getSpeedUptown(self) : 
        return self.speeduptown


    def handle_starttag(self, tag, attrs) :
        attrs = dict(attrs)

        if self.status == 'START' : 
            if tag == 'div' and 'class' in attrs : 
                if attrs['class'].find('destino-olho-vivo') != -1 : 
                    self.status = 'DIV.DESTINO'
                if attrs['class'].find('velocidade-olho-vivo') != -1 : 
                    self.status = 'DIV.VELOCIDADE'

    def handle_endtag(self, tag) :
        if self.status in ['DIV.DESTINO', 'DIV.VELOCIDADE'] : 
            if tag == 'div' : 
                self.status = 'START'

    def handle_data(self, data) : 
        if self.status == 'DIV.DESTINO' : 
            if data == 'Bairro > Centro' : 
                self.direction = 'downtown'

            elif data == 'Centro > Bairro' : 
                self.direction = 'uptown'

        elif self.status == 'DIV.VELOCIDADE' : 
            if self.direction == 'downtown' : 
                self.speeddowntown = data.strip().split('k')[0]
            elif self.direction == 'uptown' : 
                self.speeduptown = data.strip().split('k')[0]

if __name__ == '__main__' : 
    pass

