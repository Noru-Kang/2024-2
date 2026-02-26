# Hotel Reservation — Room Type Prediction

---

## [프로젝트 기본]

- **Project Title:** Hotel Reservation — Room Type Prediction
- **One-line summary:** 캐글 호텔 예약 데이터를 활용해 고객이 예약한 객실 유형(room_type_reserved)을 예측하는 다중 분류 ML 템플릿 노트북
- **Project Type:** ML (Multi-class Classification) / Data Mining
- **My Role / Key Contribution:**
  - 전체 ML 파이프라인(전처리 → 다중 모델 학습 → 하이퍼파라미터 탐색 → 체크포인트 저장) 코드 직접 작성
  - 비전공자도 파라미터 변경만으로 재사용 가능하도록 템플릿화 (변경 지점 주석 `# 변경바람` 명시)
  - 12종 sklearn/XGBoost/LightGBM/CatBoost 모델을 단일 루프로 통합 평가하는 자동화 구조 설계
  - DL(PyTorch) 섹션 자리 마련 (미구현 — 향후 확장 예정)
  - EDA 노트북 작성: 이상치 탐지(도메인 기반 판단), 통계 검증(ANOVA·Cramér's V·Point-Biserial), 다중공선성 분석(VIF) 수행

---

## [TL;DR]

- **Problem:** 호텔 예약 데이터(36,275건)에서 고객이 예약한 객실 유형(`room_type_reserved`)을 예측하는 다중 분류 문제
- **Approach:** Label Encoding → KNN Imputation(avg_price_per_room의 0값 처리) → RobustScaler → StratifiedKFold + RandomizedSearchCV 기반 12종 ML 모델 자동 탐색 및 체크포인트 저장
- **Main Result:** RandomForestClassifier 5 epoch 시점 Accuracy 0.9249, Weighted F1 0.9205 (학습 중단 시점 기준 최고치; 전체 모델 최종 비교 결과는 추가 필요)
- **Keywords:** `hotel-reservation`, `room-type-classification`, `multi-class`, `random-forest`, `xgboost`, `lightgbm`, `catboost`, `EDA`, `statistical-validation`, `template-notebook`

---

## [Motivation & Background]

- **Background:** Kaggle에 공개된 호텔 예약 데이터셋을 활용한 개인 학습용 프로젝트. 예약 정보(투숙 인원, 리드 타임, 특별 요청 수 등)로부터 고객이 선택한 객실 유형을 예측한다.
- **Why this problem matters:** 객실 유형 예측은 호텔 재고 관리·가격 최적화와 직결되며, 다양한 ML 알고리즘의 비교 실험을 통해 성능 기준선(baseline)을 확보하는 학습 목적도 겸한다.
- **Gap in existing work:** 단일 모델 학습에 그치는 기존 Kaggle 노트북과 달리, (1) EDA에서 도메인 기반 이상치 판단 및 통계적 피처 유의성 검증(ANOVA, Cramér's V, Point-Biserial)을 선행하고, (2) 12종 모델을 동일 조건(RandomizedSearchCV + StratifiedKFold)으로 자동 비교하며, (3) 체크포인트를 에폭별로 저장하는 구조를 갖춘다.
- **Related work:** Kaggle "Hotel Reservations Classification Dataset" 공개 노트북 참고 (링크 추가 필요). sklearn 공식 문서, XGBoost/LightGBM/CatBoost 공식 문서 기반 구현.

---

## [Approach]

### ML/DL 블록

- **Model/Architecture:**
  12종 분류 모델을 단일 리스트(`ML`)로 관리하며 동일 전처리 결과물에 순차 적용:

  | 범주 | 모델 |
  |------|------|
  | Ensemble | RandomForestClassifier, AdaBoostClassifier, BaggingClassifier, GradientBoostingClassifier |
  | GLM | LogisticRegression |
  | Tree | DecisionTreeClassifier |
  | Naive Bayes | GaussianNB |
  | KNN | KNeighborsClassifier |
  | SVM | SVC |
  | Boosting | XGBClassifier, LGBMClassifier, CatBoostClassifier |

  - 입력: 17개 피처 (인코딩 + 대치 + 스케일링 완료된 float64)
  - 출력: `room_type_reserved` 클래스 레이블 (다중 클래스)

- **Loss & Optimization:** RandomizedSearchCV (scoring=`accuracy`, n_iter=10, cv=StratifiedKFold(5)). 모델 내부 손실은 각 알고리즘 기본값 사용.

- **Training strategy / key mechanisms:**
  - 에폭 루프(1~10) × RandomizedSearchCV 반복: 매 에폭마다 다른 random_state(42+epoch)로 새로운 하이퍼파라미터 조합 탐색
  - 에폭별 최고 Accuracy/F1 모델을 `checkpoints/{ModelName}/{ModelName}_epoch_{N}.pkl`로 joblib 저장
  - 전체 모델 중 최종 최고 모델 선정 후 StratifiedKFold 교차 검증 출력

- **Inference/Serving path:** `joblib.load(checkpoint_path)` → `best_model.predict(x_test)`

- **Ablation/Design choices:**
  - 이상치 제거(IQR, Z-score) 코드 구현되어 있으나 "데이터 손실이 너무 많음" 이유로 주석 처리
  - Scaler 후보: StandardScaler, MinMaxScaler, RobustScaler → RobustScaler 선택 (이상치에 덜 민감)
  - Imputer 후보: KNNImputer, IterativeImputer → KNNImputer 선택
  - DL(PyTorch) 섹션은 임포트·구조체만 존재, 미구현

### Algorithm/Statistics 블록
해당 없음

### Data Mining/Science 블록
- **Problem framing:** 다중 클래스 분류 (객실 유형 예측)
- **Validation strategy:** StratifiedKFold(n_splits=5) + RandomizedSearchCV. 클래스 불균형을 고려한 층화 분할 사용.
- **Interpretability & debugging:** 주석 처리된 EDA 시각화 코드(히스토그램/막대 차트) 포함; 현재는 비활성화.

### System/Pipeline 블록
해당 없음

---

## [Data & Experiment]

- **Dataset type:** 정형 데이터 (Tabular)
- **Source:** Kaggle — Hotel Reservations Classification Dataset ([링크 추가 필요: https://www.kaggle.com/datasets/...])
- **Size:** 36,275 samples × 19 columns (Booking_ID 포함); 학습 후 x_train 29,020건 확인
- **Label/Target definition:** `room_type_reserved` — 고객이 예약한 객실 유형 (다중 카테고리; 정확한 클래스 수는 추가 필요)

  > ⚠️ **데이터 누수 주의:** `booking_status`(예약 취소 여부)가 피처로 포함되어 있음. 예약 취소 여부가 객실 유형 선택에 종속적일 수 있어 실제 배포 환경에서는 제거 검토 필요.

- **Preprocessing:**

  **EDA 노트북에서 수행 (도메인 기반 이상치 판단)**

  | 단계 | 방법 | 대상 | 판단 근거 |
  |------|------|------|----------|
  | 이상치 제거 | 조건부 행 삭제 | `no_of_children > 5` → 제거 | 동일 방 10명+ 비현실적 |
  | 이상치 제거 | 조건부 행 삭제 | `no_of_previous_cancellations > 12` → 제거 | ID 제외 모든 컬럼 동일(중복 의심) |
  | 이상치 제거 | 조건부 행 삭제 | `avg_price_per_room >= 500` → 제거 | 박스플롯 확인 후 상한 초과 |
  | 0값 유지 | 제거 없음 | `avg_price_per_room == 0` | complementary/online 할인으로 간주 |
  | 피처 엔지니어링 | 파생변수 생성 | `total_guests = no_of_adults + no_of_children` | — |
  | 피처 엔지니어링 | 파생변수 생성 | `total_stay = no_of_weekend_nights + no_of_week_nights` | — |

  **ML 템플릿 노트북에서 수행 (전처리 파이프라인)**

  | 단계 | 방법 | 대상 |
  |------|------|------|
  | Feature Selection | 수동 선택 | 18개 컬럼 (Booking_ID 제외) |
  | Encoding | LabelEncoder | type_of_meal_plan, room_type_reserved, market_segment_type, booking_status |
  | Imputation | KNNImputer | avg_price_per_room (0 → NaN 처리 후 대치, ML 파이프라인 한정) |
  | Outlier Removal | **비활성화** (IQR/Z-score 코드 주석 처리) | EDA 노트북에서는 도메인 기반 제거 수행 |
  | Scaling | RobustScaler | 전체 피처 |

- **Leakage checks:**
  - `booking_status_encode`가 피처에 포함됨 — 예약 취소 여부가 객실 유형 선택에 종속적일 수 있어 실 배포 시 제거 검토 필요
  - VIF 분석 결과 `arrival_year=35.1`, `avg_price_per_room=14.8`, `arrival_month=7.2` 로 높은 다중공선성 확인 (총 파생변수 `total_guests`, `total_stay`도 inf — 원 피처와 선형 종속)
  - 시간 기반 랜덤 분할에 의한 잠재적 누수 가능성 있음
- **Split:** Train 80% / Test 20% (`test_size=0.2, random_state=42`) → Train 29,020건 / Test 7,255건(추산)
- **Evaluation protocol:** StratifiedKFold(n_splits=5, shuffle=True, random_state=42) + 홀드아웃 Test set 평가
- **Metrics:** Accuracy, Weighted F1-Score (다중 클래스 대응을 위해 weighted 사용)
- **Environment:** Google Colab (GPU — CUDA, XGBClassifier에 `tree_method='gpu_hist'` 명시)
- **Frameworks/Libraries:**

  ```
  pandas, numpy, matplotlib, seaborn, scipy
  scikit-learn (impute, preprocessing, model_selection, ensemble, linear_model, tree, naive_bayes, neighbors, svm, neural_network, metrics)
  xgboost, lightgbm, catboost
  torch, torch.nn, torch.optim (임포트만, DL 미구현)
  joblib, tqdm
  ```

- **Reproducibility:** `random.seed(42)`, `np.random.seed(42)`, `torch.manual_seed(42)`, `torch.cuda.manual_seed_all(42)`, `torch.backends.cudnn.deterministic=True`, `torch.backends.cudnn.benchmark=False` (`Config.set_seed(42)`)

---

## [Results]

> 학습이 RandomForestClassifier 5 epoch 시점에서 중단되어, 전체 12종 모델의 최종 비교 결과는 수집되지 않았습니다.

**RandomForestClassifier (부분 결과 — 10 epoch 중 5 epoch)**

| Epoch | Accuracy | Weighted F1 |
|-------|----------|-------------|
| 1 | 0.9227 | 0.9183 |
| 2 | 0.9223 | 0.9173 |
| 3 | 0.9225 | 0.9176 |
| 4 | 0.9242 | 0.9199 |
| 5 | 0.9249 | 0.9205 |
| 6~10 | 추가 필요 | 추가 필요 |

- **Baseline method:** 추가 필요 (노트북에 dummy/baseline 비교 없음)
- **Best observed so far:** RandomForestClassifier, Epoch 5, Accuracy **0.9249**, Weighted F1 **0.9205**
- **Additional results:** AdaBoost, GradientBoosting, XGBoost, LightGBM, CatBoost 등 나머지 11종 모델 결과 추가 필요
- **Statistical significance / confidence:** K-Fold 최종 교차 검증 결과 추가 필요 (학습 중단으로 미출력)
- **Visualization notes:** `model_graph (1).png` 존재 — 추가 필요 (파일 내용 미확인)

---

## [EDA Key Findings]

### 이상치 탐지
- `no_of_children > 5`: 3개 행만 존재, 방 1개에 10명+ 비현실적 → 제거
- `no_of_previous_cancellations > 12`: ID 제외 모든 컬럼이 완벽 동일 → 중복/이상치로 판정 제거
- `avg_price_per_room >= 500`: 박스플롯에서 극단값 확인 → 제거
- `avg_price_per_room == 0` (489건): complementary(제휴) 및 online 채널에서 다수 발생 → 할인으로 간주, 유지
- 주말+평일 숙박 모두 0인 케이스(당일 대실) 및 lead_time=0(당일 예약)은 이상치 아님으로 판단

### 분포 관찰
- 재방문 고객(repeated_guest=1) 비율이 압도적으로 낮음 → 신규 고객 유지 vs 재방문 유도 전략 필요
- Online 채널이 예약 수 1위; Corporate 채널은 **재방문율 최고**이나 동시에 **이전 취소율도 최고**
- lead_time이 증가할수록 Not_Canceled 비율이 감소 (장기 사전 예약일수록 취소율 높음)

### 통계 검증 결과

**Point-Biserial Correlation (room_type_reserved vs 연속형)**

| 변수 | r | p-value | 유의성 |
|------|---|---------|--------|
| avg_price_per_room | 0.41 | < 0.0001 | ✓ 유의 |
| lead_time | -0.09 | < 0.0001 | ✓ 유의 |
| arrival_month | -0.00 | 0.4227 | ✗ 비유의 |

**ANOVA (room_type_reserved 그룹별 연속형 변수 차이)**

| 연속형 변수 | F-통계량 | p-값 | 유의성 |
|------------|---------|------|--------|
| avg_price_per_room | 2031.93 | ≈ 0 | ✓ 매우 유의 |
| lead_time | 77.34 | 2.0×10⁻⁹⁶ | ✓ 유의 |
| arrival_month | 4.69 | 8.8×10⁻⁵ | ✓ 유의 |

**Cramér's V (room_type_reserved vs 범주형/이산형)**

| 변수 | Cramér's V | 해석 |
|------|-----------|------|
| no_of_children | **0.47** | 상관성 가장 강함 |
| no_of_adults | 0.33 | 중간 |
| no_of_special_requests | 0.08 | 약함 |
| no_of_previous_bookings_not_canceled | 0.06 | 약함 |
| no_of_previous_cancellations | 0.06 | 약함 |
| no_of_week_nights | 0.06 | 약함 |
| no_of_weekend_nights | 0.03 | 가장 약함 |

**다중공선성 (VIF)**

| 주요 변수 | VIF |
|----------|-----|
| arrival_year | **35.1** (높음) |
| avg_price_per_room | 14.8 |
| arrival_month | 7.2 |
| arrival_date | 4.2 |
| market_segment_type | 3.5 |
| lead_time | 3.0 |
| total_guests, total_stay | inf (원 피처와 선형 종속) |
| type_of_meal_plan | 1.4 (낮음) |

---

## [Discussion]

- **Key observations:**
  1. RandomForestClassifier는 5 epoch만에 Accuracy 0.9249에 도달 — 트리 앙상블 계열이 이 데이터셋에 강한 경향
  2. **avg_price_per_room**이 room_type과 가장 강한 상관성 보유 (r=0.41, F=2031) — 가격이 객실 유형을 결정하는 핵심 피처
  3. **no_of_children**이 Cramér's V 0.47로 범주형 피처 중 최강 — 자녀 수에 따른 객실 선택 패턴 명확
  4. Corporate 채널이 재방문율·취소율 모두 가장 높음 — 출장 패턴에 의한 행동 특성 반영
  5. arrival_year VIF=35로 다중공선성 심각 — arrival_month, arrival_date와 강한 선형 관계

- **Interpretation:** 객실 유형은 가격(`avg_price_per_room`)과 투숙 인원(`no_of_children`, `no_of_adults`)에 의해 주도적으로 결정된다. 트리 기반 모델은 이러한 비선형적 분기를 자연스럽게 학습함으로써 높은 정확도를 달성한 것으로 해석된다.
- **Trade-offs:** RandomizedSearchCV 10 epoch × 12 모델은 탐색 시간이 매우 길어 실용적으로는 epoch 범위 축소 또는 Optuna 등 효율적 탐색 알고리즘으로 교체 고려 필요.
- **Failure cases / surprising results:** IQR/Z-score 기반 일괄 이상치 제거는 데이터 손실 과다로 비활성화 — EDA에서 도메인 기반 판단으로 대체함.
- **What I learned:**
  1. 통계 검증(ANOVA, Cramér's V, Point-Biserial)을 활용한 피처 유의성 사전 검증
  2. 다중공선성 분석(VIF)으로 피처 중복성 파악
  3. 여러 ML 모델을 단일 파이프라인으로 통합 평가하는 템플릿 구조의 설계
  4. 결측치를 단순 제거 대신 KNN 대치로 처리하는 실무적 접근

---

## [Limitations & Future Work]

- **Limitations:**
  1. DL(PyTorch) 섹션 미구현 — 임포트와 `Config` 클래스만 존재
  2. 전체 12종 모델 학습이 완료되지 않아 최종 모델 비교 불가
  3. `booking_status` 피처 포함으로 인한 잠재적 데이터 누수
  4. EDA와 ML 템플릿 노트북의 전처리 파이프라인 불일치 (EDA에서는 도메인 이상치 제거 수행, ML 노트북에서는 미반영)
  5. arrival_year VIF=35 — 다중공선성 심각하나 피처 제거 전략 미적용
  6. `강강술래.pdf` 발표자료 내용이 노트북과 어느 범위까지 대응하는지 명시 필요

- **Future directions:**
  1. PyTorch 기반 MLP/TabNet 등 DL 모델 구현으로 ML 대비 성능 비교
  2. `booking_status` 제거 후 성능 변화 실험 (누수 검증)
  3. Optuna 또는 Bayesian Optimization으로 하이퍼파라미터 탐색 효율화
  4. SHAP/LIME 기반 피처 중요도 해석 추가 (특히 avg_price_per_room, no_of_children 중요도 정량화)
  5. arrival_year 제거 + arrival_month/date만 유지해 다중공선성 해소 후 성능 비교
  6. EDA 노트북의 도메인 이상치 제거를 ML 파이프라인에 통합

- **If I had more time:** 전체 모델 학습 완료 후 최종 리더보드 구성, EDA 시각화 복원, DL 섹션 구현

---

## [Project Structure]

```
Hotel_reservation/
├── Temp_Hotel_Reservation.ipynb          # ML 파이프라인 템플릿 노트북 (모델링 엔트리포인트)
├── 토이프로젝트_EDA_ipynb의_사본.ipynb   # EDA 전용 노트북 (이상치 탐지 + 통계 검증)
├── 강강술래.pdf                           # 발표자료 (42 pages, 이미지 기반 스캔본)
├── data_dictionary (1).xlsx              # 피처 명세 문서 (컬럼명/타입/설명)
├── data-20250111T055859Z-001.zip         # 원본 데이터 압축파일 (Hotel_Reservations.csv 포함)
└── model_graph (1).png                   # 모델 구조/그래프 이미지 (추가 필요: 내용 미확인)
```

**실행 환경 전제:** Google Colab + Google Drive 마운트

**변경 필요 항목 (비전공자 가이드):**
```python
os.chdir('/content/drive/MyDrive/toy_project')  # ← 본인 Google Drive 경로로 변경
config.set_path("./data/")                       # ← 데이터 폴더 경로로 변경
imputer = ls_imputer[0]   # 0=KNNImputer / 1=IterativeImputer
scaler = ls_scaler[2]     # 0=Standard / 1=MinMax / 2=Robust
kfold = ls_kfold[1]       # 0=KFold / 1=StratifiedKFold
```

---

## [PDF/Slides Mapping]

- **Main slide deck:** `강강술래.pdf` — 42 pages, 이미지 기반 스캔본 (텍스트 추출 불가)

> ⚠️ PDF가 이미지 기반(스캔본)으로 텍스트 추출이 불가하여 아래 매핑은 **추가 필요** 항목으로 처리됩니다.
> 발표자료를 직접 확인하여 해당 슬라이드 번호를 채워 주세요.

- **Slide-to-README mapping:**
  - Problem statement slide(s): 추가 필요
  - Method/Architecture slide(s): 추가 필요
  - Experiment setup slide(s): 추가 필요
  - Results/Comparison slide(s): 추가 필요
  - Ablation/Analysis slide(s): 추가 필요
  - Conclusion/Future work slide(s): 추가 필요

- **Numbers provenance:** 추가 필요 (PDF 텍스트 추출 불가)
- **Any missing slides / gaps:** PDF 내용 수동 확인 필요 — 총 42 pages

---

## [Citation & License]

- **Citation info:**
  - Dataset: "Hotel Reservations Classification Dataset", Kaggle (출처 링크 추가 필요)
- **License:** 추가 필요
- **Papers/links:**
  - Kaggle Dataset: 추가 필요 (https://www.kaggle.com/datasets/ ...)
  - scikit-learn documentation: https://scikit-learn.org
  - XGBoost: https://xgboost.readthedocs.io
  - LightGBM: https://lightgbm.readthedocs.io
  - CatBoost: https://catboost.ai
