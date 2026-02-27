# 한국어 학습자를 위한 노래 추천 시스템

> **Team:** Communication In Korean (COMINKO)  
> **발표:** 학술제 PPT (`Communication In Korean_학술제 PPT.pptx/.pdf`)

---

## 프로젝트 기본

| 항목 | 내용 |
|---|---|
| **Project Title** | 한국어 학습자를 위한 노래 추천 시스템 |
| **One-line Summary** | 외국인 한국어 학습자의 TOPIK 수준에 맞는 K-POP 가사 난이도를 측정하고, 개인화된 노래를 추천하여 학습 효율을 높이는 시스템 |
| **Project Type** | Algorithm / Statistics / Data Mining / ML |
| **My Role** | 가사 난이도 스코어링 알고리즘 단독 설계·구현 (MeCab-ko + Komoran 이중 형태소 분석기, TOPIK 어간 매칭, IQR 기반 난이도 범주화); 데이터 전처리 전반 담당; 코사인 유사도 기반 추천 시스템 공동 개발; 발표 담당 |

---

## TL;DR

- **Problem:** K-POP 인기로 한국어 학습 외국인이 증가했지만, 가사 난이도를 객관적으로 파악할 수 없어 수준에 맞지 않는 노래를 선택 → 학습 효율 저하 및 학습 포기 가능성 상승
- **Approach:** TOPIK 단어장을 기준으로 가사에 등장하는 어휘의 평균 TOPIK 급수를 산출(스코어링)한 뒤, IQR로 초·중·고급을 분류하고, 사용자의 수준·장르·선호곡 입력을 받아 코사인 유사도(PCA 변수 선택 적용)로 상위 5곡을 추천
- **Main Result:** "Ditto" 입력 시 LE SSERAFIM·NEWJEANS 계열 추천, "LOSER"(BigBang) 입력 시 같은 소속사(BigBang, iKON) 곡이 포함되어 음악적 특성 유사성이 확인됨. 인디·힙합은 카이제곱 검정 결과 가사 난이도와 유의미한 연관 없음 확인.
- **Keywords:** `K-POP`, `한국어 학습`, `TOPIK`, `가사 난이도`, `MeCab-ko`, `Komoran`, `코사인 유사도`, `PCA`

---

## Motivation & Background

### Background
최근 5년간 K-POP의 세계적 인기에 힘입어 한국어를 학습하는 외국인 수가 급증했다. 노래를 통한 언어 학습은 동기 부여 및 반복 학습 효과가 입증된 교육 방법이나, 현재 학습자 스스로가 특정 곡의 가사 난이도를 정량적으로 파악할 수 있는 도구가 없다.

### Why this problem matters
- 학습자 수준에 맞지 않는 어휘가 포함된 노래를 사용하면 학습 좌절로 이어질 수 있다.
- 노래를 활용한 맞춤형 학습 자료의 부재는 K-POP을 활용한 체계적인 한국어 교육법 발전을 저해한다.

### Gap in existing work
기존 한국어 교육 연구는 노래 활용의 유효성을 논의하지만(괵셀 튀르쾨쥬 1999), **가사 난이도의 정량화·위계화** 작업이 부재하다. 기존 스트리밍 플랫폼은 청취 통계 기반 추천만 제공하며 학습자 언어 수준을 고려하지 않는다.

### Related work
- 괵셀 튀르쾨쥬. (1999). 노래를 활용한 한국어 교육 – 터키인을 대상으로 –. *국어교육연구*, 6, 88–98.  
  → 효과적인 한국어 학습을 위해 **학습자 수준에 맞는 노래 선정 기준**이 필요함을 제시.  
  → 이 연구를 기반으로, 본 프로젝트는 한국어능력시험(TOPIK) 어휘 체계를 난이도 기준으로 채택.

---

## Approach

### Algorithm / Statistics 블록

**Formulation / Variables**

| 변수 | 설명 |
|---|---|
| `difficulty_level` | 가사 어휘 TOPIK 급수의 가중 평균 (연속형) |
| `difficulty_level_category` | IQR 기반 범주: 초급(≤Q1) / 중급(Q1~Q3) / 고급(>Q3) |
| `energy` | Spotify 에너지 지표 |
| `english_ratio` | 가사 중 영어 문자 비율 |
| `korean_ratio` | 가사 중 한글 문자 비율 |
| `dps` | 초당 가사 단어 수 (가사길이 ÷ 곡 길이) |
| `specific_genres` | 장르 축소 분류: K-POP / 발라드 / 인디 / 힙합 |

**스코어링 알고리즘 (핵심 전개)**

```
1. TOPIK 단어장 전처리
   - MeCab-ko + Komoran으로 각 단어의 어간 추출 (VV, VA, NNG)
   - (어간, 품사) → TOPIK 급수 매핑 테이블 생성
   - 중복 어간은 최저 급수(쉬운 쪽) 유지

2. 가사 형태소 분석 (이중 파이프라인)
   - 1차: MeCab-ko (Viterbi 알고리즘, C++ 기반, 고속)
   - 2차: Komoran (HMM 통계 모델, Java 기반, 1차 누락 보완)
   - 동사 어미 확장: stem + "이" 형태 추가 매칭

3. 가사 난이도 계산
   - 매칭된 어휘의 TOPIK 급수 총합 ÷ 매칭 어휘 수 = difficulty_level
   - 미매칭 어휘는 분모/분자에서 제외

4. IQR 기반 범주화 (정규분포 가정)
   - ≤ Q1(0.25) → 초급
   - Q1 ~ Q3(0.75) → 중급
   - > Q3 → 고급
```

**추천 알고리즘 (코사인 유사도 + PCA)**

```
1. PCA 기반 변수 선택
   - 수치형 변수 StandardScaler 표준화
   - PCA 수행 → 로딩 행렬에서 |절대값| > 0.7 변수 추출
   - 누적 설명분산 ≤ 80% 주성분 내 변수로 최종 확정
   → 선택된 변수: energy, english_ratio, korean_ratio, dps

2. 특징 스케일링: RobustScaler

3. 코사인 유사도 행렬 계산 (전곡 × 전곡)

4. 추천 실행
   - 사용자 입력: 한국어 수준(초급/중급/고급) + 선호 장르 + 기준 곡명
   - 필터: difficulty_level_category == user_level AND specific_genres == user_genre
   - 필터된 곡 중 기준 곡과 유사도 상위 5곡 반환

5. 결과 시각화: 레이더 차트 (energy, english_ratio, korean_ratio, dps 4축)
```

**가설 검정 (카이제곱 검정)**

| 장르 | 초급 연관성 | 고급 연관성 | 유의성 |
|---|---|---|---|
| K-POP | 높음 | - | 유의 |
| 발라드 | 높음 | 높음 | 유의 |
| 인디 | - | - | 연관 없음 |
| 힙합 | - | - | 연관 없음 |

→ 가사 난이도만 기준으로 추천하면 특정 장르에 치우칠 가능성이 있음 → 장르 필터 병행 필요 확인

---

### ML/DL 블록
해당 없음

### Data Mining/Science 블록
해당 없음

### System/Pipeline 블록
해당 없음

---

## Data & Experiment

- **Dataset type:** 텍스트(가사) + 정형(Spotify 음악 특성) + 어휘 사전
- **Source:**
  - Spotify API → 음악 특성 및 메타데이터 (K-POP 장르 필터, 인기순 500곡)
  - Melon 웹 크롤링 (Selenium + BeautifulSoup) → 한국어 가사
  - 한국어능력시험(TOPIK) 단어장 → 급수별 어휘 (1~6급)
  - *(Spotify 가사 API 활용 불가 + K-POP 가사 오류 높음 → Melon으로 대체)*
- **Size:** ~500곡 (K-POP 장르, 인기순 필터링 후)
- **Label / Target definition:**  
  `difficulty_level_category` — TOPIK 어휘 매칭 기반 연속 난이도 점수를 IQR로 초급/중급/고급 3단계 분류 (사람이 직접 라벨링하지 않음, 알고리즘 자동 생성)
- **Preprocessing:**
  - 외국어(영어·일본어) 가사 곡 삭제 (정규표현식)
  - 중복 버전 곡 및 결측치 제거 (예: 윤도현밴드 - 사랑했나봐)
  - 파생변수 생성: `lyric_length`, `english_ratio`, `korean_ratio`, `dps` (초당 가사 글자수), `release_date` 정수화
  - 장르 축소·분류: k-pop·k-pop group 등 → K-POP / 발라드 / 인디 / 힙합 4종
- **Leakage checks:** 추가 필요: 명시적 누수 점검 기록 없음
- **Split:** 추천 시스템 특성상 Train/Val/Test 분리 없음 (전체 데이터 사용, 콘텐츠 기반 필터링)
- **Evaluation protocol:** 정성 평가 — 대표 곡("Ditto", "LOSER") 입력 시 추천 결과의 음악적·아티스트 유사성 육안 확인
- **Metrics:** 정량 지표 없음 (추가 필요: 사용자 만족도/정밀도 평가 미수행)
- **Environment:** Google Colab (CPU)
- **Frameworks / Libraries:**
  - `pandas`, `numpy`, `matplotlib`, `seaborn`
  - `konlpy` (MeCab-ko, Komoran)
  - `scikit-learn` (PCA, StandardScaler, RobustScaler, cosine_similarity)
  - `selenium`, `beautifulsoup4` (크롤링)
  - `spotipy` (Spotify API)
- **Reproducibility:** 추가 필요: random seed 고정 기록 없음. 데이터는 Google Drive `/ComInKo/data/` 경로에 저장.

---

## Results

### 정량 지표
추가 필요: 추천 정확도(Precision@K, NDCG 등) 공식 평가 미수행.

### 정성 결과 (슬라이드 27–28)

| 입력 곡 | 입력 수준 | 입력 장르 | 추천 결과 (상위 5곡) |
|---|---|---|---|
| Ditto | 초급 | K-POP | LE SSERAFIM, NEWJEANS(3곡), 연준 |
| LOSER (BigBang) | 추가 필요 | 추가 필요 | BigBang('꽃길', 'LAST DANCE'), iKON('사랑을 했다') 포함 |

→ 같은 가수 또는 같은 소속사(YG) 곡들 간에 음악적 특성 벡터가 유사함을 확인.

### 가설 검정 결과 (카이제곱)
- 독립변수: 가사 난이도 범주 (초급/중급/고급)
- 독립변수: 장르 (K-POP/발라드/인디/힙합)
- 추가 필요: p-value, χ² 통계량 수치 (슬라이드 22에서 방향만 제시, 수치 미명시)

### Visualization notes
- 레이더 차트: 입력 곡과 추천 5곡 각각에 대해 `energy`, `english_ratio`, `korean_ratio`, `dps` 4개 축으로 개별 시각화
- 슬라이드 11: TOPIK 1~6급 어휘 샘플 목록 시각화
- 슬라이드 22: 장르별 가사 난이도 카이제곱 사후 검정 결과

---

## Discussion

### Key observations
1. **가사 난이도 장르 편향:** K-POP·발라드는 초급과 강한 연관성을 보여, 난이도만으로 추천 시 해당 장르가 과다 추천될 수 있다.
2. **발라드의 양극화:** 발라드는 초급과 고급 모두와 연관성이 높아 내부 어휘 난이도 분산이 큰 장르임을 확인.
3. **소속사·아티스트 클러스터링:** 코사인 유사도 기반 추천이 같은 소속사 그룹 내에서 음악적 특성이 유사한 곡을 잘 포착함.
4. **형태소 이중 파이프라인의 유효성:** MeCab-ko 단독 처리 시 일부 누락 토큰이 Komoran으로 보완되어 스코어링 범위 확대.

### Interpretation
TOPIK 단어장 어휘 매칭 기반 스코어링은 학습자 수준과 직접 연결되는 객관적인 지표를 제공하며, IQR 범주화가 데이터의 왜도에 비교적 강건하다. 그러나 매칭 불가 어휘(TOPIK 수록 외 단어, 비유적 표현, 신조어)가 다수 존재해 스코어가 과소평가될 가능성이 있다.

### Trade-offs
- **정확도 vs 커버리지:** Mecab/Komoran 기반 어간 매칭은 빠르고 체계적이나 TOPIK 단어장 범위 밖 어휘를 처리할 수 없음.
- **규칙 기반 vs 딥러닝:** 규칙 기반 접근은 설명가능성이 높고 데이터가 적어도 동작하지만, 추상적·음운적 복잡성 등 의미 기반 난이도를 반영하지 못함.
- **필터 기반 추천 vs 하이브리드:** 장르+난이도 필터가 관련 없는 곡을 효과적으로 제거하지만, 필터 교차 조건이 너무 나로우해 추천 풀이 극히 작아질 수 있음.

### Failure cases / surprising results
- 인디·힙합 장르는 가사 난이도와 통계적 연관성이 없어, 해당 장르를 선호하는 학습자에게는 난이도 기준 추천의 실효성이 낮을 수 있다.
- TOPIK 단어장에 예문이 부족해 자연어 처리 딥러닝 모델(예: BERT)을 직접 활용하기 어려웠다.

### What I learned
1. 형태소 분석기마다 토큰화 결과가 다르며, 이중 파이프라인 구성이 누락 어휘를 보완하는 실질적인 효과를 가져온다.
2. 카이제곱 검정을 통해 데이터 기반으로 추천 필터 설계(장르 조건 추가)의 필요성을 사후에 검증할 수 있다.
3. 코사인 유사도는 도메인 지식 없이도 음악적 특성의 유사성을 효과적으로 포착하지만, 변수 선택(PCA)이 결과 품질을 크게 좌우한다.

---

## Limitations & Future Work

### Limitations
1. **한국어 음운 현상 미반영:** 가사 발음의 복잡성(연음, 축약 등)은 정량화되지 않아 실제 학습 난이도와 괴리가 있을 수 있다.
2. **추상적·비유적 표현:** 어휘 레벨이 낮더라도 비유·관용 표현이 많으면 실제 이해 난이도가 높을 수 있으나 현재 모델에서 미반영.
3. **데이터 규모 한계:** Spotify API 제한으로 약 500곡 수집. 추천 풀이 작아 장르+난이도 필터 후 후보가 매우 적을 수 있다.
4. **TOPIK 어휘 커버리지:** 단어장에 없는 신조어·고유명사·줄임말은 매칭 불가 → 난이도 과소평가 가능성.
5. **정량 평가 부재:** 추천 품질(Precision@K, NDCG 등)을 검증하지 않아 추천 성능을 수치로 확인할 수 없다.

### Future directions
1. **NLP 모델 도입:** TOPIK 예문 데이터를 보강하여 KR-BERT·GPT 기반 의미론적 난이도 평가 모델로 고도화.
2. **음운 복잡성 피처 추가:** 음절 변화·받침 패턴 등 발음 난이도 지표를 추가 변수로 도입.
3. **데이터 확장:** Melon/Genie 장기 크롤링으로 수집 곡 수를 1,000곡 이상으로 확대 및 장르 다양화.
4. **사용자 피드백 루프:** 실제 학습자로부터 추천 만족도 평가를 수집하고 이를 반영한 재랭킹(LightFM 등 하이브리드) 적용.
5. **평가 체계 구축:** Precision@5, nDCG, 사용자 설문 조사를 통한 오프라인·온라인 평가 프로토콜 마련.

### If I had more time
- 가사 의미 임베딩(Sentence-BERT) 기반 난이도 산출 실험
- 장르 편향성을 보정하는 다양성(diversity) 고려 추천 알고리즘 비교 실험
- 실제 외국인 학습자 그룹 대상 A/B 테스트

---

## Project Structure

```
song_recommender/
├── lylics_scoring.ipynb          # [엔트리포인트 1] 가사 난이도 스코어링 알고리즘
│                                 #   MeCab-ko + Komoran 형태소 분석
│                                 #   TOPIK 어간 매칭 → difficulty_level 산출
│                                 #   IQR 범주화 → lyrics_with_levels.csv 저장
├── lylics_scoreing.ipynb         # 스코어링 이전 버전 (오타 포함, 참고용)
├── Recommendation_by_Cos_N_PCA.ipynb  # [엔트리포인트 2] 추천 시스템
│                                 #   PCA 변수 선택 → 코사인 유사도 행렬
│                                 #   사용자 입력 → 상위 5곡 추천 + 레이더 차트
├── lyrics_with_levels.csv        # [생성 파일] 스코어링 결과 (cp949 인코딩)
├── lyrics_with_levels.xlsx       # [생성 파일] 동일 데이터 Excel 버전
├── dictionary.csv                # TOPIK 1~6급 어휘 사전 (Vocabulary, Level 컬럼)
├── Communication In Korean_학술제 PPT.pptx  # 발표자료 (36슬라이드)
├── Communication In Korean_학술제 PPT.pdf   # 발표자료 PDF 버전
├── .gitattributes                # Git LFS 설정
└── axiv/                         # 구버전 보관 폴더
    ├── lylics_scoring.ipynb
    ├── Recommendation_by_Cos_N_PCA.ipynb
    ├── 최종 파일.zip / 작업용.zip / data.zip / axiv.zip / logs.zip
```

**실행 순서:**
```
1. lylics_scoring.ipynb       → lyrics_with_levels.csv 생성
2. Recommendation_by_Cos_N_PCA.ipynb  → 추천 결과 출력
```

---

## PDF/Slides Mapping

- **Main slide deck:** `Communication In Korean_학술제 PPT.pptx` (36슬라이드, 학술제 발표용)

| README 섹션 | 해당 슬라이드 |
|---|---|
| Problem statement | Slide 4 (문제 배경), Slide 5 (선행연구 인용) |
| Why it matters | Slide 6 (기대 효과) |
| Dataset 설명 | Slide 8 (수집 방법: Spotify API + Melon 크롤링 + TOPIK 사전) |
| Feature list | Slide 9 (노래 정보·특징 컬럼 목록) |
| TOPIK 단어장 details | Slide 10–11 (급수별 설명 및 어휘 샘플) |
| Preprocessing | Slide 14 (데이터 정제), Slide 15–16 (파생변수 생성·스코어링) |
| Scoring algorithm | Slide 19 (MeCab vs Komoran 비교), Slide 20 (어간 매칭 다이어그램), Slide 21 (처리 순서 7단계) |
| 가설 검정 | Slide 22 (카이제곱 결과) |
| 추천 시스템 | Slide 24 (코사인 유사도 개념), Slide 25 (변수 선택 PCA), Slide 26 (추천 입력 예시) |
| Results 정성 | Slide 27 (Ditto 추천 결과), Slide 28 (LOSER 추천 결과) |
| 결론 | Slide 32–33 (학습 효율 극대화, K-POP 동기 강화, 데이터 기반 교육법) |
| Limitations | Slide 34 |
| 팀 역할 | Slide 35 |

- **Numbers provenance:**
  - 수집 곡 수 500곡 → Slide 8
  - 카이제곱 통계량/p-value → 추가 필요 (Slide 22에 방향만 제시, 수치 미표기)
  - 추천 결과 곡명 → Slide 27–28

- **Missing slides / gaps:**
  - 추가 필요: Slide 29–31 (결론/한계점 섹션 내 일부 슬라이드 텍스트 미추출 — 이미지 기반 구성 추정)
  - 추가 필요: 카이제곱 검정 정확한 수치 (χ², p-value, 자유도)

---

## Team

| 이름 | 역할 |
|---|---|
| 강태영 | 전처리, 모델링, 발표 |
| 권수연 | Melon 크롤링, 전처리 |
| 김재환 | 전처리, 추천시스템 모델링 |
| 왕용웅 | 단어장 전처리, 시각화, 가설 검정 |
| 이송아 | Spotify API, 전처리, 시각화 |
| 이승재 | Melon 크롤링, 전처리, 발표 |

---

## Citation & License

- **Citation info:**  
  강태영, 권수연, 김재환, 왕용웅, 이송아, 이승재. (2024). 한국어 학습자를 위한 노래 추천 시스템. *Communication In Korean (COMINKO) 학술제 발표.*
- **License:** 추가 필요
- **Papers / links:**
  - 괵셀 튀르쾨쥬. (1999). 노래를 활용한 한국어 교육 – 터키인을 대상으로 –. *국어교육연구*, 6, 88–98.
  - Spotify Web API: https://developer.spotify.com/documentation/web-api
  - MeCab-ko for Google Colab: https://github.com/SOMJANG/Mecab-ko-for-Google-Colab
  - KoNLPy (Komoran): https://konlpy.org
