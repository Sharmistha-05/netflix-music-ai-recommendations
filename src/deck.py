"""Slide-building helpers (python-pptx) in the visual language of the earlier
Netflix Music deck: red top rule, dark section dividers, light panels with red
caps labels, Arial for portability (renders the same in PowerPoint, Keynote,
Google Slides and LibreOffice)."""
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

RED = RGBColor(0xE5, 0x09, 0x14)
INK = RGBColor(0x1A, 0x1A, 0x1A)
INK2 = RGBColor(0x5F, 0x5F, 0x5F)
PANEL = RGBColor(0xF5, 0xF5, 0xF4)
PINK = RGBColor(0xFD, 0xE8, 0xE9)
LINE = RGBColor(0xDD, 0xDD, 0xDD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x14, 0x14, 0x14)
HEAD = RGBColor(0x26, 0x26, 0x26)
GREEN = RGBColor(0x3A, 0x9D, 0x5D)
AMBER = RGBColor(0xC2, 0x87, 0x00)
FONT = "Arial"
MONO = "Courier New"


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        self.blank = self.prs.slide_layouts[6]

    # ------------------------------------------------------------------ primitives
    def text(self, s, x, y, w, h, text, size=14, color=INK, bold=False, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, font=FONT, spacing=0.35, italic=False):
        """text: str, or list of paragraphs; a paragraph may be a list of runs
        (str, or (str, {"bold":..., "color":..., "size":...}))."""
        tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = Inches(0.04)
        tf.margin_top = tf.margin_bottom = Inches(0.02)
        paras = text if isinstance(text, list) else [text]
        for i, para in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            p.space_after = Pt(size * spacing)
            runs = para if isinstance(para, list) else [para]
            for run in runs:
                txt, st = (run, {}) if isinstance(run, str) else run
                r = p.add_run()
                r.text = txt
                f = r.font
                f.name = st.get("font", font)
                f.size = Pt(st.get("size", size))
                f.bold = st.get("bold", bold)
                f.italic = st.get("italic", italic)
                f.color.rgb = st.get("color", color)
        return tb

    def rect(self, s, x, y, w, h, fill, line=None, shape=MSO_SHAPE.RECTANGLE, radius=None):
        sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
        if line is None:
            sh.line.fill.background()
        else:
            sh.line.color.rgb = line
            sh.line.width = Pt(0.75)
        sh.shadow.inherit = False
        if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
            sh.adjustments[0] = radius
        return sh

    def shape_text(self, sh, text, size=12, color=INK, bold=False, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE):
        tf = sh.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        tf.margin_left = tf.margin_right = Inches(0.06)
        tf.margin_top = tf.margin_bottom = Inches(0.03)
        lines = text if isinstance(text, list) else [text]
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = align
            runs = line if isinstance(line, list) else [line]
            for run in runs:
                txt, st = (run, {}) if isinstance(run, str) else run
                r = p.add_run()
                r.text = txt
                r.font.name = FONT
                r.font.size = Pt(st.get("size", size))
                r.font.bold = st.get("bold", bold)
                r.font.color.rgb = st.get("color", color)
        return sh

    def box(self, s, x, y, w, h, text, fill=PANEL, size=12, color=INK, bold=False, line=None,
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, rounded=True):
        sh = self.rect(s, x, y, w, h, fill, line, MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
                       radius=0.08 if rounded else None)
        return self.shape_text(sh, text, size, color, bold, align, anchor)

    def arrow(self, s, x, y, w=0.35, h=0.3, color=RED):
        return self.rect(s, x, y, w, h, color, shape=MSO_SHAPE.RIGHT_ARROW)

    def down_arrow(self, s, x, y, w=0.3, h=0.3, color=RED):
        return self.rect(s, x, y, w, h, color, shape=MSO_SHAPE.DOWN_ARROW)

    def notes(self, s, text):
        s.notes_slide.notes_text_frame.text = text

    def image(self, s, path, x, y, w, h, align="center"):
        """Place an image inside the box (x, y, w, h), keeping its aspect ratio."""
        iw, ih = Image.open(path).size
        scale = min(w / iw, h / ih)
        pw, ph = iw * scale, ih * scale
        px = x + (w - pw) / 2 if align == "center" else x
        py = y + (h - ph) / 2
        return s.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(pw), Inches(ph))

    # ------------------------------------------------------------------ slide types
    def base(self, title, subtitle=None, source=None):
        s = self.prs.slides.add_slide(self.blank)
        self.rect(s, 0, 0, 13.333, 0.1, RED)
        tsize = 26 if len(title) <= 56 else (23 if len(title) <= 64 else 21)
        self.text(s, 0.6, 0.38, 12.1, 0.7, title, size=tsize, bold=True)
        if subtitle:
            self.text(s, 0.6, 1.05, 12.1, 0.45, subtitle, size=14, color=INK2)
        if source:
            self.text(s, 0.6, 7.03, 10.5, 0.3, "Source: " + source, size=9, color=INK2)
        self.text(s, 11.9, 7.03, 0.85, 0.3, str(len(self.prs.slides)), size=9, color=INK2, align=PP_ALIGN.RIGHT)
        return s

    def section(self, part, title, subtitle):
        s = self.prs.slides.add_slide(self.blank)
        self.rect(s, 0, 0, 13.333, 7.5, DARK)
        self.rect(s, 0, 0, 13.333, 0.1, RED)
        self.text(s, 0.9, 2.45, 11, 0.4, part.upper(), size=14, color=RED, bold=True)
        self.text(s, 0.9, 2.9, 11.8, 1.1, title, size=42 if len(title) <= 34 else 34, color=WHITE, bold=True)
        self.text(s, 0.9, 4.05, 11, 0.9, subtitle, size=18, color=RGBColor(0xBF, 0xBF, 0xBF))
        self.text(s, 11.9, 7.03, 0.85, 0.3, str(len(self.prs.slides)), size=9,
                  color=RGBColor(0x8A, 0x8A, 0x8A), align=PP_ALIGN.RIGHT)
        return s

    # ------------------------------------------------------------------ components
    def card(self, s, x, y, w, h, label, body, fill=PANEL, size=12, label_color=RED, body_color=INK, bullets=False):
        self.rect(s, x, y, w, h, fill)
        self.text(s, x + 0.2, y + 0.16, w - 0.4, 0.3, label.upper(), size=11, bold=True, color=label_color)
        items = body if isinstance(body, list) else [body]
        if bullets:
            items = [[("•  ", {"color": RED, "bold": True}), it] if isinstance(it, str) else [("•  ", {"color": RED, "bold": True})] + it
                     for it in items]
        self.text(s, x + 0.2, y + 0.5, w - 0.4, h - 0.6, items, size=size, color=body_color, spacing=0.45)

    def bullets(self, s, x, y, w, h, items, size=14, spacing=0.55, color=INK):
        """items: str, or (lead, rest) to bold a lead-in."""
        paras = []
        for it in items:
            if isinstance(it, tuple):
                paras.append([("•  ", {"color": RED, "bold": True}), (it[0], {"bold": True}), " " + it[1]])
            else:
                paras.append([("•  ", {"color": RED, "bold": True}), it])
        return self.text(s, x, y, w, h, paras, size=size, spacing=spacing, color=color)

    def kpi(self, s, x, y, w, h, value, label, fill=PANEL, vcolor=RED):
        self.rect(s, x, y, w, h, fill)
        self.text(s, x + 0.15, y + 0.12, w - 0.3, h * 0.5, value, size=26, bold=True, color=vcolor)
        self.text(s, x + 0.15, y + h * 0.55, w - 0.3, h * 0.42, label, size=11, color=INK2)

    def code(self, s, x, y, w, h, code, size=10.5, title=None):
        self.rect(s, x, y, w, h, RGBColor(0x1E, 0x1E, 0x1E))
        top = y + 0.12
        if title:
            self.text(s, x + 0.2, top, w - 0.4, 0.3, title, size=10, bold=True, color=RGBColor(0xFF, 0x8A, 0x8F))
            top += 0.34
        self.text(s, x + 0.2, top, w - 0.4, h - (top - y) - 0.1, code.split("\n"), size=size,
                  color=RGBColor(0xE8, 0xE8, 0xE8), font=MONO, spacing=0.08)

    def table(self, s, x, y, col_w, rows, size=11, row_h=0.38, header_fill=HEAD, zebra=True,
              bold_first_col=False, highlight=None, header_size=None, col_align=None):
        """rows[0] is the header. highlight: dict row_index -> fill colour."""
        n_r, n_c = len(rows), len(rows[0])
        gs = s.shapes.add_table(n_r, n_c, Inches(x), Inches(y), Inches(sum(col_w)), Inches(row_h * n_r))
        tbl = gs.table
        tbl.first_row = True
        tbl.horz_banding = False
        for j, w in enumerate(col_w):
            tbl.columns[j].width = Inches(w)
        for i in range(n_r):
            tbl.rows[i].height = Inches(row_h)
            for j in range(n_c):
                c = tbl.cell(i, j)
                c.margin_left = c.margin_right = Inches(0.08)
                c.margin_top = c.margin_bottom = Inches(0.04)
                c.vertical_anchor = MSO_ANCHOR.MIDDLE
                c.fill.solid()
                if i == 0:
                    c.fill.fore_color.rgb = header_fill
                elif highlight and i in highlight:
                    c.fill.fore_color.rgb = highlight[i]
                else:
                    c.fill.fore_color.rgb = PANEL if (zebra and i % 2 == 0) else WHITE
                val = rows[i][j]
                runs = val if isinstance(val, list) else [val]
                tf = c.text_frame
                tf.word_wrap = True
                p = tf.paragraphs[0]
                if col_align and col_align[j]:
                    p.alignment = col_align[j]
                for run in runs:
                    txt, st = (str(run), {}) if not isinstance(run, tuple) else run
                    r = p.add_run()
                    r.text = txt
                    r.font.name = FONT
                    r.font.size = Pt(header_size or size) if i == 0 else Pt(st.get("size", size))
                    r.font.bold = True if i == 0 else st.get("bold", bold_first_col and j == 0)
                    r.font.color.rgb = WHITE if i == 0 else st.get("color", INK)
        return gs

    def save(self, path):
        self.prs.save(str(path))
