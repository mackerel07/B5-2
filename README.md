# B5-2 Mini Redis

Python 3.8 이상에서 동작하는 CLI 기반 Mini Redis입니다. 과제의 필수 범위만 구현했으며 보너스 과제는 포함하지 않았습니다.

## 실행

```bash
python3 cli.py
```

큰따옴표로 감싼 공백 포함 값도 입력할 수 있습니다.

```text
mini-redis> SET greeting "hello world"
OK
mini-redis> GET greeting
"hello world"
mini-redis> quit
```

## 테스트

```bash
python3 -m unittest discover -v
```

## 파일 구조

- `doubly_linked_list.py`: LRU와 해시맵 버킷에 쓰는 이중 연결 리스트
- `hash_map.py`: 직접 만든 해시 함수와 체이닝을 사용하는 해시맵
- `min_heap.py`: `(expire_at, key)`를 저장하는 TTL 최소 힙
- `mini_redis.py`: 명령어, 메모리 계산, LRU 제거, TTL 관리
- `cli.py`: `mini-redis>` REPL과 입력 파싱
- `CONCEPT_GUIDE.md`: 평가 문항 원문과 답변을 포함한 초보자용 개념서
- `output/pdf/B5-2_Mini_Redis_개념서.pdf`: 핵심 다이어그램을 포함한 9쪽 PDF 개념서
- `scripts/build_concept_pdf.py`: PDF를 다시 생성하는 스크립트

## 필수 요구사항 대응표

| 요구사항 | 구현 위치 |
|---|---|
| 이중 연결 리스트 6개 메서드, O(1) 연산 | `DoublyLinkedList` |
| 해시맵 6개 메서드, 직접 만든 해시, 체이닝, 0.75 초과 시 2배 확장 | `HashMap` |
| 최소 힙 4개 메서드와 두 heapify | `MinHeap` |
| SET, GET, DEL, EXISTS, DBSIZE, KEYS | `MiniRedis` |
| CONFIG SET maxmemory, INFO memory | `MiniRedis` |
| EXPIRE, TTL, lazy deletion | `MiniRedis` |
| Redis 스타일 결과와 오류 | `MiniRedis.execute` |
| 따옴표 입력, exit/quit | `cli.main` |
| `dict`, `set`, `collections` 미사용 | 전체 구현 |

메모리는 UTF-8로 인코딩한 키와 값의 바이트 수만 계산합니다. 자료구조 오버헤드는 과제 규칙대로 제외합니다.
