from fpdf import FPDF

# Генерує PDF-файл резюме на основі об'єкта CV з бази даних.
def create_pdf(cv, filename: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Підключаємо шрифти з підтримкою кирилиці
    pdf.add_font("ArialCustom", style="", fname="arial.ttf")
    pdf.add_font("ArialCustom", style="B", fname="arialbd.ttf")

    # Шапка: Ім'я та бажана посада
    pdf.set_font("ArialCustom", style="B", size=22)
    pdf.set_text_color(25, 25, 25)
    pdf.cell(0, 12, cv.name, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("ArialCustom", style="", size=14)
    pdf.set_text_color(45, 95, 175)
    pdf.cell(0, 8, cv.position, new_x="LMARGIN", new_y="NEXT")

    # Декоративна лінія-розділювач під шапкою
    pdf.ln(3)
    pdf.set_draw_color(45, 95, 175)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(7)

    # Допоміжна функція для оформлення секцій
    def add_section(title: str, content: str):
        pdf.set_font("ArialCustom", style="B", size=12)
        pdf.set_text_color(25, 25, 25)
        pdf.cell(0, 8, title.upper(), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("ArialCustom", style="", size=11)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(0, 6, content, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

    add_section("Контакти", cv.contacts)
    add_section("Ключові навички", cv.skills)
    add_section("Досвід та освіта", cv.experience)

    pdf.output(filename)