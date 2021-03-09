from html.parser import HTMLParser
from unicodedata import normalize

import os.path


class Cameras (HTMLParser) : 
    def __init__(self) : 
        super(Cameras, self).__init__()
        self.status = 'START'

        self.images = []


    def handle_starttag(self, tag, attrs) :
        attrs = dict(attrs)

        if self.status == 'START' : 
            if tag == 'div' and 'id' in attrs and attrs['id'] == 'barraLista' : 
                self.status = '#LISTA'

        elif self.status == '#LISTA' : 
            if tag == 'div' and 'class' in attrs and attrs['class'] == 'chkboxtexto' : 
                self.status = '#LISTA #CHECKBOX'

        elif self.status == '#LIST #CHECKBOX'
            if tag == 'img' and 'src' in attrs : 
                self.image = os.path.basename(attrs['src'])

    def handle_endtag(self, tag) :
        if status == '#LISTA' : 
            self.status = 'END'
        elif status == '#LISTA #CHECKBOX' : 
            if tag == 'div' : 
                self.status = '#LISTA'


    def handle_data(self, data) : 
        if self.status == '#LIST #CHECKBOX' : 
            self.images.append({'addr': data.strip(), 'image': self.image})

if __name__ == '__main__' : 
    pass

