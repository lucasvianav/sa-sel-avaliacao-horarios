from re import sub

JUPITER_URI = "https://uspdigital.usp.br/jupiterweb/obterTurma?sgldis="

ENG_NAME = [
    "eng elétrica",
    "eng eletrica",
    "eng. elétrica",
    "eng. eletrica",
    "engenharia elétrica",
    "engenharia eletrica",
]

ELETR_NAME = [
    "eletrônica",
    "eletronica",
    "eletro",
]

AUTOMA_NAME = [
    "energia",
    "autom",
    "energia e autom",
    "automação",
    "automacao",
    "sistemas de energia",
    "sistemas",
    "sis energia e autom",
]


def has_same_parity(x, y):
    x = int(x)
    y = int(y)
    return (x % 2 == 0) == (y % 2 == 0)


def weekday(string):
    return {
        "seg": "Segunda-Feira",
        "ter": "Terça-Feira",
        "qua": "Quarta-Feira",
        "qui": "Quinta-Feira",
        "sex": "Sexta-Feira",
        "sab": "Sábado",
        "dom": "Domingo",
        "2": "Segunda-Feira",
        "3": "Terça-Feira",
        "4": "Quarta-Feira",
        "5": "Quinta-Feira",
        "6": "Sexta-Feira",
        "7": "Sábado",
        "1": "Domingo",
        "segunda": "Segunda-Feira",
        "terça": "Terça-Feira",
        "terca": "Terça-Feira",
        "quarta": "Quarta-Feira",
        "quinta": "Quinta-Feira",
        "sexta": "Sexta-Feira",
        "sabado": "Sábado",
        "segunda-feira": "Segunda-Feira",
        "terça-feira": "Terça-Feira",
        "quarta-feira": "Quarta-Feira",
        "quinta-feira": "Quinta-Feira",
        "sexta-feira": "Sexta-Feira",
    }[string.lower()]


def extract_sheet_semester(title):
    return sub(r"^(\d)º? Período$", r"\g<1>", title)
