# 딥러닝을 활용한 주가 예측 — KR-FinBERT 감성분석을 활용한 삼성전자 주가 예측 (논문 구현)

---

## 프로젝트 기본

| 항목 | 내용 |
|------|------|
| **Project Title** | 딥러닝을 활용한 주가 예측 — KR-FinBERT 감성분석을 활용한 주가지수 예측 (논문 구현) |
| **One-line Summary** | 뉴스 헤드라인에서 감성을 추출해 기술적 지표에 추가함으로써, 감성 정보가 삼성전자 주가 예측 성능에 미치는 영향을 정량적으로 검증한다. |
| **Project Type** | ML/DL |
| **My Role / Key Contribution** | 개인 프로젝트로 전체 파이프라인(데이터 수집·전처리·감성분석·피처 엔지니어링·학습·평가) 직접 구현. 원 논문(KOSPI 상위 30종목)의 방법론을 단일 종목(삼성전자 005930)에 적용하고, 기간을 2014–2023으로 확장. 시가총액 비율 가중치 기반 감성도(Sentiment degree) 및 반응도(Sensitive degree) 지표 설계 및 이동평균 실험 수행. |

---

## TL;DR

- **Problem**: 기술적 지표만으로는 뉴스에서 발생하는 심리적 가격 변동을 포착할 수 없다. 감성 정보를 피처로 추가했을 때 주가 예측 성능이 개선되는지 실증적으로 확인하고자 한다.
- **Approach**: KR-FinBERT로 한경 뉴스 헤드라인의 감성(긍정/부정)을 추출 → 시가총액 비율을 가중치로 감성도·반응도 산출 → 90일 이동평균 적용 → TA-Lib 기술적 지표와 결합 → XGBoost / RandomForest로 삼성전자 종가 예측.
- **Main Result**: 감성 피처 추가 시 XGBoost RMSE가 **15,756 → 8,711** (-44.7%), RandomForest가 **15,759 → 8,438** (-46.4%)로 크게 개선됨.
- **Keywords**: `KR-FinBERT`, `감성분석`, `주가예측`, `XGBoost`, `RandomForest`, `TA-Lib`, `시계열`, `삼성전자`

---

## Motivation & Background

- **Background**: 주가는 기술적 지표·거시 수치에 큰 변화가 없어도 뉴스·루머 하나에 급변할 수 있다. 기존 정형화된 지표 기반 모델은 이러한 심리적 요인을 반영하지 못하는 구조적 한계가 있다.
- **Why this problem matters**: 뉴스는 투자자에게 정보를 전달하는 핵심 매개체로, 주식시장과 뉴스 사이에는 밀접한 관계가 존재한다. 자동화된 감성 분류를 통해 이 정보를 피처화하면 예측 모델의 설명력을 높일 수 있다.
- **Gap in existing work**: 기존 주가 예측 연구 대다수는 기술적·재무 지표 위주이며, 뉴스 감성 정보를 시가총액 비율로 가중(weighted by market cap ratio)하여 기술적 지표와 결합한 사례는 제한적이다. 기존 Word2Vec, Bag-of-Words 기반 방법은 한국어 금융 도메인에서 성능이 떨어진다.
- **Related work**:
  1. 장주현, 김재윤 (2023). "KR-FinBERT 뉴스 감성분석을 활용한 KOSPI 주가지수 예측." 2023년도 한국통신학회 동계종합학술발표회. — **본 구현의 원 논문**. KOSPI 상위 30종목·빅카인즈 73,539건 뉴스 사용.
  2. 이우식 (2017). "딥러닝분석과 기술적 분석 지표를 이용한 한국 코스피주가지수 방향성 예측." 한국데이터정보과학회지.
  3. 어균선, 이건창 (2020). "합성곱 신경망을 이용한 주가방향 예측: 상관관계 속성선택 방법을 중심으로." Information Systems Review.
  4. 허준영, 양진용 (2015). "SVM 기반의 재무 정보를 이용한 주가 예측." 정보과학회 컴퓨팅의 실제 논문지.
  5. KR-FinBERT: https://huggingface.co/snunlp/KR-FinBert-SC

---

## Approach

### ML/DL

**Model / Architecture**

단일 추론 단계가 아닌 2-stage 파이프라인:

1. **Stage 1 — 감성 점수 산출 (KR-FinBERT)**
   - 모델: `snunlp/KR-FinBert-SC` (HuggingFace Transformers)
   - 입력: 뉴스 헤드라인 텍스트(한국어 금융 뉴스)
   - 출력: `positive / neutral / negative` 레이블
   - 중립(neutral) 제거 후 `positive=+1, negative=-1`로 수치화

2. **Stage 2 — 주가 회귀 예측 (XGBoost / RandomForest)**
   - 입력: 기술적 지표 + 감성도 이동평균 피처 (하단 피처 목록 참조)
   - 출력: 삼성전자 일별 종가(Close)
   - XGBoost: `objective='reg:squarederror'`, `tree_method='hist'`, `device='cuda'`
   - RandomForest: `sklearn.ensemble.RandomForestRegressor` 기본 하이퍼파라미터

**피처 목록 (최종 입력 Features)**

| 카테고리 | 피처 |
|----------|------|
| 감성 지표 | `Sentiment_degree_ma` (90일 MA), `Sensitive_degree_ma` (90일 MA) |
| 모멘텀/추세 | `TRIX(30)`, `ADX(14)`, `ADXR(14)`, `DX(14)`, `CMO(14)`, `BOP` |
| 가격/거래량 | `MFI(14)`, `fastK(5)`, `fastD(3)` (Stochastic), `MINUS_DM(14)`, `ma_macdhist` (MACD hist 9일 MA) |

**감성도·반응도 계산식**

```
Sentiment degree (일별) = avg(sentiment score) × (Samsung Market Cap / KOSPI Market Cap)
Sensitive degree (일별) = avg(|sentiment score|) × (Samsung Market Cap / KOSPI Market Cap)

Sentiment_degree_ma = Sentiment degree의 90일 이동평균
Sensitive_degree_ma = Sensitive degree의 90일 이동평균
```

**Loss & Optimization**
- Loss: MSE (`reg:squarederror`)
- XGBoost: 트리 기반 gradient boosting, 하이퍼파라미터 튜닝 없이 default 사용
- RandomForest: 앙상블 random forest, 하이퍼파라미터 튜닝 없이 default 사용

**Training Strategy / Key Mechanisms**
- 시계열 데이터이므로 `shuffle=False`로 시간순 80/20 분할 유지 (미래 데이터 누수 방지)
- MinMaxScaler 적용 (fit: train set only, transform: test set)
- 감성 피처의 이동 평균 윈도우(1·7·15·30·90일) 실험을 통해 90일이 최적임 확인
- 비교군: 감성 피처(`Sentiment_degree_ma`, `Sensitive_degree_ma`)만 제거한 동일 모델

**Inference / Serving Path**
- 온라인 서빙 없음. 배치 추론(노트북 내 전체 실행).

**Ablation / Design Choices**

**① 감성 기간(이동평균 윈도우) Ablation**: MA 1→7→15→30→90일로 증가시키며 XGBoost RMSE 추적

| MA 윈도우 | XGBoost Test RMSE | XGBoost R² |
|-----------|-------------------|------------|
| 1일 | 14,960.27 | -5.3193 |
| 7일 | 13,471.01 | -4.1238 |
| 15일 | 11,927.79 | -3.0171 |
| 30일 | 9,655.50 | -1.6323 |
| **90일** | **8,711.45** | **-1.1428** |

→ 긴 이동평균 윈도우일수록 감성 피처의 노이즈가 줄어 예측 성능 개선됨.

**② 가격 지표(OHLCV) 의도적 제외** (발표자료 Slide 54–55):
- 시가·고가·저가·종가·거래량 등 가격 지표를 포함하면 **감성 지표의 피처 중요도가 심각하게 저하**됨.
- 감성 지표만의 순수 기여도를 측정하기 위해 이동 지표(Momentum/Oscillator)만 사용하는 설계를 선택.
- 즉 이 프로젝트는 "감성분석 피처가 이동 지표 군에 추가될 때의 효과"를 검증하는 것이 핵심 목적.  

---

## Data & Experiment

- **Dataset type**: 정형(주가·기술적 지표) + 텍스트(뉴스 헤드라인 → 수치 변환)
- **Source**:
  - 삼성전자 주가: `FinanceDataReader` (symbol: `005930`)
  - 삼성전자 시가총액: `yfinance` (symbol: `005930.KS`) × 발행주식수
  - 뉴스 데이터: 한국경제 뉴스 (`data/NewsResult_YYYYMMDD-YYYYMMDD.xlsx`, 연도별 10개 파일)
  - KOSPI 상장시가총액: `data/data_5434~5530_20241028.csv` (5개 파일 병합, 출처: KRX 추정)
- **Size**:
  - 주가: 삼성전자(005930) 2014-01-01 ~ 2023-12-31 (약 2,450 거래일)
  - 뉴스: 한경 뉴스 2014–2023 연도별 xlsx 10개 파일
  - KOSPI 시가총액: 5개 종목 코드별 csv (2024-10-28 수집 기준)
- **Label / Target definition**: `Close` (삼성전자 일별 종가, 회귀 문제)
- **Preprocessing**:
  1. 뉴스 헤드라인 KR-FinBERT 감성 레이블링 → `positive=+1, neutral=0, negative=-1`
  2. 중립(neutral) 뉴스 제거
  3. 일별 감성 점수 평균(groupby date → mean)
  4. 시가총액 비율(Samsung / KOSPI) 가중 → 감성도(Sentiment degree), 반응도(Sensitive degree) 생성
  5. 90일 롤링 이동평균 적용
  6. 삼성전자 주가·시가총액(yfinance)과 날짜 인덱스 기준 left merge
  7. KOSPI 시가총액 데이터 추가 merge
  8. `avg_score`, `Market Cap`, `상장시가총액` 컬럼 최종 drop (순수 피처만 유지)
  9. TA-Lib 기술적 지표 10종 추가 계산
  10. 결측치: `ffill` (forward fill) → X 행렬에 잔여 결측 시 `bfill` 추가 적용
  11. 이상치: `Open == 0` 행 제거(액면분할 영향)
  12. IQR 이상치 제거는 코드에 작성되었으나 주석 처리(미적용)
- **Leakage checks**: `shuffle=False` 시계열 분할로 미래 데이터 누수 방지. MinMaxScaler fit은 train set에만 적용.
- **Split**: Train 80% (2014–2022년 초), Test 20% (약 2022년 말–2023년 말), 시간 순 비례 분할 (`test_size=0.2, shuffle=False`)
- **Evaluation protocol**: Hold-out (time-series split). 교차검증 코드(`TimeSeriesSplit(n_splits=5)`) 선언되어 있으나 최종 평가는 단일 hold-out으로 수행.
- **Metrics**: RMSE (예측값과 실제 종가의 편차 크기 중심), R² (결정계수, 기준선 대비 설명력)
- **Environment**: Google Colaboratory, CUDA GPU (XGBoost `device='cuda'`), Python 3.10
- **Frameworks / Libraries**:
  - `transformers` (KR-FinBERT 추론)
  - `xgboost`, `sklearn` (모델 학습·평가)
  - `FinanceDataReader`, `yfinance` (주가·시총 수집)
  - `ta-lib` (기술적 지표)
  - `pandas`, `numpy`, `matplotlib`, `tqdm`
- **Reproducibility**: `random.seed(42)`, `np.random.seed(42)`, XGBoost/RF `random_state=42`

---

## Results

### 메인 결과: 감성 피처 포함 vs 미포함 (MA=90일)

| 모델 | 피처 구성 | Test RMSE | Test R² |
|------|-----------|-----------|---------|
| XGBoost | 기술적 지표만 (Baseline) | 15,756.86 | -6.0102 |
| RandomForest | 기술적 지표만 (Baseline) | 15,759.21 | -6.0123 |
| **XGBoost** | **기술적 지표 + 감성 피처 (MA=90)** | **8,711.45** | **-1.1428** |
| **RandomForest** | **기술적 지표 + 감성 피처 (MA=90)** | **8,437.88** | **-1.0103** |

> RMSE 단위: 삼성전자 종가(KRW). 감성 피처 추가 시 XGBoost -44.7%, RandomForest -46.4% RMSE 감소.

### 감성 피처 MA 윈도우별 XGBoost RMSE Ablation

| MA 윈도우 | Test RMSE | Test R² |
|-----------|-----------|---------|
| 1일 | 14,960.27 | -5.3193 |
| 7일 | 13,471.01 | -4.1238 |
| 15일 | 11,927.79 | -3.0171 |
| 30일 | 9,655.50 | -1.6323 |
| 90일 | 8,711.45 | -1.1428 |

### 원 논문 결과 (참고, 단위·데이터 상이)

| MA 기간 | 벤치마킹(동일가중) | 뉴스빈도 가중 | 시가총액 가중 | 모멘텀만 |
|---------|-------------------|--------------|-------------|---------|
| 1일 | 562.48 | 557.67 | 561.16 | 563.81 |
| 7일 | — | 545.84 | 557.70 | 548.14 |
| 15일 | — | 544.05 | 548.31 | 567.85 |
| 30일 | — | 520.11 | 469.23 | 524.00 |
| 90일 | — | 561.82 | 426.99 | 309.06 |

> 원 논문은 KOSPI 지수 RMSE, 본 구현은 삼성전자 종가(KRW) RMSE로 단위 상이 — 직접 비교 불가.

### Statistical Significance / Confidence
- 단일 hold-out split이므로 통계적 유의성 검정 없음.

### Visualization Notes
- **그림 1 (with sentiment)**: 2014–2024 전 구간 실제 종가 vs XGBoost/RF 예측 비교. Train 구간은 두 모델 모두 실제값에 거의 완벽히 피팅. Test 구간(2022말–2024)은 추세 방향은 일부 추종하나 절대값 편차 존재.
- **그림 2 (without sentiment)**: 감성 피처 제거 시 Test 구간 예측값 불안정성이 두드러짐 (급격한 상하 진동). 감성 피처의 안정화 효과 시각적으로 확인 가능.
- **그림 3 (Feature Importance)**: XGBoost feature importance (weight 기준) — 추가 필요: 노트북 실행 후 출력 이미지 직접 확인 요망.

---

## Discussion

- **Key observations**:
  1. **기술 지표에 감성 지표를 추가하는 경우 성능이 더 뛰어남** (발표자료 Slide 53). XGBoost RMSE 15,756 → 8,711 (-44.7%), RandomForest 15,759 → 8,438 (-46.4%).
  2. MA 윈도우가 길어질수록 RMSE 단조 감소 → 단기 노이즈를 제거한 장기 감성 트렌드가 예측에 더 유효.
  3. **가격 지표(OHLCV) 포함 시 감성 지표 중요도 심각하게 저하** (Slide 55) → 피처 설계에서 이동 지표만 사용한 이유.
  4. Train RMSE와 Test RMSE 차이가 극명 → 두 모델 모두 훈련 구간에 과적합(train R² ≈ 1, test R² 음수).
  5. Test R²가 음수 — 절대 가격 예측은 여전히 어렵지만, 감성 피처 추가로 예측 불안정성(Slide 52의 폭발적 진동) 억제 효과 확인.
- **Interpretation**: 감성 정보는 기술적 지표만으로 설명하지 못하는 가격 변동 요소를 보완하며, 특히 장기 감성 트렌드(90일 MA)가 단기 노이즈 대비 효과적임. 단, 비선형적 시장 역학을 단순 회귀로 완전히 포착하는 것은 한계가 있다.
- **Trade-offs**: 감성 피처 추가 시 전처리 복잡도(KR-FinBERT 추론 시간, 시가총액 데이터 수집 등) 증가. 그러나 예측 정확도(RMSE) 이득이 명확하여 비용 대비 효과 긍정적.
- **Failure cases / Surprising results**: 이동평균 90일~이후 성능이 더 올라갈 가능성이 있으나 탐색하지 않음. R²가 여전히 음수인 것은 절대 종가 예측의 내재적 어려움을 반영.
- **What I learned**:
  1. 텍스트 감성 정보를 수치 피처로 변환해 정형 모델에 결합하는 멀티모달 파이프라인 설계 경험.
  2. 시계열 예측에서 데이터 누수 방지(shuffle=False, scaler fit on train)의 중요성.
  3. RMSE 개선과 R² 음수가 공존할 수 있음 — 절대값 정확도와 트렌드 설명력은 별개 지표.

---

## Limitations & Future Work

**Limitations**

1. **원 논문 완벽 구현 불가** (발표자료 Slide 56–57): 원 논문은 KOSPI 상위 30종목 × BigKinds 73,539건 뉴스를 사용했으나, 관련 세부 데이터 미공개·대량 수집 불가로 인해 단일 종목(삼성전자) + 한경 뉴스 데이터로 범위를 축소하여 구현.
2. **단일 종목(삼성전자) 한정**: 원 논문의 30종목 대비 일반화 가능성 낮음.
3. **시가총액 비율 고정**: 수집 데이터가 2024-10-28 특정 시점 기준 → 2014–2023 기간 동안의 동적 비율 변화 미반영.
4. **R² 음수**: 테스트 구간 두 모델 모두 평균 예측보다 성능이 낮아 실제 투자 활용에는 한계.
5. **가격 지표 의도적 제외**: OHLCV 포함 시 감성 중요도 저하로 제외했으나, 이로 인해 절대 가격 예측 성능 자체가 낮아짐.
6. **하이퍼파라미터 미조정**: XGBoost, RF 모두 default 파라미터 사용.

**Future Directions**

1. KOSPI 상위 30종목 전체로 확장하여 원 논문 재현도 향상.
2. 감성 피처 MA 윈도우를 90일 이상(180일·365일)으로 확장 탐색.
3. XGBoost 하이퍼파라미터 튜닝(Optuna 등)으로 추가 성능 개선.
4. LSTM / Transformer 계열 시계열 모델 적용 및 XGBoost와 비교.
5. 시가총액 비율을 월별·분기별 동적으로 계산하는 방식으로 개선.

**If I Had More Time**

- 뉴스 본문(body) 포함한 감성 분석 실험.
- 뉴스 발행 시간대(장중/장후) 기반 날짜 shift 로직 정교화 (원 논문 Table 1 방식 구현).
- Optuna 기반 하이퍼파라미터 자동 탐색.

---

## Project Structure

```
sentiment analysis/
├── kr_FinBERT.ipynb                  # 메인 실행 파일 (전체 파이프라인)
├── 강태영.pdf                         # 발표 슬라이드 (60 pages)
├── KR-FinBERT 뉴스 감성분석을 활용한 KOSPI 주가지수 예측 (1).pdf  # 원 논문
├── news_df.csv.zip                   # KR-FinBERT 감성 점수 부여 완료 뉴스 캐시 (zip)
└── data/
    ├── NewsResult_20140101-20141231.xlsx  ┐
    ├── NewsResult_20150101-20151231.xlsx  │  한경 뉴스 원본 (2014–2023, 연도별)
    ├── ...                                │
    ├── NewsResult_20230101-20231231.xlsx  ┘
    ├── data_5434_20241028.csv             ┐
    ├── data_5453_20241028.csv             │  KOSPI 종목 상장시가총액 데이터
    ├── data_5505_20241028.csv             │  (KRX 수집, 2024-10-28 기준)
    ├── data_5519_20241028.csv             │
    └── data_5530_20241028.csv             ┘
```

**실행 순서 (kr_FinBERT.ipynb)**

```
1. SetUp (pip install talib, finance-datareader, Google Drive mount)
2. Data 수집
   ├── 삼성전자 주가 (FinanceDataReader, 005930)
   ├── 한경 뉴스 xlsx 로드 (2014–2023)
   ├── KR-FinBERT 감성분석 → news_df.csv 캐시 저장
   ├── 삼성전자 시가총액 (yfinance, 005930.KS)
   └── KOSPI 상장시가총액 (data_5434~5530.csv)
3. 감성도·반응도 생성 및 주가 데이터와 merge
4. PreProcessing (결측치 ffill, Open==0 제거)
5. 피처 엔지니어링 (TA-Lib 10종 지표, 90일 이동평균)
6. 데이터 분할·스케일링 (MinMaxScaler, 80/20 시계열 split)
7. 모델 학습 (XGBoost, RandomForest)
8. 평가 및 시각화 (RMSE, R², 예측 vs 실제 그래프)
9. 비교군 실험 (감성 피처 제거 후 동일 모델 재학습·평가)
```

---

## PDF / Slides Mapping

- **Main slide deck**: `hrd_2024_2.pptx` (60 슬라이드, 발표자료 / `강태영.pdf`는 동일 내용 PDF 버전이나 파일 손상으로 텍스트 추출 불가)
- **Reference paper**: `KR-FinBERT 뉴스 감성분석을 활용한 KOSPI 주가지수 예측 (1).pdf` (2 pages, 한국통신학회 2023 동계종합학술발표회)

**Slide-to-README mapping (PPTX OCR 기반)**:

| README 섹션 | PPTX 슬라이드 | 원 논문 PDF |
|-------------|---------------|-------------|
| Problem statement | Slide 3–14 (서론, 관련 연구) | Page 1, 서론 (Ⅰ) |
| Method / Architecture (KR-FinBERT) | Slide 34 (추론 코드) | Page 1, 2.2 KR-FinBERT |
| Sentiment/Sensitive degree 수식 | Slide 36–38, 42 | Page 1–2, 2.3절 |
| Feature design | Slide 39 (피처 목록) | Page 1, 2.4절 |
| Experiment setup (scaler, split) | Slide 45–46 | — |
| Results / Comparison | Slide 50 (결과 표), 51–52 (그래프) | Page 2, Table 3 |
| Ablation (MA window) | Slide 50 | 코드 주석 |
| Design choice (OHLCV 제외 이유) | Slide 54–55 | — |
| Conclusion | Slide 53 | Page 2, Ⅲ 결론 |
| Limitations | Slide 56–57 | Page 2, Ⅲ 결론 |
| Data 구성 (BigKinds, 73,539건) | Slide 32–33 | Page 1, 2.1 Data |
| 상관계수 Table (Table 2) | — | Page 2 |
| Feature Importance (Fig. 1) | — | Page 2 |

**발표자료 PPTX (`hrd_2024_2.pptx`, 60 슬라이드) 매핑**:

| Slide | 내용 |
|-------|------|
| 1 | 표지 (이미지) |
| 2 | 목차 |
| 3 | 1. 서론 |
| 4–8 | AI → ML → DL 개념 소개, ML 기반 주가 예측 배경 |
| 9–14 | 관련 연구 논문 목록, 뉴스-주가 관계 문제 제기 |
| 15–18 | 데이터 수집 방법(BigKinds, 한경뉴스), Claude/NLP 도구 소개 |
| 19 | 2. 데이터 및 사전지식 |
| 20–23 | 빅카인즈 뉴스 수집 UI, Robots.txt 설명 |
| 24–30 | NLP 개념, BERT 설명, 감성분석(Sentiment Analysis) 개념 |
| 31 | 구분선(섹션 전환) |
| 32 | 프로젝트 제목 슬라이드 |
| 33 | 뉴스 DataFrame 구성 예시(2014–2023 헤드라인 적재) |
| 34 | KR-FinBERT 모델 로딩·추론 코드 |
| 35 | 감성 점수 수치화(+1/0/-1) 결과 표 |
| 36–38 | 감성도(Sentiment degree)·반응도(Sensitive degree) 수식 |
| 39 | 피처 목록: TRIX, ADX, BOP, ADXR, FASTK, FASTD, MFI, CMO, DX, MA_MACDHIST, MINUS_DM |
| 40 | 실험군(기술지표+감성) vs 대조군(이동지표만) 구조 |
| 41 | 최종 데이터셋 샘플(2023년 말 데이터 tail) |
| 42 | Sensitive_degree_ma 이동평균 수식 |
| 43–44 | XGBoost 개념(트리 앙상블), RandomForest 개념 |
| 45 | MinMaxScaler + TimeSeriesSplit 설명 |
| 46 | 학습 코드 (XGBoost + RandomForest) |
| 47–48 | RMSE·R² 평가 지표 설명 |
| 49 | (이미지) |
| 50 | **결과 표**: MA 30 → RMSE 9,655 / R² -1.6323, MA 90 → RMSE 8,711 / R² -1.1428, Baseline → 15,756 / R² -6.0102 |
| 51 | **예측 그래프 (감성지표 포함)**: Actual vs XGBoost/RF 2014–2024 |
| 52 | **예측 그래프 (감성지표 제거)**: Baseline 비교 — Test 구간 폭발적 진동 |
| 53 | **결론**: 기술 지표에 감성 지표를 추가하면 성능이 더 뛰어남 |
| 54 | **설계 결정**: 가격지표(OHLCV)는 예측에 매우 중요하나 지표 비교를 위해 의도적으로 제외 |
| 55 | **디자인 선택 근거**: 가격지표 포함 시 감성지표 중요도 심각 저하 → 이동지표만 사용 |
| 56–57 | **프로젝트 한계**: 대량 데이터 수집 불가, 세부 자료 미공개 → 완벽 구현 불가 |
| 58–59 | 마무리 (데이터 접근성의 중요성 강조) |
| 60 | 마지막 슬라이드 |

**Numbers provenance**:

| 수치 | 출처 |
|------|------|
| XGBoost RMSE 8,711.45 (with sentiment) | `kr_FinBERT.ipynb` Cell `#VSC-d2403cac` stdout 출력 |
| RandomForest RMSE 8,437.88 (with sentiment) | 동일 셀 |
| XGBoost RMSE 15,756.86 (without sentiment) | `kr_FinBERT.ipynb` Cell `#VSC-91482d7d` stdout 출력 |
| RandomForest RMSE 15,759.21 (without sentiment) | 동일 셀 |
| MA-window ablation 수치 (1·7·15·30·90일) | `kr_FinBERT.ipynb` Cell `#VSC-d2403cac` 코드 내 주석 |
| 원 논문 RMSE Table (Table 3) | 원 논문 PDF Page 2 |
| 원 논문 상관계수 Table (Table 2) | 원 논문 PDF Page 2 |

**Any missing slides / gaps**:
- Slide 1–2, 9–10, 14, 17–18, 20, 22–23, 26–28, 49, 58, 60: OCR 텍스트 추출 불가(이미지/다이어그램 전용 슬라이드). 관련 논문·뉴스 스크린샷, 개념 다이어그램으로 추정.
- 원 논문의 30종목 상관계수 Table 2 전체 및 Feature Importance(Fig. 1) 수치: 본 구현 노트북 출력에 없으며 원 논문 데이터로만 존재 → 본 구현 결과로 대체 불가.

---

## Citation & License

**구현한 원 논문**
```
장주현, 김재윤. (2023). "KR-FinBERT 뉴스 감성분석을 활용한 KOSPI 주가지수 예측."
2023년도 한국통신학회 동계종합학술발표회, pp. 1142–1143.
순천향대학교. (kwack0202@sch.ac.kr, kimym38@sch.ac.kr)
```

**사용 모델**
```
KR-FinBERT-SC: https://huggingface.co/snunlp/KR-FinBert-SC
```

- **License**: 추가 필요 (별도 라이선스 파일 없음)
- **Papers / Links**:
  - KR-FinBERT: https://huggingface.co/snunlp/KR-FinBert-SC
  - FinanceDataReader: https://github.com/FinanceData/FinanceDataReader
  - TA-Lib: https://ta-lib.org
