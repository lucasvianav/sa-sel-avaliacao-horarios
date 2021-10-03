import csv
from datetime import date
from functools import reduce
from re import search, sub

from bs4 import BeautifulSoup
from requests import get

from config import sheets
from util import ENG_NAME, JUPITER_URI, extract_sheet_semester, has_same_parity, weekday

# first vs. second semester
current_semester = 1 if date.today().month <= 7 else 2

# sheets containing the current semester's courses
current_sheets = [
    sh
    for sh in sheets
    if search(r"^\dº? Período$", sh.title)
    and has_same_parity(extract_sheet_semester(sh.title), current_semester)
]

# all researched info
info = []

# for each period in the sheet
for sh in current_sheets:
    # current period's list of courses to be researched
    current_period = [[e.strip() for e in c] for c in sh.get_all_values()]

    # removes the sheet's header
    current_period.pop(0)

    # for each course in the current period
    for course in current_period:
        # fetches Júpiter's source code
        r = get(JUPITER_URI + course[0])
        html = r.text

        # if the course is not being offered
        if search(f"N.o existe oferecimento para a sigla {course[0]}.", html):
            continue

        # parses the HTML
        soup = BeautifulSoup(html, "html.parser")

        # this course's classes
        classes = soup.find("td", attrs={"width": "568"}).find_all(
            "div", recursive=False
        )

        # for each offered class_ ("class"
        # is a reserved work in python)
        for class_ in classes:
            # blocks of information inside this class's div
            blocks = class_.find_all("table")

            # current class's id
            class_code = sub(r"\D", "", blocks[0].find("tr").find_all("td")[1].text)

            schedule = blocks[1].find_all("tr")
            schedule.pop(0)

            # list of lists with day, start time, end
            # time and teacher's name (respectively)
            schedule = [[td.text.strip() for td in t.find_all("td")] for t in schedule]

            # checks if "Engenharia Elétrica" is in this class
            # (written in any way supported by ENG_NAME)
            def reducer_fn(acc, cur):
                return acc or cur in blocks[2].text.lower()

            has_elétrica = reduce(reducer_fn, ENG_NAME, False)

            # saves the classe's info
            if has_elétrica:
                for sch in schedule:
                    # TODO: class with 2 teachers?
                    # https://i.imgur.com/SbmXkUp.png
                    if not sch[0]:
                        continue

                    info.append(
                        {
                            "CÓDIGO DA DISCIPLINA": course[0],
                            "NOME DA DISCIPLINA": course[1],
                            "CÓDIGO DA TURMA": class_code,
                            "DIA DA AULA": weekday(sch[0]),
                            "INÍCIO DA AULA": sch[1],
                            "TÉRMINO DA AULA": sch[2],
                            "PROFESSOR": sch[3],
                            "TIPO DA DISCIPLINA": course[2],
                        }
                    )

# export to .csv
if info:
    with open(f"av-profs-disc--output__{str(date.today())}.csv", "w") as f:
        writer = csv.DictWriter(f, fieldnames=list(info[0].keys()), delimiter="%")
        writer.writeheader()

        writer.writerows(info)
