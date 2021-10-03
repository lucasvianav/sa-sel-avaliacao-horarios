import csv
from datetime import date
from functools import reduce
from logging import exception
from re import search, sub

from bs4 import BeautifulSoup
from requests import get

from config import sheets
from util import (
    AUTOMA_NAME,
    ELETR_NAME,
    ENG_NAME,
    JUPITER_URI,
    extract_sheet_semester,
    has_same_parity,
    weekday,
)

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
            general_info = blocks[0].find_all("td")

            for i in range(len(general_info)):
                line = sub(r"\W", "", general_info[i].text.lower())

                if "códigodaturma" in line:
                    class_code = general_info[i + 1].text.strip()
                elif "tipodaturma" in line:
                    class_type = general_info[i + 1].text.strip()

            schedule = blocks[1].find_all("tr")
            schedule.pop(0)  # "Horário      Prof(a)."

            # list of lists with day, start time, end
            # time and teacher's name (respectively)
            schedule = [[td.text.strip() for td in t.find_all("td")] for t in schedule]

            careers = blocks[2].find_all("tr")

            # checks if "Engenharia Elétrica" is in this class
            # (written in any way supported by ENG_NAME)
            def get_reducer_fn(row):
                def reducer_fn(acc, cur):
                    return acc or cur in row.lower()

                return reducer_fn

            no_students = {
                "eletrônica": 0,
                "automa": 0,
                "unificado": 0,
            }

            has_elétrica = False
            for row in careers:
                cols = row.text.strip().split("\n")

                try:
                    career = cols[0]
                    students = cols[2]
                except IndexError:
                    continue

                is_elétrica = reduce(get_reducer_fn(career), ENG_NAME, False)

                if not is_elétrica:
                    continue

                is_eletrônica = reduce(get_reducer_fn(career), ELETR_NAME, False)
                is_automa = reduce(get_reducer_fn(career), AUTOMA_NAME, False)

                if is_eletrônica == is_automa:  # (if both are True or False)
                    no_students["unificado"] = students
                elif is_eletrônica:
                    no_students["eletrônica"] = students
                else:
                    no_students["automa"] = students

                has_elétrica = True

            # saves the classe's info
            if has_elétrica:
                for i, sch in enumerate(schedule):
                    # TODO: class with 2 teachers?
                    # https://i.imgur.com/SbmXkUp.png
                    if not sch[0]:
                        continue

                    if info:
                        # if the current row doesn't have a teacher
                        # copy it from the last one
                        if not sch[3]:
                            if class_code == info[-1]["CÓDIGO DA TURMA"]:
                                sch[3] = info[-1]["DOCENTE"]

                        # if the last row doesn't have a teacher
                        # copy it from this one
                        elif not info[-1]["DOCENTE"]:
                            if class_code == info[-1]["CÓDIGO DA TURMA"]:
                                info[-1]["DOCENTE"] = sch[3]

                    info.append(
                        {
                            "CÓDIGO DA DISCIPLINA": course[0],
                            "NOME DA DISCIPLINA": course[1],
                            "TIPO": course[2],
                            "CLASSE": class_type,
                            "CÓDIGO DA TURMA": class_code,
                            "DIA DA AULA": weekday(sch[0]),
                            "INÍCIO DA AULA": sch[1],
                            "TÉRMINO DA AULA": sch[2],
                            "DOCENTE": sch[3],
                            "INSCRITOS UNIFICADO": no_students["unificado"],
                            "INSCRITOS ELETRÔNICA": no_students["eletrônica"],
                            "INSCRITOS AUTOMA": no_students["automa"],
                        }
                    )

# export to .csv
if info:
    title = f"av-profs-disc--output__{str(date.today())}.csv"
    with open(title, "w") as f:
        writer = csv.DictWriter(f, fieldnames=list(info[0].keys()), delimiter="%")
        writer.writeheader()
        writer.writerows(info)
