from config import sheets
from datetime import date
from re import search, sub
from requests import get
from bs4 import BeautifulSoup
from functools import reduce
import csv

JUPITER_URI = 'https://uspdigital.usp.br/jupiterweb/obterTurma?sgldis='

hasSameParity = lambda x, y: (x % 2 == 0) == (y % 2 == 0)
weekday = lambda string: {
    'seg': 'Segunda-Feira',
    'ter': 'Terça-Feira',
    'qua': 'Quarta-Feira',
    'qui': 'Quinta-Feira',
    'sex': 'Sexta-Feira',
    'sab': 'Sábado',
    'dom': 'Domingo',
    '2': 'Segunda-Feira',
    '3': 'Terça-Feira',
    '4': 'Quarta-Feira',
    '5': 'Quinta-Feira',
    '6': 'Sexta-Feira',
    '7': 'Sábado',
    '1': 'Domingo',
    'segunda': 'Segunda-Feira',
    'terça': 'Terça-Feira',
    'terca': 'Terça-Feira',
    'quarta': 'Quarta-Feira',
    'quinta': 'Quinta-Feira',
    'sexta': 'Sexta-Feira',
    'sabado': 'Sábado',
    'segunda-feira': 'Segunda-Feira',
    'terça-feira': 'Terça-Feira',
    'quarta-feira': 'Quarta-Feira',
    'quinta-feira': 'Quinta-Feira',
    'sexta-feira': 'Sexta-Feira',
}[string.lower()]

# Primeiro ou segundo semestre do ano?
currentSemester = 1 if date.today().month <= 7 else 2

# Planilhas com as disciplinas do semestre atual 
currentSheets = list(filter(lambda sh: search('^\dº? Período$', sh.title) and hasSameParity(int(sub('^(\d)º? Período$', '\g<1>', sh.title)), currentSemester), sheets))

# Todas as informações pesquisadas
info = []

# Para cada período da planilha
for sh in currentSheets:
    # Lista de disciplinas do período atual a serem pesquisadas
    courses = list(map(lambda c: [e.strip() for e in c], sh.get_all_values()))
    
    # Remove a linha com o header da planilha
    courses.pop(0)
    
    # Para cada disciplina do período atual
    for course in courses:
        # Pega o código HTML da página do Júpiter
        r = get(JUPITER_URI + course[0])
        html = r.text
        
        # Se aquela disciplina não está sendo oferecida, passa pra próxima
        if search(f'N.o existe oferecimento para a sigla {course[0]}.', html): continue

        # Parseia o código HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # Lista com as turmas dessa disciplina
        classes = soup.find('td', attrs={'width': '568'}).find_all('div', recursive=False)
        
        # Para cada turma sendo oferecida dessa disciplina
        for class_ in classes:
            # Blocos de informação dentro da div dessa turma
            blocks = class_.find_all('table')
            
            # Código da turma atual
            classCode = sub('\D', '', blocks[0].find('tr').find_all('td')[1].text)
            
            schedule = blocks[1].find_all('tr')
            schedule.pop(0)
            
            # Lista de listas com, respectivamente, dia, horário de início, 
            # horário de término e nome do professor de cada aula dessa turma
            schedule = [ list(map(lambda td: td.text.strip(), t.find_all('td'))) for t in schedule ]
            
            # Jeitos de se escrever "Engenharia Elétrica"
            availableOptions = ['eng elétrica', 'eng eletrica', 'eng. elétrica', 'eng. eletrica', 'engenharia elétrica', 'engenharia eletrica']
            
            # A disciplina é oferecida para a Elétrica?
            # Checa se a Engenharia Elétrica na lista de cursos
            hasElétrica = reduce(lambda acc, cur: acc or cur in blocks[2].text.lower(), availableOptions, False)
            
            # Se aquela turma é oferecida para a Elétrica,
            # anexa as informações daquela turma no array
            # que será usado para o output
            if hasElétrica:
                for sch in schedule: info.append({
                    'CÓDIGO DA DISCIPLINA': course[0],
                    'NOME DA DISCIPLINA': course[1],
                    'CÓDIGO DA TURMA': classCode,
                    'DIA DA AULA': weekday(sch[0]),
                    'INÍCIO DA AULA': sch[1],
                    'TÉRMINO DA AULA': sch[2],
                    'PROFESSOR': sch[3],
                    'TIPO DA DISCIPLINA': course[2]
                })

# Se tiver pelo menos uma disciplina no array
# escreve todas as informações num arquivo .csv
if len(info):
    with open(f'av-profs-disc--output__{str(date.today())}.csv', 'w') as f:
        writer = csv.DictWriter(f, fieldnames=list(info[0].keys()), delimiter='%')
        writer.writeheader()
        writer.writerows(info)