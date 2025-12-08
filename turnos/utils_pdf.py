# turnos/utils_pdf.py
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
import tempfile

def generar_receta_pdf(turno):
    html_string = render_to_string('turnos/receta_template.html', {'turno': turno})
    html = HTML(string=html_string, base_url='')  # base_url si hay assets
    result = html.write_pdf()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receta_{turno.pk}.pdf'
    response.write(result)
    return response
