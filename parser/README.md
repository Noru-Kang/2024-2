# 재귀하강 파서 (Recursive Descent Parser)

## 프로젝트 기본

- **Project Title**: 재귀하강 파서 (Recursive Descent Parser)
- **One-line summary**: 프로그래밍언어론 강의의 과제로 BNF 문법을 따르는 할당문 언어를 재귀하강 방식으로 구문 분석하는 파서 직접 구현
- **Project Type**: System/Pipeline
- **My Role / Key Contribution**: 
  - Parser 클래스 전체 구현 (재귀 하강 파싱 로직, 오류 처리, 표현식 평가)
  - 괄호 불균형 검출 및 연산자 누락/중복 처리
  - 메인 프로그램 실행 흐름 (파일 입출력, 결과 출력 포맷)
  - 내부/외부 문서 14페이지 작성 (문법 정의, 구현 설명, 예제)

---

## TL;DR

- **Problem**: BNF로 정의된 간단한 할당문 언어(assignment statement language)에 대한 어휘 분석 및 구문 분석기를 재귀 하강 방식으로 구현
- **Approach**: SymbolTable, LexicalAnalysis, Parser 세 클래스로 분리 설계. 각 BNF 비터미널을 재귀 함수로 매핑하고, 전역 토큰 상태를 공유하며 top-down 파싱 수행. 오류 발생 시에도 복구 메커니즘을 통해 지속 분석 가능.
- **Main Result**: 466줄의 Python 코드로 완전 동작하는 파서 구현 완료. 식별자/상수/연산자 집계, 괄호 균형 검사, 정의되지 않은 변수 참조 검출, 표현식 실시간 계산 및 심볼 테이블 관리 기능 포함.
- **Keywords**: Recursive Descent Parsing, Compiler Design, Lexical Analysis, Syntax Analysis, BNF Grammar, Symbol Table, Python, Programming Language Theory

---

## Motivation & Background

### Background
컴파일러 설계의 핵심 단계인 어휘 분석(lexical analysis)과 구문 분석(syntax analysis)을 직접 구현함으로써 프로그래밍 언어의 동작 원리를 이해하는 것이 목적이다. 재귀 하강 파싱(Recursive Descent Parsing)은 LL(1) 문법에 적합한 top-down 파싱 기법으로, 각 비터미널을 함수로 구현하여 문법 규칙을 직관적으로 반영할 수 있다.

### Why this problem matters
- 프로그래밍 언어론의 이론을 실제 코드로 구현하여 학습 효과를 극대화
- 컴파일러/인터프리터의 프론트엔드 구조 이해
- 오류 검출 및 복구 메커니즘 설계 능력 향상

### Gap in existing work
기존 파서 생성기(YACC, ANTLR 등)는 자동화 도구이지만, 본 프로젝트는 손수(hand-written) 재귀 하강 파서를 구현하여 알고리즘의 내부 동작을 깊이 이해하는 데 초점을 맞춤.

### Related work
- Aho, Sethi, Ullman의 "Compilers: Principles, Techniques, and Tools" (Dragon Book)의 재귀 하강 파싱 이론
- LL(k) 파싱 이론 및 예측적 파싱(predictive parsing) 기법
- Python의 `keyword` 모듈을 활용한 예약어 검출

---

## Approach

### System/Pipeline

#### System architecture
```
Input (.txt files)
    ↓
[LexicalAnalysis]
    ├─ Token extraction (IDENTIFIER, CONSTANT, operators, etc.)
    ├─ Symbol counting (ID, CONST, OP)
    └─ Error detection (reserved words, missing semicolon)
    ↓
[Parser] (Recursive Descent)
    ├─ program() → statements() → statement()
    ├─ expression() → term() → factor()
    ├─ term_tail() / factor_tail() (left recursion elimination)
    ├─ Symbol table update
    └─ Expression evaluation
    ↓
[SymbolTable]
    ├─ Variable storage (global dict)
    └─ Value retrieval
    ↓
Output (parse results + symbol table)
```

**클래스 구성**:
- **SymbolTable**: 전역 딕셔너리로 식별자와 값을 저장/조회
- **LexicalAnalysis**: 입력 텍스트를 스캔하여 토큰(token type, token string)을 생성
- **Parser**: 토큰 스트림을 소비하며 BNF 규칙에 따라 재귀적으로 비터미널 함수 호출

#### Data flow
1. `.txt` 파일의 각 줄을 읽어 `LexicalAnalysis` 객체 생성
2. `lexical()` 메서드가 토큰을 하나씩 추출하여 `(token_type, token_string)` 반환
3. `Parser`가 `analyze()`를 호출하여 전역 변수 `next_token`, `token_string`에 저장
4. 비터미널 함수들이 현재 토큰을 확인하고 다음 토큰으로 진행
5. 표현식 계산 결과를 `SymbolTable`에 저장
6. 모든 문장 처리 후 심볼 테이블을 정렬하여 출력

#### Control flow
- **program()**: 프로그램 시작, EOF가 아니면 statements() 호출
- **statements()**: statement() 처리 후 세미콜론이 있으면 재귀적으로 다음 statements() 호출
- **statement()**: IDENTIFIER 확인 → ASSIGN_OP(`:=`) 확인 → expression() 호출 → 결과를 심볼 테이블에 저장
- **expression()**: term() 호출 후 term_tail()로 덧셈/뺄셈 연쇄 처리
- **term()**: factor() 호출 후 factor_tail()로 곱셈/나눗셈 연쇄 처리
- **factor()**: 괄호 표현식, 식별자, 상수 중 하나를 처리

**재귀 제거**: BNF의 좌재귀(left recursion)를 `term_tail`, `factor_tail` 등으로 우재귀로 변환하여 무한 재귀 방지

#### Deployment/Serving
```bash
python main.py <파일명>.txt [<파일명2>.txt ...]
```
- 명령줄 인자로 `.txt` 파일 경로를 받아 순차 처리
- 각 파일의 각 줄을 독립적으로 분석
- 빈 줄은 자동으로 건너뜀

#### Monitoring/Logging
- 각 줄마다 분석 결과 출력:
  - 입력 코드 원문
  - `ID: <개수>; CONST: <개수>; OP: <개수>;`
  - 에러/경고 메시지 (있으면)
  - `(OK)` 또는 에러 목록
- 파일 종료 시 전역 심볼 테이블 출력 (`Result ==> x: 10; y: 15`)

#### Scaling/Performance
- 단일 파일 단일 쓰레드로 충분 (교육용 소규모 입력)
- 토큰 단위 스트리밍 방식으로 메모리 효율적
- 복잡도: O(n) (n = 입력 문자 수)

---

### ML/DL
해당 없음

### Algorithm/Statistics
해당 없음

### Data Mining/Science
해당 없음

---

## Data & Experiment

### Dataset type
텍스트 파일 (`.txt` 형식의 커스텀 언어 소스 코드)

### Source
- 과제 명세에서 제공되는 공식 테스트 케이스
- 개인 설계 테스트 케이스: 직접 설계한 edge case 및 오류 검증용 입력 파일 (프로젝트에 업로드됨)

### Size
과제용 소규모 입력 (수십 줄 내외)

### Label/Target definition
- 없음 (파서는 입력의 구문 정확성을 검증하고 변수 값을 계산하는 것이 목표)

### Preprocessing
- 각 줄의 양 끝 공백 제거 (`line.strip()`)
- 빈 줄 건너뛰기

### Leakage checks
해당 없음 (테스트/검증 데이터 분리 개념 없음)

### Split
Train/Val/Test 개념 없음 (단일 입력 처리)

### Evaluation protocol
1. 정상 입력에 대해 `(OK)` 출력 및 올바른 변수 값 계산 여부 확인
2. 오류 입력에 대해 적절한 경고/에러 메시지 출력 여부 확인
3. 심볼 테이블의 변수-값 대응 정확성 확인
4. 개인 테스트: 직접 설계한 테스트 케이스로 edge case 검증
5. 공식 평가: 과목 담당 교수가 제공한 테스트 세트로 채점

### Metrics
- **정확성**: 올바른 토큰 개수 집계 (ID, CONST, OP)
- **오류 검출률**: 의도적 오류 입력에 대한 경고/에러 발생 여부
- **복구 능력**: 중복 연산자 제거 등 오류 복구 후 지속 분석 여부
- **과제 평가**: 공식 테스트 케이스 통과율

### Environment
- **OS**: macOS
- **CPU/GPU**: 일반 개발 환경 (CPU only)
- **Python 버전**: 3.13.0
- **IDE**: VSCode

### Frameworks/Libraries
- Python 표준 라이브러리만 사용 (`os`, `sys`, `keyword`)
- 외부 의존성 없음

### Reproducibility
- `main.py` 실행 시 항상 동일한 입력에 대해 동일한 출력 생성
- 전역 변수 초기화를 각 파일/줄마다 수행하여 재현성 보장

---

## Results

### Baseline method
- 수동 파싱 (사람이 직접 토큰을 세고 문법을 확인)

### This Work
- **재귀하강 파서 (Recursive Descent Parser)** 구현
- **토큰 집계**: 식별자, 상수, 연산자 개수 자동 집계
- **오류 검출**: 
  - 괄호 불균형 검출 (`'(' 없음` / `')' 없음`)
  - 연산자/피연산자 누락 검출
  - 정의되지 않은 변수 참조 검출
  - 예약어 사용 검출
  - 세미콜론 누락/이중 세미콜론 검출
- **표현식 평가**: 실시간으로 산술 표현식을 계산하여 변수 값 할당
- **오류 복구**: 중복 연산자 제거 후 계속 분석 진행

### Additional results
- **전체 코드 길이**: 466줄 (Python)
- **구현 완성도**: 모든 BNF 규칙 대응 완료
- **문서화**: 14페이지 내부/외부 문서 작성 (문법 정의, 구현 세부사항, 예제)
- **과제 평가 결과**: 약 40팀 중 20등 (중위권)
  - Python 구현으로 C/Java 가산점 미적용 추정
  - 기본 기능 구현 완료, 동일 점수대 다수 존재

### Statistical significance / confidence
- 공식 테스트 세트 통과 (과제 명세 요구사항 충족)
- 개인 설계 테스트 케이스로 edge case 검증 완료

### Visualization notes
PDF 문서 내 BNF 문법 표, 토큰 코드 표, 클래스 다이어그램 포함

---

## Discussion

### Key observations
1. **재귀 하강의 직관성**: 각 BNF 비터미널을 함수로 매핑하여 코드 구조가 문법과 1:1 대응
2. **좌재귀 제거의 필요성**: `term_tail`, `factor_tail` 도입으로 무한 재귀 방지
3. **전역 상태 관리**: `next_token`, `token_string`을 전역 변수로 두어 함수 간 토큰 공유
4. **오류 복구 메커니즘**: 중복 연산자를 자동 제거하고 `op_count` 조정하여 지속 분석 가능
5. **심볼 테이블의 간결함**: Python 딕셔너리로 충분히 구현 가능

### Interpretation
- 간단한 문법(할당문 + 산술 표현식)이지만, 어휘 분석/구문 분석/의미 분석(표현식 평가)의 전체 흐름을 포괄
- 오류 처리 과정에서 Warning과 Error를 구분하여 사용성 향상
- 팀 협업: 어휘 분석(jh)과 구문 분석(ty)으로 역할 분담

### Trade-offs
- **정확도 vs 복잡도**: LL(1) 문법으로 제한하여 구현 복잡도를 낮춤 (lookahead 1개만 사용)
- **오류 복구 vs 정확성**: 중복 연산자를 무조건 제거하는 방식으로 일부 오류를 무시할 수 있음
- **구현 언어 선택 (Python vs C/Java)**:
  - 장점: 빠른 개발, 읽기 쉬운 코드, 딕셔너리/리스트 등 자료구조 간편
  - 단점: 과제 평가에서 C/Java 가산점 미적용 (순위에 영향)
  - 결론: 학습 목적과 구현 편의성을 우선시한 선택

### Failure cases / surprising results
- 예약어 사용 시 Warning만 출력하고 계속 진행 (Error로 중단하지 않음)
- 할당 연산자 오류(`:=` 대신 `=` 사용) 시에도 값 할당이 이루어짐 (관대한 오류 처리)

### What I learned
1. 컴파일러 이론과 실제 구현 사이의 간극을 좁히는 경험
2. 재귀 함수를 통한 문법 규칙 표현의 우아함
3. 오류 복구 메커니즘 설계의 중요성 (한 오류가 전체 분석을 중단시키지 않도록)
4. 구현 언어 선택의 trade-off: 빠른 개발과 가독성(Python)을 선택했지만, 평가 기준에 따른 불이익도 존재함을 인지
5. 개인 테스트 케이스 설계의 중요성: 공식 테스트만으로는 edge case를 완전히 검증하기 어려움

---

## Limitations & Future Work

### Limitations
1. **LL(1) 문법으로 제한**: lookahead가 1개뿐이라 복잡한 문법(예: ambiguous grammar) 처리 불가
2. **좌결합성 문제**: `term_tail` 재귀 방식에서 연산 순서가 오른쪽부터 계산됨 (수정 필요)
3. **심볼 테이블 스코프 없음**: 전역 변수만 지원, 블록/함수 스코프 개념 없음
4. **타입 검사 없음**: 모든 값을 정수로 가정, 타입 불일치 검사 없음
5. **구현 언어에 따른 평가 불이익**: Python 선택으로 C/Java 가산점 없음 (성적 영향)

### Future directions
1. **LR 파싱 구현**: 더 넓은 범위의 문법(LR(k)) 지원
2. **AST 생성**: 추상 구문 트리(Abstract Syntax Tree)를 명시적으로 구축하여 중간 표현 제공
3. **타입 시스템**: 정수/실수/문자열 등 다양한 타입 지원 및 타입 검사
4. **제어문 추가**: if/while/for 등 제어 구조 확장
5. **함수 정의/호출**: 사용자 정의 함수 및 스코프 관리

### If I had more time
- 더 많은 edge case 테스트 (괄호 중첩, 복잡한 표현식, 다양한 오류 조합)
- 백트래킹 기반 파서(recursive descent with backtracking) 구현
- 중간 코드 생성 및 간단한 가상 머신 실행

---

## Project Structure

```
parser/
├── main.py                              # 전체 구현 (466줄)
│   ├── SymbolTable                      # 심볼 테이블 클래스
│   ├── LexicalAnalysis                  # 어휘 분석기
│   │   ├── advance()
│   │   ├── skip_whitespace()
│   │   ├── get_number()
│   │   ├── get_identifier()
│   │   ├── lexical()                    # 토큰 추출
│   │   ├── analyze()                    # 전역 토큰 갱신
│   │   └── print_result()
│   ├── Parser                           # 구문 분석기 (재귀 하강)
│   │   ├── program()
│   │   ├── statements()
│   │   ├── statement()
│   │   ├── expression()
│   │   ├── term_tail()
│   │   ├── term()
│   │   ├── factor_tail()
│   │   ├── factor()
│   │   ├── const()
│   │   └── ident()
│   └── __main__                         # 파일 입출력 및 실행
└── Internal & External Documents.pdf    # 14페이지 프로젝트 문서
    ├── 문법 정의 (BNF)
    ├── 토큰 코드 표
    ├── 클래스 구조 설명
    ├── 오류 처리 규칙
    └── 실행 방법 및 예제
```

---

## PDF/Slides Mapping

### Main slide deck(s)
- **파일명**: `Internal & External Documents.pdf`
- **페이지**: 14페이지
- **작성일**: 2024년 (추정, PDF 메타데이터 기준)
- **작성자**: 강태영, 송재호

### Slide-to-README mapping

| 슬라이드/섹션 | 내용 | README 섹션 |
|---------------|------|-------------|
| **표지 (1페이지)** | 프로젝트 제목, 과목명, 팀원 정보 | 프로젝트 기본 |
| **문법 정의 (2-4페이지)** | BNF 규칙 전체 (`<program>` ~ `<const>`) | Approach → Control flow |
| **토큰 코드 (5페이지)** | IDENTIFIER=1, ADD_OP=3 등 토큰 코드 표 | Approach → Data flow |
| **SymbolTable 클래스 (6페이지)** | 메서드 설명, 전역 딕셔너리 사용 | Approach → System architecture |
| **LexicalAnalysis 클래스 (7-8페이지)** | 속성, 메서드 상세 (`lexical()`, `analyze()`) | Approach → System architecture |
| **Parser 클래스 (9-11페이지)** | 재귀 하강 로직, 비터미널별 함수 설명 | Approach → Control flow |
| **오류 처리 (12페이지)** | Warning/Error 분류, 메시지 목록 | Results → 오류 검출 |
| **실행 방법 (13페이지)** | 명령줄 실행 예제 (`python main.py ...`) | Data & Experiment → Deployment |
| **개발 환경 (14페이지)** | Python 3.13.0, VSCode | Data & Experiment → Environment |

### Numbers provenance
- **코드 길이**: 466줄 (main.py 실제 줄 수 확인)
- **클래스 개수**: 3개 (SymbolTable, LexicalAnalysis, Parser)
- **토큰 종류**: 11개 (IDENTIFIER ~ EOF)
- **오류 메시지 종류**: 13개 (Warning 7개, Error 6개)

### Any missing slides / gaps
- **테스트 케이스**: 개인 설계 테스트 파일은 업로드되었으나 PDF에 명시되지 않음
- **성능 측정**: 파싱 속도, 메모리 사용량 등 정량적 성능 지표 없음
- **비교 분석**: 다른 파싱 기법(SLR, LALR 등) 대비 장단점 비교 없음
- **과제 평가 세부**: 공식 테스트 세트 내용 및 채점 기준 비공개

---

## Citation & License

### Citation info
```
Title: 재귀하강 파서 (Recursive Descent Parser)
Authors: 강태영, 송재호
Course: 프로그래밍 언어론
Instructor: 김진성 교수
Institution: [학교명 - 추가 필요]
Department: 응용통계학과/소프트웨어학부
Year: 2024
```

### License
추가 필요: 라이선스 정책 명시 (MIT, Apache 2.0, 교육용 비공개 등)

### Papers/links
- Aho, A. V., Sethi, R., & Ullman, J. D. (1986). *Compilers: Principles, Techniques, and Tools*. Addison-Wesley. (Dragon Book)
- Python `keyword` module documentation: https://docs.python.org/3/library/keyword.html
- LL parser theory: https://en.wikipedia.org/wiki/LL_parser
- Recursive descent parsing: https://en.wikipedia.org/wiki/Recursive_descent_parser

---

## 실행 예제

### 입력 파일 (example.txt)
```
x := 10;
y := x + 5;
z := (x + y) * 2;
```

### 실행 명령
```bash
python main.py example.txt
```

### 예상 출력
```
'example.txt' 파일 실행
x := 10 ;
ID: 1; CONST: 1; OP: 0;
(OK)

y := x + 5 ;
ID: 2; CONST: 1; OP: 1;
(OK)

z := ( x + y ) * 2 ;
ID: 4; CONST: 1; OP: 2;
(OK)

Result ==> x: 10; y: 15; z: 50
```

---

## 팀원 기여도

| 이름 | 학번 | 주요 기여 |
|------|------|-----------|
| **강태영** | 20204885 | Parser 클래스 전체 구현 (재귀 하강 로직, 오류 처리, 표현식 평가), 메인 실행 흐름, 문서 작성 (14페이지) |
| **송재호** | 20216946 | LexicalAnalysis 클래스 구현 (토큰 추출, 예약어 검사, 세미콜론 검증), SymbolTable 클래스, 전역 변수 설계 |

---

**프로젝트 완료 일자**: 2024년 (추정)  
**최종 업데이트**: 2026년 2월 26일 (README 작성)
