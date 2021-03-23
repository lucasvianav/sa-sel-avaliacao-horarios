from config import sheets
from datetime import date
from re import search, sub
from requests import get
from bs4 import BeautifulSoup

JUPITER_URI = 'https://uspdigital.usp.br/jupiterweb/obterTurma?sgldis='

hasSameParity = lambda x, y: (x % 2 == 0) == (y % 2 == 0)

# Primeiro ou segundo semestre do ano?
currentSemester = 1 if date.today().month <= 7 else 2

# Planilhas com as disciplinas do semestre atual 
currentSheets = filter(lambda sh: search('^\d Período$', sh.title) and hasSameParity(sub('^(\d) Período$', '\1', sh.title), currentSemester), sheets)

courses = []

for sh in currentSheets:
    values = sh.get_all_values()
    
    # Remove a linha com o header da planilha
    values.pop(0)
    
    for course in values:
        html = get(JUPITER_URI + course[0])
        soup = BeautifulSoup('html', 'html.parser')
        
        classes = soup.find('td', width=568).find_all('div', recursive=False)
        
        for class in classes:
            blocks = class.find_all('table')
            classCode = sub('\D', '', blocks[0].find('tr').find_all('td')[1].text)
            
            times = blocks[1].find_all('tr')
            times.pop(0)
            
            times = [ list(map(lambda td: td.text.strip(), t.find_all('td'))) for t in times ]