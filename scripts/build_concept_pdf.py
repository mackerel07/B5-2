"""Build the illustrated Korean Mini Redis concept guide as a PDF."""

from html import escape
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "B5-2_Mini_Redis_개념서.pdf"
FONT_PATH = Path.home() / "Library" / "Fonts" / "NotoSansKR-VariableFont_wght.ttf"

NAVY = colors.HexColor("#172554")
BLUE = colors.HexColor("#2563EB")
SKY = colors.HexColor("#E0F2FE")
CYAN = colors.HexColor("#0891B2")
GREEN = colors.HexColor("#059669")
MINT = colors.HexColor("#D1FAE5")
ORANGE = colors.HexColor("#EA580C")
AMBER = colors.HexColor("#FEF3C7")
SLATE = colors.HexColor("#334155")
MUTED = colors.HexColor("#64748B")
LINE = colors.HexColor("#CBD5E1")
PAPER = colors.HexColor("#F8FAFC")


def register_fonts():
    pdfmetrics.registerFont(TTFont("NotoKR", str(FONT_PATH)))
    pdfmetrics.registerFont(TTFont("NotoKR-Bold", str(FONT_PATH)))


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleKR", parent=base["Title"], fontName="NotoKR-Bold", fontSize=28,
            leading=37, textColor=NAVY, alignment=TA_LEFT, spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleKR", parent=base["Normal"], fontName="NotoKR", fontSize=12,
            leading=19, textColor=SLATE, spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "H1KR", parent=base["Heading1"], fontName="NotoKR-Bold", fontSize=18,
            leading=25, textColor=NAVY, spaceBefore=8, spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2KR", parent=base["Heading2"], fontName="NotoKR-Bold", fontSize=13,
            leading=19, textColor=BLUE, spaceBefore=8, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "BodyKR", parent=base["BodyText"], fontName="NotoKR", fontSize=9.5,
            leading=15.5, textColor=SLATE, spaceAfter=6, wordWrap="CJK",
        ),
        "small": ParagraphStyle(
            "SmallKR", parent=base["BodyText"], fontName="NotoKR", fontSize=8.2,
            leading=12.5, textColor=MUTED, spaceAfter=4, wordWrap="CJK",
        ),
        "bullet": ParagraphStyle(
            "BulletKR", parent=base["BodyText"], fontName="NotoKR", fontSize=9.3,
            leading=15, leftIndent=12, firstLineIndent=-8, bulletIndent=0,
            textColor=SLATE, spaceAfter=4, wordWrap="CJK",
        ),
        "question": ParagraphStyle(
            "QuestionKR", parent=base["BodyText"], fontName="NotoKR-Bold", fontSize=10,
            leading=15.5, textColor=NAVY, spaceAfter=0, wordWrap="CJK",
        ),
        "answer": ParagraphStyle(
            "AnswerKR", parent=base["BodyText"], fontName="NotoKR", fontSize=9.2,
            leading=15, textColor=SLATE, spaceAfter=0, wordWrap="CJK",
        ),
        "code": ParagraphStyle(
            "Code", parent=base["Code"], fontName="NotoKR", fontSize=7.5,
            leading=10.5, textColor=colors.HexColor("#E2E8F0"), leftIndent=8,
            rightIndent=8, spaceBefore=5, spaceAfter=7,
        ),
        "cover_tag": ParagraphStyle(
            "CoverTag", parent=base["Normal"], fontName="NotoKR-Bold", fontSize=10,
            leading=14, textColor=BLUE, alignment=TA_LEFT,
        ),
        "center": ParagraphStyle(
            "CenterKR", parent=base["Normal"], fontName="NotoKR", fontSize=9,
            leading=14, textColor=SLATE, alignment=TA_CENTER,
        ),
        "table_header": ParagraphStyle(
            "TableHeaderKR", parent=base["Normal"], fontName="NotoKR-Bold", fontSize=8.5,
            leading=12, textColor=colors.white, alignment=TA_LEFT, wordWrap="CJK",
        ),
    }


def paragraph(text, style):
    return Paragraph(escape(text).replace("\n", "<br/>"), style)


def bullet(text, styles):
    return Paragraph("• " + escape(text), styles["bullet"])


def code_block(text, styles):
    block = XPreformatted(escape(text), styles["code"])
    table = Table([[block]], colWidths=[166 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#1E293B")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def qa(number, question, answer, styles):
    label = Paragraph(f"Q{number}", ParagraphStyle(
        f"QLabel{number}", parent=styles["small"], fontName="NotoKR-Bold",
        fontSize=8, textColor=BLUE, spaceAfter=2,
    ))
    content = [label, paragraph(question, styles["question"]), Spacer(1, 4), paragraph(answer, styles["answer"])]
    box = Table([[content]], colWidths=[164 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PAPER),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([box, Spacer(1, 7)])


def callout(title, text, styles, fill=SKY, stroke=BLUE):
    content = [paragraph(title, styles["question"]), Spacer(1, 3), paragraph(text, styles["body"])]
    box = Table([[content]], colWidths=[164 * mm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("BOX", (0, 0), (-1, -1), 0.7, stroke),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return box


def data_table(headers, rows, widths, styles):
    data = [[paragraph(cell, styles["table_header"]) for cell in headers]]
    data.extend([[paragraph(cell, styles["small"]) for cell in row] for row in rows])
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


class Diagram(Flowable):
    def __init__(self, height, drawer):
        super().__init__()
        self.width = 166 * mm
        self.height = height
        self.drawer = drawer

    def draw(self):
        self.drawer(self.canv, self.width, self.height)


def rounded_box(canvas, x, y, width, height, label, fill, stroke=LINE, font_size=8.5):
    canvas.setFillColor(fill)
    canvas.setStrokeColor(stroke)
    canvas.roundRect(x, y, width, height, 6, fill=1, stroke=1)
    canvas.setFillColor(NAVY)
    canvas.setFont("NotoKR-Bold", font_size)
    canvas.drawCentredString(x + width / 2, y + height / 2 - font_size / 3, label)


def arrow(canvas, x1, y1, x2, y2, color=BLUE):
    canvas.setStrokeColor(color)
    canvas.setFillColor(color)
    canvas.setLineWidth(1.2)
    canvas.line(x1, y1, x2, y2)
    angle = 4
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 > x1 else -1
        canvas.line(x2, y2, x2 - direction * angle, y2 + angle / 2)
        canvas.line(x2, y2, x2 - direction * angle, y2 - angle / 2)
    else:
        direction = 1 if y2 > y1 else -1
        canvas.line(x2, y2, x2 + angle / 2, y2 - direction * angle)
        canvas.line(x2, y2, x2 - angle / 2, y2 - direction * angle)


def draw_architecture(canvas, width, height):
    canvas.setFillColor(PAPER)
    canvas.roundRect(0, 0, width, height, 10, fill=1, stroke=0)
    command_x = width / 2 - 50
    rounded_box(canvas, 10, height - 42, 78, 28, "CLI 입력", SKY)
    rounded_box(canvas, command_x, height - 42, 100, 28, "MiniRedis 명령", colors.white, BLUE)
    arrow(canvas, 88, height - 28, command_x, height - 28)
    labels = [
        (8, 15, 84, 34, "data 해시맵", SKY),
        (100, 15, 84, 34, "LRU 연결 리스트", MINT),
        (192, 15, 84, 34, "lru_nodes 해시맵", MINT),
        (284, 15, 84, 34, "TTL 최소 힙", AMBER),
        (376, 15, 84, 34, "expirations 맵", AMBER),
    ]
    for x, y, w, h, label, fill in labels:
        rounded_box(canvas, x, y, w, h, label, fill, font_size=6.8)
        arrow(canvas, width / 2, height - 43, x + w / 2, y + h)


def draw_hash_chain(canvas, width, height):
    canvas.setFillColor(PAPER)
    canvas.roundRect(0, 0, width, height, 10, fill=1, stroke=0)
    canvas.setFont("NotoKR-Bold", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(10, height - 16, "해시 인덱스가 같으면 한 버킷의 연결 리스트에 이어 붙인다")
    y_values = [height - 42, height - 73, height - 104]
    for index, y in enumerate(y_values):
        rounded_box(canvas, 18, y, 42, 22, f"버킷 {index}", colors.white, BLUE, 7.5)
    rounded_box(canvas, 96, y_values[0], 94, 22, '("user:1", "A")', SKY, font_size=7)
    arrow(canvas, 60, y_values[0] + 11, 96, y_values[0] + 11)
    rounded_box(canvas, 96, y_values[1], 94, 22, '("user:2", "B")', SKY, font_size=7)
    rounded_box(canvas, 229, y_values[1], 94, 22, '("name", "Kim")', SKY, font_size=7)
    arrow(canvas, 60, y_values[1] + 11, 96, y_values[1] + 11)
    arrow(canvas, 190, y_values[1] + 11, 229, y_values[1] + 11)
    canvas.setFont("NotoKR", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(335, y_values[1] + 7, "충돌: 실제 키를 비교해 찾음")
    canvas.drawString(96, 10, "로드 팩터 > 0.75  →  버킷 2배  →  모든 키 재해시")


def draw_lru(canvas, width, height):
    canvas.setFillColor(PAPER)
    canvas.roundRect(0, 0, width, height, 10, fill=1, stroke=0)
    canvas.setFont("NotoKR-Bold", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(10, height - 16, "LRU: 최근 사용은 앞(head), 가장 오래된 사용은 뒤(tail)")
    labels = [("user:3", MINT), ("user:1", MINT), ("user:2", AMBER)]
    x = 72
    for index, (label, fill) in enumerate(labels):
        rounded_box(canvas, x, 35, 92, 30, label, fill, font_size=8)
        if index < len(labels) - 1:
            arrow(canvas, x + 92, 52, x + 122, 52, GREEN)
            arrow(canvas, x + 122, 44, x + 92, 44, GREEN)
        x += 122
    canvas.setFont("NotoKR-Bold", 7.5)
    canvas.setFillColor(GREEN)
    canvas.drawString(72, 22, "head / MRU")
    canvas.setFillColor(ORANGE)
    canvas.drawRightString(408, 22, "tail / eviction 대상")
    canvas.setFont("NotoKR", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(72, 8, "lru_nodes 해시맵이 key → 위 노드를 바로 연결하므로 이동도 평균 O(1)")


def draw_heap(canvas, width, height):
    canvas.setFillColor(PAPER)
    canvas.roundRect(0, 0, width, height, 10, fill=1, stroke=0)
    canvas.setFont("NotoKR-Bold", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(10, height - 16, "TTL 최소 힙: 가장 이른 expire_at이 루트에 온다")
    nodes = [
        (width / 2 - 42, height - 48, "12:01 / A"),
        (width / 2 - 132, height - 87, "12:03 / B"),
        (width / 2 + 48, height - 87, "12:05 / C"),
    ]
    arrow(canvas, width / 2, height - 48, width / 2 - 90, height - 63, CYAN)
    arrow(canvas, width / 2, height - 48, width / 2 + 90, height - 63, CYAN)
    for x, y, label in nodes:
        rounded_box(canvas, x, y, 84, 24, label, AMBER, ORANGE, 7.5)
    canvas.setFont("NotoKR", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(10, 8, "최신 expirations 값과 다르면 오래된 힙 항목으로 보고 무시한다 (lazy deletion)")


def draw_flow(canvas, width, height):
    canvas.setFillColor(PAPER)
    canvas.roundRect(0, 0, width, height, 10, fill=1, stroke=0)
    canvas.setFont("NotoKR-Bold", 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(10, height - 16, "SET과 GET의 필수 처리 순서")
    set_labels = ["만료 정리", "크기 계산", "저장+TTL 제거", "LRU 앞으로", "초과 시 tail 제거"]
    get_labels = ["TTL 확인", "만료면 삭제", "값 조회", "성공 시 LRU 앞으로", "값 반환"]
    for row, labels in enumerate((set_labels, get_labels)):
        y = height - 53 - row * 50
        canvas.setFont("NotoKR-Bold", 8)
        canvas.setFillColor(BLUE if row == 0 else GREEN)
        canvas.drawString(10, y + 8, "SET" if row == 0 else "GET")
        x = 38
        for index, label in enumerate(labels):
            rounded_box(canvas, x, y, 77, 25, label, SKY if row == 0 else MINT, font_size=6.3)
            if index < len(labels) - 1:
                arrow(canvas, x + 77, y + 12.5, x + 86, y + 12.5, BLUE if row == 0 else GREEN)
            x += 86


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.4)
    canvas.line(22 * mm, 14 * mm, 188 * mm, 14 * mm)
    canvas.setFont("NotoKR", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(22 * mm, 9 * mm, "B5-2 Mini Redis 개념서")
    canvas.drawRightString(188 * mm, 9 * mm, str(doc.page))
    canvas.restoreState()


def build_legacy():
    register_fonts()
    styles = make_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=22 * mm, leftMargin=22 * mm,
        topMargin=20 * mm, bottomMargin=19 * mm, title="B5-2 Mini Redis 개념서",
        author="B5-2",
    )
    story = []

    story.extend([
        Spacer(1, 22 * mm),
        paragraph("B5-2 · DATA STRUCTURES", styles["cover_tag"]),
        Spacer(1, 6 * mm),
        paragraph("Mini Redis 개념서", styles["title"]),
        paragraph("해시맵 · 이중 연결 리스트 · 최소 힙으로 이해하는 LRU와 TTL", styles["subtitle"]),
        Spacer(1, 12 * mm),
        Diagram(36 * mm, draw_architecture),
        Spacer(1, 12 * mm),
        Table([
            [paragraph("학습 목표", styles["question"]), paragraph("코드를 읽고 평가 문항 17개에 자신의 말로 답하기", styles["body"])],
            [paragraph("구현 범위", styles["question"]), paragraph("필수 명령 10개 + CLI, 보너스 과제 제외", styles["body"])],
            [paragraph("읽는 순서", styles["question"]), paragraph("전체 그림 → 자료구조 → 명령 흐름 → 평가 Q&A", styles["body"])],
        ], colWidths=[32 * mm, 134 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), SKY),
            ("GRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])),
        Spacer(1, 15 * mm),
        paragraph("기준 문서: 미션 - AI 도구 학습.pdf / B5-2_평가.pdf", styles["small"]),
        paragraph("Python 3.8+ · CLI only · dict/set/collections 미사용", styles["small"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("1. 전체 구조와 핵심 용어", styles["h1"]),
        paragraph("Mini Redis는 키로 값을 찾는 작은 메모리 저장소다. 빠른 조회, 사용 순서, 만료 순서는 서로 다른 문제이므로 자료구조도 역할을 나눠 가진다.", styles["body"]),
        Diagram(31 * mm, draw_architecture),
        Spacer(1, 5),
    ])
    concept_rows = [
        ["구조", "쉬운 비유", "이 코드의 역할", "복잡도"],
        ["해시맵", "이름으로 사물함 번호 찾기", "키→값·노드·만료 시각 조회", "평균 O(1)"],
        ["이중 연결 리스트", "앞뒤 사람을 모두 아는 줄", "최근 사용 순서와 tail 제거", "O(1)"],
        ["최소 힙", "가장 이른 알람이 맨 위", "가장 빠른 만료 찾기", "peek O(1)"],
        ["LRU", "오래 안 쓴 것부터 버리기", "메모리 제한 초과 시 eviction", "평균 O(1)/키"],
    ]
    table_data = [[paragraph(cell, styles["small"] if r else styles["table_header"]) for cell in row] for r, row in enumerate(concept_rows)]
    concept_table = Table(table_data, colWidths=[30 * mm, 47 * mm, 61 * mm, 28 * mm], repeatRows=1)
    concept_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([
        concept_table,
        Spacer(1, 6),
        paragraph("O(1)은 데이터가 늘어도 한 번의 작업량이 거의 일정하다는 뜻이다. 해시맵은 평균 O(1)이며, 연결 리스트는 대상 노드를 이미 알고 있을 때 O(1)이다. 힙 삽입·삭제는 O(log n)이다.", styles["body"]),
        paragraph("구현 파일", styles["h2"]),
        bullet("doubly_linked_list.py: Node와 6개 필수 리스트 메서드", styles),
        bullet("hash_map.py: 직접 만든 해시, 체이닝, 로드 팩터 기반 resize", styles),
        bullet("min_heap.py: push/pop/peek/size와 두 heapify", styles),
        bullet("mini_redis.py: 명령, 메모리, LRU, TTL을 결합", styles),
        PageBreak(),
    ])

    story.extend([
        paragraph("2. 자료구조를 코드로 이해하기", styles["h1"]),
        paragraph("2.1 이중 연결 리스트", styles["h2"]),
        paragraph("Node는 prev, next, data를 가진다. 리스트는 head와 tail도 기억한다. 삭제할 노드의 양옆 링크만 바꾸므로 전체를 순회하지 않는다.", styles["body"]),
        code_block("def remove_node(self, node):\n    if node.prev is None:\n        self.head = node.next\n    else:\n        node.prev.next = node.next\n\n    if node.next is None:\n        self.tail = node.prev\n    else:\n        node.next.prev = node.prev", styles),
        paragraph("중요: 노드를 찾는 작업까지 리스트로 하면 O(n)이다. LRU에서는 lru_nodes 해시맵이 키로 노드를 바로 알려준다.", styles["body"]),
        paragraph("2.2 체이닝 해시맵", styles["h2"]),
        paragraph("해시는 문자열 키를 숫자 인덱스로 바꾸는 규칙이다. 이 구현은 UTF-8 바이트를 차례로 섞고 버킷 수로 나눈 나머지를 사용한다.", styles["body"]),
        code_block("value = 0\nfor byte in key.encode(\"utf-8\"):\n    value = (value * 31 + byte) & 0xFFFFFFFF\nreturn value % self.capacity", styles),
        Diagram(40 * mm, draw_hash_chain),
        Spacer(1, 4),
        paragraph("충돌은 서로 다른 키가 같은 인덱스를 얻는 현상이다. 버킷마다 이중 연결 리스트를 두고 실제 키가 같은지 비교한다. count / capacity가 0.75를 넘으면 버킷을 2배로 만들고 모든 키를 다시 해시한다.", styles["body"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("3. LRU와 TTL", styles["h1"]),
        paragraph("3.1 해시맵 + 이중 연결 리스트로 만드는 LRU", styles["h2"]),
        Diagram(34 * mm, draw_lru),
        Spacer(1, 4),
        paragraph("해시맵은 키의 노드를 평균 O(1)에 찾고, 연결 리스트는 그 노드를 O(1)에 앞으로 옮긴다. 둘 중 하나만 있으면 순서 또는 빠른 노드 조회를 잃는다.", styles["body"]),
        code_block("def _touch(self, key):\n    node = self.lru_nodes.get(key)\n    if node is None:\n        node = self.lru.insert_front(key)\n        self.lru_nodes.put(key, node)\n    else:\n        self.lru.move_to_front(node)", styles),
        paragraph("3.2 최소 힙으로 관리하는 TTL", styles["h2"]),
        Diagram(36 * mm, draw_heap),
        Spacer(1, 4),
        paragraph("TTL(Time To Live)은 키가 살아 있을 남은 시간이다. 최소 힙의 루트에는 가장 작은 expire_at이 온다. EXPIRE를 다시 설정해 생긴 과거 힙 항목은 expirations 해시맵의 최신 값과 비교해 무시한다. 이것이 lazy deletion(지연 삭제)이다.", styles["body"]),
        paragraph("DEL과 만료 삭제는 공통 _delete_key를 호출한다. 데이터, used_memory, LRU 노드, 최신 TTL을 한 번에 정리해 구조 사이의 불일치를 막는다.", styles["body"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("4. 명령 전체 흐름", styles["h1"]),
        Diagram(42 * mm, draw_flow),
        paragraph("4.1 SET과 eviction", styles["h2"]),
        bullet("만료된 키를 먼저 정리하고 새 키+값의 UTF-8 바이트 크기를 계산한다.", styles),
        bullet("한 항목만으로 maxmemory를 넘으면 저장하지 않고 OOM을 반환한다.", styles),
        bullet("덮어쓰기면 이전 크기를 빼고 새 크기를 더하며, 기존 TTL은 지운다.", styles),
        bullet("SET한 키를 LRU 앞으로 옮기고, 제한을 넘는 동안 tail부터 제거한다.", styles),
        code_block("while self.maxmemory > 0 and self.used_memory > self.maxmemory:\n    oldest_key = self.lru.tail.data\n    self._delete_key(oldest_key)\n    self.evicted_keys += 1", styles),
        paragraph("4.2 GET", styles["h2"]),
        code_block("if self._delete_if_expired(key) or not self.data.contains(key):\n    return \"(nil)\"\nvalue = self.data.get(key)\nself._touch(key)\nreturn self._quote(value)", styles),
        paragraph("만료 또는 없음이면 즉시 끝나므로 LRU가 갱신되지 않는다. 값 반환에 성공한 경우에만 _touch가 실행된다.", styles["body"]),
        paragraph("4.3 메모리 공식", styles["h2"]),
        paragraph("used_memory = Σ(len(utf8(key)) + len(utf8(value))). 노드·포인터·버킷 오버헤드는 과제 공식에 따라 제외한다. maxmemory가 0이면 무제한이다.", styles["body"]),
        PageBreak(),
    ])

    result_rows = [
        ["상황", "출력"],
        ["SET 성공", "OK"],
        ["GET 없음 또는 만료", "(nil)"],
        ["DEL / EXISTS / EXPIRE", "(integer) 1 또는 (integer) 0"],
        ["TTL: 키 없음 / 만료 없음 / 만료 있음", "-2 / -1 / 남은 초"],
        ["한 항목이 maxmemory보다 큼", "OOM, 저장하지 않음"],
        ["잘못된 명령 / 인자 / 정수", "(error) ..."],
    ]
    rt = Table([[paragraph(c, styles["small"] if r else styles["table_header"]) for c in row] for r, row in enumerate(result_rows)], colWidths=[88 * mm, 78 * mm], repeatRows=1)
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([
        paragraph("5. 출력 규칙과 평가 Q&A", styles["h1"]),
        rt,
        Spacer(1, 8),
        paragraph("질문 문구는 B5-2_평가.pdf 항목 1-4를 그대로 옮겼다. 항목 5는 보너스 문제이므로 지시대로 제외했다.", styles["small"]),
        paragraph("항목 1 · 기능 동작", styles["h2"]),
        qa(1, "String 타입 기본 동작: SET, GET, DEL, EXISTS, DBSIZE, KEYS 명령어가 모두 정상 동작하는가?", "네. MiniRedis가 여섯 메서드를 제공하고 execute가 명령 이름과 인자 수를 검사해 연결한다. SET/GET은 LRU도 갱신하고, DBSIZE/KEYS는 먼저 만료 키를 정리한다.", styles),
        qa(2, "LRU 자동 제거: maxmemory 설정 후 제한 초과 시 가장 오래된 키가 자동 제거되는가?", "네. 최근 사용 키는 리스트의 head, 가장 오래된 키는 tail에 있다. SET 뒤 제한을 넘으면 tail부터 _delete_key로 지우며 제한 이하가 될 때까지 반복한다.", styles),
        qa(3, "메모리 정보 확인: INFO memory에서 used_memory/maxmemory/evicted_keys가 규칙에 맞게 출력되는가?", "네. used_memory는 모든 키와 값의 UTF-8 바이트 길이 합이고 구조 오버헤드는 제외한다. maxmemory는 설정값, evicted_keys는 LRU로 제거한 누적 개수다.", styles),
        PageBreak(),
    ])

    story.extend([
        paragraph("항목 1 · 기능 동작 (계속)", styles["h1"]),
        qa(4, "TTL 관리: EXPIRE/TTL 규칙이 동작하며 만료된 키가 적절히 제거되는가?", "네. EXPIRE는 최신 만료 시각을 해시맵과 최소 힙에 저장한다. TTL은 없음 -2, 만료 설정 없음 -1, 설정 있음 남은 초를 반환한다. 접근하거나 전체 정리를 할 때 지난 키를 삭제한다.", styles),
        qa(5, "에러 처리: 잘못된 명령/인자/정수 오류/OOM이 표준 형식으로 출력되는가?", "네. execute가 알 수 없는 명령과 인자 수 오류를 구분한다. 정수 변환 실패·음수 maxmemory는 정수 오류를, 한 항목이 제한보다 크면 OOM을 반환한다.", styles),
        paragraph("항목 2 · 기본 자료구조", styles["h2"]),
        qa(6, "이중 연결 리스트의 노드 구조(prev, next, data)와 핵심 메서드들이 O(1)로 동작하도록 어떻게 구성했는지 설명할 수 있는가?", "Node가 앞·뒤 노드와 데이터를 기억하고 리스트가 head, tail을 기억한다. 삽입·삭제·이동은 대상 노드와 이웃의 링크 몇 개만 바꾼다. 대상 노드를 이미 아는 조건에서 O(1)이다.", styles),
        qa(7, "해시맵에서 직접 설계한 해시 함수가 어떤 입력을 받아 어떤 과정을 거쳐 인덱스를 만드는지 설명할 수 있는가?", "문자열 키를 UTF-8 바이트열로 바꾼다. 각 바이트마다 value = value * 31 + byte를 계산하고 32비트로 제한한다. 마지막 값을 버킷 수로 나눈 나머지가 인덱스다.", styles),
        qa(8, "충돌 해결을 체이닝 방식으로 어떻게 구현했는지(버킷 내부 구조 선택 포함) 설명할 수 있는가?", "버킷 배열의 각 칸에 DoublyLinkedList를 둔다. 같은 인덱스를 받은 (key, value)들을 그 리스트에 연결한다. 조회는 해당 버킷만 순회하며 실제 키가 같은 노드를 찾는다.", styles),
        qa(9, "로드 팩터 0.75 초과 시 “버킷 2배 확장”을 어떤 절차로 수행하는지 설명할 수 있는가?", "새 키를 넣은 뒤 count / capacity가 0.75보다 큰지 본다. 크면 capacity를 2배로 만들고 빈 버킷 배열을 만든다. 기존 모든 노드를 돌며 새 capacity로 인덱스를 다시 계산해 삽입한다.", styles),
        PageBreak(),
    ])

    story.extend([
        paragraph("항목 3 · LRU, TTL, 명령 흐름", styles["h1"]),
        qa(10, "LRU 구현에서 “해시맵 + 이중 연결 리스트”가 각각 어떤 역할을 하고, 왜 둘 다 필요한지 설명할 수 있는가?", "해시맵 lru_nodes는 키로 리스트 노드를 평균 O(1)에 찾는다. 리스트는 최근 사용 순서를 유지하며 앞 이동과 뒤 제거를 O(1)에 한다. 해시맵만으로는 순서를 모르고, 리스트만으로는 노드를 찾는 데 O(n)이 걸리므로 둘 다 필요하다.", styles),
        qa(11, "O(1) LRU 달성 원리를 “조회(해시) + 갱신(리스트 이동)” 관점에서 설명할 수 있는가?", "_touch가 해시맵에서 키의 노드를 평균 O(1)에 조회하고 move_to_front가 링크만 바꿔 O(1)에 앞으로 옮긴다. 가장 오래된 키도 tail로 즉시 찾는다.", styles),
        qa(12, "TTL 관리에 힙을 사용한 이유(가장 빠른 만료를 빠르게 찾는 성질)를 설명할 수 있는가?", "최소 힙 루트에는 가장 작은 expire_at, 즉 가장 먼저 만료될 항목이 있다. 다음 만료 확인은 O(1), 새 만료 추가와 루트 제거는 O(log n)이므로 모든 키를 매번 O(n)으로 훑지 않아도 된다.", styles),
        qa(13, "메모리 초과 시 eviction 흐름을 단계별로 설명할 수 있는가? (used_memory 산정/갱신, LRU 제거, evicted_keys 증가 포함)", "새 키+값의 UTF-8 바이트 크기를 계산한다. 기존 키면 이전 크기를 빼고 새 크기를 더한다. SET한 키를 LRU 앞에 둔 뒤 초과하면 tail 키를 모든 구조에서 지우고 그 크기를 used_memory에서 빼며 evicted_keys를 증가시킨다. 제한 이하가 될 때까지 반복한다.", styles),
        qa(14, "GET 명령어 전체 흐름을 순서대로 설명할 수 있는가? (TTL 확인→삭제 여부→값 반환→LRU 갱신 조건)", "키의 만료 시각을 먼저 확인한다. 지났다면 모든 관련 구조에서 삭제하고 (nil)을 반환한다. 만료되지 않았지만 키가 없어도 (nil)이다. 존재할 때만 값을 읽고 LRU 맨 앞으로 옮긴 다음 따옴표로 감싼 값을 반환한다.", styles),
        PageBreak(),
    ])

    story.extend([
        paragraph("항목 4 · 확장 사고", styles["h1"]),
        qa(15, "“만약 LRU 대신 LFU정책을 구현한다면 자료구조를 어떻게 변경해야 하는가?”에 합리적으로 답변할 수 있는가?", "LFU는 가장 오래 안 쓴 키가 아니라 사용 횟수가 가장 적은 키를 지운다. 각 키의 빈도를 GET/SET 때 증가시켜야 한다. 효율적으로는 키→(값, 빈도, 노드) 해시맵, 빈도→같은 빈도의 키 목록 해시맵, 현재 최소 빈도 값이 필요하다. 같은 빈도끼리는 연결 리스트로 최근 사용 순서를 정한다.", styles),
        qa(16, "“데이터가 10만 건으로 늘어나면 현재 구조에서 병목이 될 수 있는 부분은 어디이며, 어떻게 개선할 수 있는가?”에 답변할 수 있는가?", "해시 분산이 나쁘면 한 버킷 리스트가 길어져 조회가 O(n)에 가까워질 수 있다. 더 좋은 해시와 적절한 초기 capacity가 필요하다. resize의 전체 재해시 비용은 점진적 rehash로 나눌 수 있다. EXPIRE를 반복하면 lazy deletion 항목이 힙에 쌓이므로 필요할 때 힙을 재구성할 수 있다. KEYS는 모든 키를 출력하므로 본질적으로 O(n)이다.", styles),
        qa(17, "“used_memory에 자료구조 오버헤드까지 포함하는 모델로 바꾸면 무엇이 달라지고, 공정한 비교/채점을 위해 어떤 보정이 필요할지” 설명할 수 있는가?", "노드 객체, 포인터, 버킷 배열, 힙 항목까지 세면 같은 키·값이어도 구현과 Python 버전에 따라 값이 달라지고 더 빨리 eviction된다. 공정한 채점을 위해 실행 환경과 측정법, 포함 항목, 중복 참조 처리 규칙을 고정해야 한다. 또는 언어별 고정 오버헤드 상수와 허용 오차를 정할 수 있다.", styles),
        Spacer(1, 8),
        paragraph("답변 공식", styles["h2"]),
        paragraph("어떤 구조인가 → 왜 필요한가 → 어느 코드가 담당하는가 → 시간 복잡도는 무엇인가 순서로 설명한다. GET과 SET을 손으로 따라가며 used_memory, LRU의 head/tail, TTL 값이 어떻게 바뀌는지 확인하면 전체 문항이 연결된다.", styles["body"]),
        Spacer(1, 10),
        Table([[paragraph("완료 체크", styles["question"]), paragraph("필수 요구사항만 구현 · 보너스 제외 · 평가 질문 17개 답변 · 자동 테스트 9개 통과", styles["body"])]], colWidths=[32 * mm, 134 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), MINT),
            ("BOX", (0, 0), (-1, -1), 0.7, GREEN),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ])),
    ])

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    from build_beginner_concept_pdf import build

    build()
