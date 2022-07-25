import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def create_pdf(title, ingredients):

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    pdfmetrics.registerFont(
        TTFont('FreeSans', 'FreeSans.ttf'))

    p.setFont('FreeSans', 20)
    y = 810
    p.drawString(55, y, f'{title}')
    y -= 30

    p.setFont('FreeSans', 14)
    string_number = 1
    for ingredient in ingredients:
        p.drawString(
            15, y,
            (f'{string_number}.'
             f'{ingredient.name.capitalize()}'
             f'({ingredient.measurement_unit}) - {ingredient.amount}'
             )
        )
        y -= 20
        string_number += 1

    p.showPage()
    p.save()
    buffer.seek(0)

    return buffer
