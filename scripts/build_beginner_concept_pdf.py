"""Build the beginner-first Mini Redis concept guide PDF."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle

from build_concept_pdf import (
    AMBER,
    BLUE,
    GREEN,
    LINE,
    MINT,
    OUTPUT,
    PAPER,
    SKY,
    Diagram,
    bullet,
    callout,
    code_block,
    data_table,
    draw_architecture,
    draw_flow,
    draw_hash_chain,
    draw_heap,
    draw_lru,
    footer,
    make_styles,
    paragraph,
    qa,
    register_fonts,
)


def add_qa_section(story, title, entries, styles):
    story.append(paragraph(title, styles["h1"]))
    for number, question, answer in entries:
        story.append(qa(number, question, answer, styles))


def build():
    register_fonts()
    styles = make_styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=22 * mm, leftMargin=22 * mm,
        topMargin=20 * mm, bottomMargin=19 * mm,
        title="B5-2 Mini Redis 개념서 - 초보자판", author="B5-2",
    )
    story = []

    story.extend([
        Spacer(1, 20 * mm),
        paragraph("B5-2 · BEGINNER FIRST", styles["cover_tag"]),
        Spacer(1, 6 * mm),
        paragraph("Mini Redis 개념서", styles["title"]),
        paragraph("용어의 뜻보다 먼저, 왜 필요한지부터 이해하기", styles["subtitle"]),
        Spacer(1, 10 * mm),
        callout(
            "이 문서가 답하는 질문",
            "LRU는 무엇이고 왜 쓰는가? TTL과는 무엇이 다른가? 왜 해시맵과 이중 연결 리스트를 같이 쓰는가? 왜 만료 시간에는 최소 힙이 필요한가?",
            styles, SKY, BLUE,
        ),
        Spacer(1, 9 * mm),
        Diagram(36 * mm, draw_architecture),
        Spacer(1, 10 * mm),
        Table([
            [paragraph("읽는 순서", styles["question"]), paragraph("문제 → 용어 → 왜 사용 → 코드 → 실행 예시 → 평가 Q&A", styles["body"])],
            [paragraph("대상", styles["question"]), paragraph("LRU, TTL, 힙이 처음인 코딩 입문자", styles["body"])],
            [paragraph("범위", styles["question"]), paragraph("필수 요구사항만 설명, 보너스 과제 제외", styles["body"])],
        ], colWidths=[32 * mm, 134 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), MINT),
            ("GRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])),
        Spacer(1, 14 * mm),
        paragraph("기준 문서: 미션 - AI 도구 학습.pdf / B5-2_평가.pdf", styles["small"]),
        paragraph("Python 3.8+ · CLI only · dict/set/collections 미사용", styles["small"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("0. Mini Redis가 무엇인가?", styles["h1"]),
        paragraph("Redis는 데이터를 메모리(RAM)에 저장해 빠르게 읽고 쓰는 프로그램이다. Mini Redis는 실제 Redis 전체가 아니라 키로 값을 저장하고 찾는 핵심 원리를 작게 구현한다.", styles["body"]),
        callout("가장 단순한 사용", "SET name Alice는 name이라는 키로 Alice라는 값을 저장한다. GET name은 name을 이용해 Alice를 찾는다.", styles, SKY, BLUE),
        Spacer(1, 7),
        data_table(
            ["용어", "쉬운 뜻", "이 과제의 예"],
            [
                ["데이터", "프로그램이 보관하는 정보", "Alice"],
                ["키(key)", "값을 찾기 위한 고유한 이름", "name"],
                ["값(value)", "키에 연결한 실제 내용", "Alice"],
                ["Key-Value", "키로 값을 저장하고 찾는 방식", "name → Alice"],
                ["메모리(RAM)", "실행 중 빠르게 쓰는 임시 공간", "Mini Redis 저장 공간"],
                ["In-Memory", "파일 대신 메모리에 보관", "빠르지만 종료하면 사라짐"],
                ["자료구조", "데이터를 놓고 관리하는 모양", "해시맵·연결 리스트·힙"],
                ["알고리즘", "문제를 해결하는 처리 순서", "만료 확인 후 GET"],
            ],
            [30 * mm, 66 * mm, 70 * mm], styles,
        ),
        Spacer(1, 8),
        paragraph("Mini Redis가 해결해야 할 추가 문제", styles["h2"]),
        bullet("메모리는 한정되어 있다. 꽉 차면 어떤 키를 버릴지 결정해야 한다.", styles),
        bullet("오래된 데이터는 계속 남으면 안 된다. 언제 만료할지 관리해야 한다.", styles),
        paragraph("첫 번째 문제의 답이 LRU, 두 번째 문제의 답이 TTL이다.", styles["body"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("1. LRU와 TTL은 왜 필요한가?", styles["h1"]),
        callout(
            "문제 A · 메모리는 무한하지 않다",
            "아무 키나 지우면 방금 사용한 중요한 값이 사라질 수 있다. 그래서 무엇을 버릴지 정하는 규칙이 필요하다.",
            styles, SKY, BLUE,
        ),
        Spacer(1, 7),
        paragraph("LRU = Least Recently Used", styles["h2"]),
        paragraph("LRU는 메모리가 부족할 때 가장 오래 사용하지 않은 키부터 버리는 정책이다. 책상에 책을 세 권만 둘 수 있다면, 가장 오래 펼치지 않은 책을 치우는 것과 같다. 최근에 본 책은 다시 볼 가능성이 높다는 가정을 이용한다.", styles["body"]),
        callout(
            "중요",
            "LRU는 자료구조 이름이 아니라 삭제 대상을 고르는 정책이다. 이 정책을 빠르게 실행하기 위해 해시맵과 이중 연결 리스트를 함께 쓴다.",
            styles, MINT, GREEN,
        ),
        Spacer(1, 9),
        callout(
            "문제 B · 오래된 데이터가 계속 남는다",
            "로그인 인증번호나 캐시 가격처럼 시간이 지나면 틀리거나 위험해지는 데이터는 정해진 시각에 무효가 되어야 한다.",
            styles, AMBER,
        ),
        Spacer(1, 7),
        paragraph("TTL = Time To Live", styles["h2"]),
        paragraph("TTL은 키가 앞으로 살아 있을 남은 시간이다. EXPIRE code 180은 code 키를 180초 동안만 유효하게 만든다. expire_at은 그 남은 시간을 실제 만료 시각으로 바꾼 값이다.", styles["body"]),
        data_table(
            ["구분", "LRU eviction", "TTL expiration"],
            [
                ["삭제 이유", "메모리 공간 부족", "유효 시간 종료"],
                ["삭제 대상", "가장 오래 사용하지 않은 키", "만료 시각이 지난 키"],
                ["관련 명령", "CONFIG SET maxmemory, SET", "EXPIRE, TTL"],
                ["필요 구조", "해시맵 + 이중 연결 리스트", "해시맵 + 최소 힙"],
            ],
            [30 * mm, 68 * mm, 68 * mm], styles,
        ),
        paragraph("한 문장으로: LRU는 자리가 없어서 버리고, TTL은 시간이 끝나서 만료한다.", styles["body"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("2. 빠르다는 말을 이해하는 O 표기법", styles["h1"]),
        paragraph("n은 저장된 데이터 개수다. O 표기법은 데이터가 많아질 때 작업량이 얼마나 늘어나는지 보여 준다.", styles["body"]),
        data_table(
            ["표기", "뜻", "데이터가 10만 개면", "이 과제의 예"],
            [
                ["O(1)", "개수와 거의 무관하게 일정", "거의 같은 단계", "해시 조회, 알려진 노드 삭제"],
                ["O(log n)", "개수가 크게 늘어도 조금 증가", "비교적 빠름", "힙 push/pop"],
                ["O(n)", "개수만큼 확인", "최악에 10만 번", "KEYS, 긴 리스트 순회"],
            ],
            [25 * mm, 50 * mm, 42 * mm, 49 * mm], styles,
        ),
        Spacer(1, 7),
        callout("오해하지 않기", "O(1)은 정확히 한 줄만 실행한다는 뜻이 아니다. 데이터가 많아져도 작업량이 크게 늘지 않는다는 뜻이다.", styles, PAPER, BLUE),
        paragraph("각 문제에 맞는 구조", styles["h2"]),
        data_table(
            ["필요한 일", "그냥 구현하면", "선택한 구조", "이유"],
            [
                ["키로 값 찾기", "전체 순회 O(n)", "해시맵", "평균 O(1) 조회"],
                ["최근 사용 순서 변경", "배열 이동 O(n)", "이중 연결 리스트", "알려진 노드 이동 O(1)"],
                ["다음 만료 찾기", "전체 만료 검사 O(n)", "최소 힙", "최솟값 peek O(1)"],
            ],
            [42 * mm, 42 * mm, 38 * mm, 44 * mm], styles,
        ),
        Spacer(1, 8),
        Diagram(32 * mm, draw_architecture),
        paragraph("한 구조가 모든 문제를 잘 풀지는 못한다. 빠른 조회, 사용 순서, 만료 순서는 성격이 달라 역할을 나눈다.", styles["body"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("3. 해시맵 · 키로 값을 빨리 찾기", styles["h1"]),
        callout("해시맵이 없으면", "user:99999를 찾으려고 저장된 키를 앞에서부터 비교해야 한다. 키가 10만 개면 최대 10만 번 확인하는 O(n)이 된다.", styles, AMBER),
        Spacer(1, 6),
        paragraph("해시맵은 키를 계산해 곧바로 저장 칸인 버킷을 고르는 자료구조다.", styles["body"]),
        code_block('"name" --해시 함수--> 큰 숫자 --나머지 연산--> 버킷 3', styles),
        data_table(
            ["용어", "뜻"],
            [
                ["해시 함수", "문자열 키를 숫자로 바꾸는 계산 규칙"],
                ["버킷", "키와 값을 담는 배열의 한 칸"],
                ["인덱스", "몇 번째 버킷인지 나타내는 번호"],
                ["capacity", "현재 버킷의 전체 개수"],
            ],
            [42 * mm, 124 * mm], styles,
        ),
        paragraph("실제 코드", styles["h2"]),
        code_block('value = 0\nfor byte in key.encode("utf-8"):\n    value = (value * 31 + byte) & 0xFFFFFFFF\nreturn value % self.capacity', styles),
        paragraph("키를 UTF-8 바이트로 바꾸고 각 바이트를 이전 결과와 섞는다. 마지막 % capacity가 결과를 0부터 capacity-1 사이의 버킷 인덱스로 만든다.", styles["body"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("3. 해시맵 · 충돌과 체이닝", styles["h1"]),
        Diagram(40 * mm, draw_hash_chain),
        paragraph("서로 다른 키가 같은 버킷 번호를 얻는 현상이 충돌이다. 버킷 수가 한정되어 있으므로 충돌은 자연스럽게 생기며 오류가 아니다.", styles["body"]),
        paragraph("체이닝(chaining)", styles["h2"]),
        paragraph("같은 버킷에 들어온 여러 (key, value)를 연결 리스트로 이어 저장한다. 조회할 때는 그 버킷 안에서 실제 키가 같은 노드를 찾는다.", styles["body"]),
        paragraph("로드 팩터와 resize", styles["h2"]),
        paragraph("로드 팩터는 항목 수 / 버킷 수다. 값이 커질수록 한 버킷에 항목이 몰릴 가능성이 높아진다. 0.75를 넘으면 버킷을 2배로 늘려 체인을 짧게 유지한다.", styles["body"]),
        callout("왜 모든 키를 다시 옮기는가?", "버킷 수가 바뀌면 hash % capacity 결과도 달라진다. 따라서 배열만 늘리면 안 되고 모든 키의 인덱스를 다시 계산해야 한다. 이것이 rehash다.", styles, SKY, BLUE),
        Spacer(1, 8),
        data_table(
            ["메서드", "역할"],
            [
                ["put", "키와 값을 저장하거나 기존 값을 덮어씀"],
                ["get", "키의 값을 조회"],
                ["remove", "키와 값을 삭제"],
                ["contains", "키 존재 여부 확인"],
                ["keys / size", "전체 키 / 키 개수 반환"],
            ],
            [44 * mm, 122 * mm], styles,
        ),
        PageBreak(),
    ])

    story.extend([
        paragraph("4. 이중 연결 리스트 · 순서를 빨리 바꾸기", styles["h1"]),
        paragraph("노드(node)는 데이터 하나와 다른 노드를 가리키는 참조를 묶은 객체다. 참조는 다른 객체가 어디 있는지 가리키는 연결이라고 이해하면 된다.", styles["body"]),
        data_table(
            ["필드", "뜻", "LRU에서의 값"],
            [
                ["data", "노드가 가진 실제 데이터", "키"],
                ["prev", "바로 앞 노드 참조", "더 최근에 쓴 키"],
                ["next", "바로 뒤 노드 참조", "더 오래전에 쓴 키"],
                ["head", "리스트의 맨 앞", "MRU, 가장 최근 사용"],
                ["tail", "리스트의 맨 뒤", "LRU, 가장 오래된 사용"],
            ],
            [30 * mm, 62 * mm, 74 * mm], styles,
        ),
        Spacer(1, 6),
        Diagram(34 * mm, draw_lru),
        paragraph("왜 배열이 아닌가?", styles["h2"]),
        paragraph("배열 가운데 항목을 맨 앞으로 옮기면 사이 항목을 밀어야 해 O(n)이 될 수 있다. 이중 연결 리스트는 옮길 노드를 이미 알 때 양옆 링크만 바꿔 O(1)에 삭제·삽입한다.", styles["body"]),
        code_block("def remove_node(self, node):\n    if node.prev is None:\n        self.head = node.next\n    else:\n        node.prev.next = node.next\n\n    if node.next is None:\n        self.tail = node.prev\n    else:\n        node.next.prev = node.prev", styles),
        callout("주의", "연결 리스트만으로 특정 키의 노드를 찾으면 O(n)이다. lru_nodes 해시맵이 key → 노드를 저장해 이 문제를 해결한다.", styles, AMBER),
        PageBreak(),
    ])

    story.extend([
        paragraph("5. LRU · 왜 두 자료구조를 같이 쓰는가?", styles["h1"]),
        data_table(
            ["구조", "담당하는 일", "없다면 생기는 문제"],
            [
                ["lru_nodes 해시맵", "키로 리스트 노드를 평균 O(1)에 찾음", "리스트를 처음부터 찾아 O(n)"],
                ["lru 이중 연결 리스트", "최근 사용 순서와 tail을 보관", "가장 오래된 키를 즉시 알 수 없음"],
            ],
            [46 * mm, 70 * mm, 50 * mm], styles,
        ),
        paragraph("GET이나 SET에 성공하면 _touch(key)가 사용 순서를 갱신한다.", styles["body"]),
        code_block("def _touch(self, key):\n    node = self.lru_nodes.get(key)\n    if node is None:\n        node = self.lru.insert_front(key)\n        self.lru_nodes.put(key, node)\n    else:\n        self.lru.move_to_front(node)", styles),
        paragraph("LRU 상태 변화", styles["h2"]),
        data_table(
            ["명령", "LRU 순서: 최근 → 오래됨", "설명"],
            [
                ["SET A 1", "A", "A를 방금 사용"],
                ["SET B 2", "B ↔ A", "B가 가장 최근"],
                ["SET C 3", "C ↔ B ↔ A", "A가 가장 오래됨"],
                ["GET A", "A ↔ C ↔ B", "A가 앞으로, B가 가장 오래됨"],
                ["메모리 초과", "A ↔ C", "tail인 B를 제거"],
            ],
            [36 * mm, 66 * mm, 64 * mm], styles,
        ),
        Spacer(1, 7),
        callout("핵심 문장", "조회는 해시맵, 순서 갱신은 연결 리스트가 담당한다. 그래서 평균 O(1) LRU가 가능하다.", styles, MINT, GREEN),
        PageBreak(),
    ])

    story.extend([
        paragraph("6. 최소 힙 · 가장 빠른 만료를 빨리 찾기", styles["h1"]),
        callout("힙이 없으면", "만료된 키를 찾을 때마다 모든 키의 만료 시각을 확인해야 한다. 키가 10만 개면 최대 10만 개를 훑는 O(n)이다.", styles, AMBER),
        Spacer(1, 7),
        paragraph("힙은 우선순위가 가장 높은 항목을 빠르게 꺼내는 트리 모양 자료구조다. 최소 힙은 부모가 자식보다 작거나 같아서 가장 작은 값이 루트에 있다.", styles["body"]),
        Diagram(36 * mm, draw_heap),
        data_table(
            ["연산", "무엇을 하는가", "복잡도"],
            [
                ["peek", "루트, 즉 가장 이른 만료 확인", "O(1)"],
                ["push", "끝에 추가 후 위로 올려 규칙 복구", "O(log n)"],
                ["pop", "루트 제거 후 아래로 내려 규칙 복구", "O(log n)"],
                ["heapify", "부모≤자식 규칙을 다시 맞춤", "O(log n)"],
            ],
            [35 * mm, 91 * mm, 40 * mm], styles,
        ),
        paragraph("왜 정렬 리스트가 아닌가?", styles["h2"]),
        paragraph("정렬 리스트는 최솟값을 바로 볼 수 있지만 새 항목을 끼워 넣을 때 여러 항목을 밀어 O(n)이 될 수 있다. 최소 힙은 전체 정렬 대신 가장 이른 만료만 맨 위에 보장해 삽입·삭제를 O(log n)에 한다.", styles["body"]),
        callout("TTL에 맞는 이유", "TTL은 전체 순서가 아니라 다음에 만료될 하나가 중요하다. 그래서 최소 힙의 성질과 정확히 맞는다.", styles, MINT, GREEN),
        PageBreak(),
    ])

    story.extend([
        paragraph("7. TTL과 lazy deletion", styles["h1"]),
        paragraph("EXPIRE session 10은 두 구조를 함께 갱신한다.", styles["body"]),
        data_table(
            ["구조", "저장 내용", "왜 필요한가"],
            [
                ["expirations 해시맵", "session → 최신 expire_at", "특정 키의 최신 만료를 평균 O(1)에 조회"],
                ["expiration_heap 최소 힙", "(expire_at, session)", "전체 중 가장 빠른 만료를 확인"],
            ],
            [48 * mm, 54 * mm, 64 * mm], styles,
        ),
        paragraph("lazy deletion은 무엇인가?", styles["h2"]),
        paragraph("EXPIRE A 10 뒤 EXPIRE A 30을 실행하면 힙에 A의 옛 예약과 새 예약이 모두 남을 수 있다. 힙 중간의 옛 항목을 즉시 찾아 지우는 대신, 나중에 루트로 올라왔을 때 최신 값인지 확인한다.", styles["body"]),
        code_block("힙에서 꺼낸 값:        (12:10, A)\nexpirations 최신 값:  (12:30, A)\n결과: 서로 다르므로 12:10 예약은 무시", styles),
        callout("왜 사용하는가?", "힙 중간 삭제를 위해 별도 위치 추적과 재정렬을 구현하지 않아도 된다. 코드는 단순해지고, 오래된 항목은 필요해진 순간 안전하게 버린다.", styles, SKY, BLUE),
        paragraph("언제 실제 삭제하는가?", styles["h2"]),
        bullet("GET/DEL/EXISTS/TTL/EXPIRE 전에 해당 키의 만료를 확인할 때", styles),
        bullet("DBSIZE/KEYS/INFO/SET 전에 힙의 가장 빠른 만료부터 정리할 때", styles),
        paragraph("만료된 키는 데이터, used_memory, LRU, 최신 TTL에서 함께 제거된다. 힙의 과거 항목은 나중에 무시된다.", styles["body"]),
        PageBreak(),
    ])

    story.extend([
        paragraph("8. 메모리 관리와 eviction", styles["h1"]),
        data_table(
            ["용어", "뜻"],
            [
                ["used_memory", "현재 키와 값이 사용하는 UTF-8 바이트 합"],
                ["maxmemory", "허용할 최대 바이트. 0은 무제한"],
                ["eviction", "공간을 만들기 위해 키를 내보내는 동작"],
                ["evicted_keys", "LRU로 제거된 키의 누적 개수"],
                ["OOM", "한 항목 자체가 제한보다 커 저장할 수 없는 상태"],
            ],
            [45 * mm, 121 * mm], styles,
        ),
        paragraph("메모리 공식", styles["h2"]),
        code_block("used_memory = Σ(len(utf8(key)) + len(utf8(value)))", styles),
        paragraph("SET name Alice는 name 4바이트 + Alice 5바이트 = 9바이트다. 한글은 UTF-8에서 보통 한 글자가 3바이트라 글자 수와 바이트 수가 다를 수 있다.", styles["body"]),
        Diagram(42 * mm, draw_flow),
        paragraph("SET 뒤 메모리 초과 시", styles["h2"]),
        bullet("lru.tail에서 가장 오래 사용하지 않은 키를 얻는다.", styles),
        bullet("_delete_key로 데이터·LRU·TTL 구조에서 함께 지운다.", styles),
        bullet("지운 크기를 used_memory에서 빼고 evicted_keys를 1 늘린다.", styles),
        bullet("maxmemory 이하가 될 때까지 반복한다.", styles),
        code_block("while self.maxmemory > 0 and self.used_memory > self.maxmemory:\n    oldest_key = self.lru.tail.data\n    self._delete_key(oldest_key)\n    self.evicted_keys += 1", styles),
        PageBreak(),
    ])

    story.extend([
        paragraph("9. 명령 하나의 내부 흐름", styles["h1"]),
        paragraph("SET key value", styles["h2"]),
        bullet("만료 키 정리 → 새 항목 크기 검사 → 값 저장 → 기존 TTL 제거 → LRU 앞으로 → 초과 시 tail 제거", styles),
        paragraph("SET이 기존 키를 덮어쓰면 TTL을 지우는 이유는 새 값이 새 데이터이기 때문이다. 예전 값의 만료 약속을 새 값에 그대로 적용하지 않는다.", styles["body"]),
        paragraph("GET key", styles["h2"]),
        code_block("if self._delete_if_expired(key) or not self.data.contains(key):\n    return \"(nil)\"\nvalue = self.data.get(key)\nself._touch(key)\nreturn self._quote(value)", styles),
        bullet("TTL 확인 → 만료면 삭제하고 (nil) → 없으면 (nil) → 값 조회 → 성공한 경우만 LRU 앞으로 → 값 반환", styles),
        callout("왜 만료 키의 LRU를 갱신하지 않는가?", "이미 사용할 수 없는 데이터이므로 최근 사용으로 기록하면 안 된다. 삭제 후 없는 키처럼 처리한다.", styles, AMBER),
        Spacer(1, 7),
        paragraph("DEL key", styles["h2"]),
        paragraph("데이터만 지우면 LRU나 TTL에 죽은 키가 남는다. _delete_key 하나가 data, used_memory, lru, lru_nodes, expirations를 함께 정리해 구조 사이의 불일치를 막는다.", styles["body"]),
        paragraph("출력 빠른 정리", styles["h2"]),
        data_table(
            ["상황", "출력"],
            [
                ["SET 성공", "OK"], ["GET 없음/만료", "(nil)"],
                ["DEL/EXISTS/EXPIRE", "(integer) 1 또는 0"],
                ["TTL: 없음/설정 없음/설정 있음", "-2 / -1 / 남은 초"],
                ["한 항목이 제한보다 큼", "OOM"],
            ],
            [95 * mm, 71 * mm], styles,
        ),
        PageBreak(),
    ])

    story.extend([
        paragraph("10. 전체 예시를 손으로 따라가기", styles["h1"]),
        paragraph("maxmemory는 6바이트이고 A, 1처럼 각 문자 하나가 1바이트라고 가정한다.", styles["body"]),
        data_table(
            ["명령", "저장 데이터", "LRU 최근→오래됨", "메모리", "일어난 일"],
            [
                ["SET A 1", "A=1", "A", "2", "A 저장"],
                ["SET B 2", "A=1, B=2", "B, A", "4", "B가 가장 최근"],
                ["SET C 3", "A=1, B=2, C=3", "C, B, A", "6", "제한과 같음"],
                ["GET A", "동일", "A, C, B", "6", "A가 앞으로, B가 LRU"],
                ["SET D 4", "A=1, C=3, D=4", "D, A, C", "6", "8바이트가 되어 B 제거"],
                ["EXPIRE C 10", "동일", "동일", "6", "C 만료를 맵+힙에 저장"],
                ["10초 뒤 GET C", "A=1, D=4", "D, A", "4", "C 만료, LRU 갱신 없음"],
            ],
            [30 * mm, 38 * mm, 39 * mm, 20 * mm, 39 * mm], styles,
        ),
        Spacer(1, 8),
        callout("이 예시에서 꼭 볼 것", "B는 메모리가 부족해서 LRU eviction으로 삭제됐다. C는 시간이 끝나 TTL expiration으로 삭제됐다. 결과는 삭제지만 이유와 자료구조가 다르다.", styles, MINT, GREEN),
        Spacer(1, 8),
        paragraph("코드 전체 연결", styles["h2"]),
        Diagram(36 * mm, draw_architecture),
        bullet("data 해시맵: 실제 key → value", styles),
        bullet("lru + lru_nodes: 사용 순서와 빠른 노드 조회", styles),
        bullet("expiration_heap + expirations: 가장 빠른 만료와 최신 만료 시각", styles),
        bullet("_delete_key: 위 구조를 한 번에 정리하는 공통 삭제 경로", styles),
        PageBreak(),
    ])

    item1 = [
        (1, "String 타입 기본 동작: SET, GET, DEL, EXISTS, DBSIZE, KEYS 명령어가 모두 정상 동작하는가?", "네. MiniRedis가 여섯 메서드를 제공한다. SET은 저장과 LRU 갱신, GET은 만료 확인 후 값 반환과 LRU 갱신을 수행한다. DEL/EXISTS도 먼저 만료를 확인하고, DBSIZE/KEYS는 힙에서 만료 키를 정리한 뒤 현재 키만 대상으로 동작한다."),
        (2, "LRU 자동 제거: maxmemory 설정 후 제한 초과 시 가장 오래된 키가 자동 제거되는가?", "네. LRU는 가장 오래 사용하지 않은 키를 버리는 정책이다. 최근 사용 키는 이중 연결 리스트의 head, 가장 오래된 키는 tail에 있다. SET 뒤 제한을 넘으면 tail부터 지워 제한 이하로 만든다."),
        (3, "메모리 정보 확인: INFO memory에서 used_memory/maxmemory/evicted_keys가 규칙에 맞게 출력되는가?", "네. used_memory는 키와 값의 UTF-8 바이트 합, maxmemory는 설정한 최대 용량, evicted_keys는 메모리 부족 때문에 LRU로 제거한 누적 개수다."),
        (4, "TTL 관리: EXPIRE/TTL 규칙이 동작하며 만료된 키가 적절히 제거되는가?", "네. TTL은 키가 살아 있을 남은 시간이다. EXPIRE는 최신 만료 시각을 expirations 해시맵과 최소 힙에 저장한다. TTL은 키 없음 -2, 만료 설정 없음 -1, 설정 있음 남은 초를 반환한다."),
        (5, "에러 처리: 잘못된 명령/인자/정수 오류/OOM이 표준 형식으로 출력되는가?", "네. execute가 알 수 없는 명령과 인자 수 오류를 구분한다. 정수 변환 실패와 음수 maxmemory는 정수 오류를, 한 항목 자체가 제한보다 크면 OOM을 반환하고 저장하지 않는다."),
    ]
    add_qa_section(story, "11. 평가 Q&A · 항목 1", item1, styles)
    story.append(PageBreak())

    item2 = [
        (6, "이중 연결 리스트의 노드 구조(prev, next, data)와 핵심 메서드들이 O(1)로 동작하도록 어떻게 구성했는지 설명할 수 있는가?", "노드는 data와 앞·뒤 노드 참조를 가진다. 리스트도 head와 tail을 기억한다. 삽입·삭제·이동은 대상 노드와 이웃 링크 몇 개만 바꾸므로, 대상 노드를 이미 아는 조건에서 O(1)이다. LRU에서는 해시맵이 그 노드를 바로 찾는다."),
        (7, "해시맵에서 직접 설계한 해시 함수가 어떤 입력을 받아 어떤 과정을 거쳐 인덱스를 만드는지 설명할 수 있는가?", "문자열 키를 UTF-8 바이트로 바꾼다. 각 바이트마다 value = value * 31 + byte를 계산하고 32비트로 제한한다. 마지막 값을 버킷 수로 나눈 나머지가 인덱스다."),
        (8, "충돌 해결을 체이닝 방식으로 어떻게 구현했는지(버킷 내부 구조 선택 포함) 설명할 수 있는가?", "충돌은 다른 키가 같은 버킷 인덱스를 얻는 현상이다. 각 버킷에 DoublyLinkedList를 두고 같은 인덱스의 (key, value)를 이어 붙인다. 조회는 그 버킷 안에서 실제 키가 같은 노드를 찾는다."),
        (9, "로드 팩터 0.75 초과 시 “버킷 2배 확장”을 어떤 절차로 수행하는지 설명할 수 있는가?", "로드 팩터는 항목 수 / 버킷 수다. 0.75를 넘으면 capacity를 2배로 만들고 빈 버킷 배열을 만든다. 버킷 수가 바뀌면 인덱스도 달라지므로 기존 모든 키를 새 capacity로 다시 해시해 넣는다."),
    ]
    add_qa_section(story, "12. 평가 Q&A · 항목 2", item2, styles)
    story.append(PageBreak())

    item3a = [
        (10, "LRU 구현에서 “해시맵 + 이중 연결 리스트”가 각각 어떤 역할을 하고, 왜 둘 다 필요한지 설명할 수 있는가?", "LRU는 가장 오래 사용하지 않은 키를 버리는 정책이다. lru_nodes 해시맵은 키로 리스트 노드를 평균 O(1)에 찾고, 이중 연결 리스트는 최근 사용 순서를 유지하며 노드 이동과 tail 제거를 O(1)에 한다. 하나만 쓰면 빠른 조회 또는 순서를 잃는다."),
        (11, "O(1) LRU 달성 원리를 “조회(해시) + 갱신(리스트 이동)” 관점에서 설명할 수 있는가?", "_touch가 해시맵으로 키의 리스트 노드를 평균 O(1)에 조회한다. move_to_front는 그 노드와 이웃의 링크만 바꿔 O(1)에 앞으로 옮긴다. 가장 오래된 키도 tail로 즉시 찾는다."),
        (12, "TTL 관리에 힙을 사용한 이유(가장 빠른 만료를 빠르게 찾는 성질)를 설명할 수 있는가?", "TTL은 키가 살아 있을 남은 시간이다. 모든 키를 훑으면 O(n)이지만 최소 힙 루트에는 가장 작은 expire_at이 있다. 다음 만료 확인은 O(1), 추가와 제거는 O(log n)이므로 다음 만료를 효율적으로 관리한다."),
    ]
    add_qa_section(story, "13. 평가 Q&A · 항목 3", item3a, styles)
    story.append(PageBreak())

    item3b = [
        (13, "메모리 초과 시 eviction 흐름을 단계별로 설명할 수 있는가? (used_memory 산정/갱신, LRU 제거, evicted_keys 증가 포함)", "eviction은 공간을 만들기 위한 삭제다. 새 키+값의 UTF-8 크기를 계산하고 기존 키면 이전 크기를 빼고 새 크기를 더한다. SET 키를 LRU 앞에 둔 뒤 초과하면 tail을 모든 구조에서 지우고 used_memory를 줄이며 evicted_keys를 늘린다. 제한 이하까지 반복한다."),
        (14, "GET 명령어 전체 흐름을 순서대로 설명할 수 있는가? (TTL 확인→삭제 여부→값 반환→LRU 갱신 조건)", "TTL을 먼저 확인한다. 만료됐으면 모든 관련 구조에서 삭제하고 (nil), 키가 없어도 (nil)이다. 존재할 때만 값을 읽고 조회 성공을 기록하기 위해 LRU 앞으로 옮긴 뒤 따옴표로 감싼 값을 반환한다."),
    ]
    add_qa_section(story, "13. 평가 Q&A · 항목 3 (계속)", item3b, styles)
    story.extend([
        Spacer(1, 8),
        callout("항목 3의 연결", "LRU는 공간 문제를 해결하고, TTL은 시간 문제를 해결한다. GET은 TTL 확인 뒤 성공한 경우에만 LRU를 갱신한다.", styles, MINT, GREEN),
        PageBreak(),
    ])

    item4 = [
        (15, "“만약 LRU 대신 LFU정책을 구현한다면 자료구조를 어떻게 변경해야 하는가?”에 합리적으로 답변할 수 있는가?", "LFU는 가장 오래 안 쓴 키가 아니라 사용 횟수가 가장 적은 키를 지운다. 키→(값, 빈도, 노드) 해시맵, 빈도→같은 빈도의 키 목록 해시맵, 현재 최소 빈도 값이 필요하다. 같은 빈도는 연결 리스트로 최근 사용 순서를 정할 수 있다."),
        (16, "“데이터가 10만 건으로 늘어나면 현재 구조에서 병목이 될 수 있는 부분은 어디이며, 어떻게 개선할 수 있는가?”에 답변할 수 있는가?", "해시 분산이 나쁘면 체인이 길어져 O(n)에 가까워질 수 있어 더 좋은 해시와 초기 capacity가 필요하다. 전체 재해시는 점진적으로 나눌 수 있다. EXPIRE 반복으로 오래된 힙 항목이 쌓이면 힙을 재구성할 수 있다. KEYS는 본질적으로 O(n)이다."),
        (17, "“used_memory에 자료구조 오버헤드까지 포함하는 모델로 바꾸면 무엇이 달라지고, 공정한 비교/채점을 위해 어떤 보정이 필요할지” 설명할 수 있는가?", "노드 객체, 참조, 버킷 배열, 힙 항목까지 세면 같은 키·값이어도 Python 버전과 구현에 따라 값이 달라지고 더 빨리 eviction된다. 실행 환경, 측정법, 포함 항목, 중복 참조 규칙을 고정하거나 언어별 고정 오버헤드와 허용 오차를 정해야 한다."),
    ]
    add_qa_section(story, "14. 평가 Q&A · 항목 4", item4, styles)
    story.append(PageBreak())

    story.extend([
        paragraph("15. 마지막 용어 사전", styles["h1"]),
        data_table(
            ["용어", "한 문장 정의"],
            [
                ["LRU", "메모리가 부족할 때 가장 오래 사용하지 않은 키를 버리는 정책"],
                ["TTL", "키가 앞으로 살아 있을 남은 시간"],
                ["expiration", "TTL이 끝나 키가 만료되는 것"],
                ["eviction", "메모리 공간을 만들기 위해 키를 내보내는 것"],
                ["해시맵", "키를 해시해 저장 위치를 정하고 값을 빠르게 찾는 구조"],
                ["충돌", "서로 다른 키가 같은 버킷 인덱스를 얻는 현상"],
                ["체이닝", "충돌한 항목을 버킷 내부 리스트에 이어 저장하는 방법"],
                ["로드 팩터", "저장 항목 수를 버킷 수로 나눈 값"],
                ["이중 연결 리스트", "노드가 앞과 뒤 노드를 모두 가리키는 구조"],
                ["최소 힙", "가장 작은 값이 항상 루트에 있는 우선순위 구조"],
                ["lazy deletion", "즉시 지우지 않고 나중에 유효성을 검사해 무시하는 방식"],
                ["OOM", "메모리 제한 때문에 새 항목을 저장할 수 없는 상태"],
            ],
            [48 * mm, 118 * mm], styles,
        ),
        Spacer(1, 9),
        callout(
            "설명하는 공식",
            "문제 → 용어의 뜻 → 왜 이 구조를 쓰는가 → 실제 코드 → 시간 복잡도 순서로 말한다. 먼저 LRU는 공간 문제, TTL은 시간 문제라는 차이를 잡는다.",
            styles, MINT, GREEN,
        ),
        Spacer(1, 10),
        paragraph("최종 점검", styles["h2"]),
        bullet("LRU가 정책이고, 해시맵+연결 리스트가 그 정책의 구현 도구임을 설명할 수 있다.", styles),
        bullet("TTL이 남은 시간이고, 최소 힙이 다음 만료를 빠르게 찾는 도구임을 설명할 수 있다.", styles),
        bullet("LRU eviction과 TTL expiration의 삭제 이유가 다름을 설명할 수 있다.", styles),
        bullet("평가 질문 17개에 용어 정의와 이유를 포함해 답할 수 있다.", styles),
    ])

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    build()
