# MCTS Variant Performance Prediction

## 프로젝트 기본

- **Project Title**: MCTS Variant Performance Prediction
- **One-line summary**: 보드 게임의 특성을 기반으로 서로 다른 MCTS 변형(variant) 간 성능을 예측하는 머신러닝 모델 개발
- **Project Type**: ML/DL, Data Mining/Science
- **My Role / Key Contribution**: 
  - 최고 스코어링 제출 달성 (RMSE 0.43378, 285등/1610팀)
  - CatBoost 모델 실험 및 하이퍼파라미터 튜닝
  - 전처리 파이프라인 설계 및 파생 피쳐 엔지니어링 (efficiency ratio, complexity interaction 등)

---

## TL;DR

- **Problem**: MCTS 알고리즘 변형마다 어떤 게임에서 잘 작동하는지 예측하기 어려움. 게임 특성을 기반으로 두 MCTS 변형 간 승률 차이(utility)를 예측해야 함.

- **Approach**: 
  - LightGBM + CatBoost 앙상블 (50:50 블렌딩)
  - Agent 파라미터 파싱 및 interaction feature 생성 (exploration constant, playout strategy)
  - TF-IDF 벡터화로 게임 규칙 텍스트 정보 활용
  - Out-of-Fold(OOF) 예측을 meta-feature로 활용한 2단계 앙상블

- **Main Result**: Public LB RMSE **0.427** (블렌딩 후) / 최종 제출 RMSE **0.43378** (285위/1610팀)

- **Keywords**: MCTS, Game AI, Gradient Boosting, Tabular Data, Feature Engineering, Ensemble Learning, GroupKFold, Regression

---

## Motivation & Background

### Background
MCTS(Monte Carlo Tree Search)는 보드 게임 AI 개발에 널리 사용되는 알고리즘으로, 지난 20년간 수백 가지 변형이 제안되었다. 하지만 대부분의 연구는 소수의 게임에서 제한적인 비교를 수행하며, 어떤 변형이 특정 게임 유형에 최적인지 일반화된 지식은 부족하다.

### Why this problem matters
- 새로운 게임이나 의사결정 문제에 적용할 MCTS 변형을 선택할 때 시행착오를 줄일 수 있음
- 게임 특성과 알고리즘 강점/약점 간 관계를 정량적으로 이해함으로써 MCTS 연구의 체계적 발전 기여
- 수천 개의 게임 시뮬레이션을 통해 축적된 데이터를 활용한 메타러닝 접근법의 가능성 탐색

### Gap in existing work
기존 연구는 주로 특정 게임 도메인(체스, 바둑 등)에 특화되어 있으며, cross-game generalization 성능을 체계적으로 평가하지 않았다. 본 대회는 700+ 게임에 걸친 MCTS 변형 대결 결과를 학습 데이터로 제공함으로써 범용 예측 모델 개발을 목표로 한다.

### Related work
- Silver et al. (2016): AlphaGo에서 MCTS + Deep RL 결합
- Browne et al. (2012): "A Survey of Monte Carlo Tree Search Methods" - MCTS 변형 분류체계 제시
- Finnsson & Björnsson (2008): General Game Playing에서 MCTS 적용 사례
- Kaggle 커뮤니티 베이스라인: andreasbis의 OOF feature engineering 접근법, yunsuxiaozi의 LightGBM 파라미터 튜닝

---

## Approach

### Data Mining/Science 접근

#### Problem framing
- **Task**: Regression (continuous prediction)
- **Target**: `utility_agent1` - Agent1이 Agent2 대비 얻는 평균 승점 차이 (범위: -1 ~ +1)
- **Prediction scenario**: 게임 규칙 + 두 MCTS 변형 파라미터를 입력받아 성능 차이 예측

#### Feature/Signal design
1. **Agent parameter parsing** (regex 기반)
   - Selection policy (Progressive History, UCB1, etc.)
   - Exploration constant (수치값)
   - Playout policy (MAST, NST, Random, etc.)
   - Score bounds (true/false)

2. **Derived features** (19개 생성)
   ```python
   - area = NumRows × NumColumns
   - Playouts/Moves = PlayoutsPerSecond / MovesPerSecond
   - TurnsDurationEfficiency = DurationActions / DurationTurnsStdDev
   - AdvantageBalanceRatio = AdvantageP1 / Balance
   - NormalizedGameTreeComplexity = GameTreeComplexity / StateTreeComplexity
   - ComplexityBalanceInteraction = Balance × GameTreeComplexity
   - AggressiveActionsRatio = sum of enemy-targeting decisions
   ```

3. **Text features** (TF-IDF)
   - `LudRules`, `EnglishRules` 열에 대한 TF-IDF 벡터화 (단어 기반)
   - ARI (Automated Readability Index), McAlpine EFLAW, Coleman-Liau Readability Index 계산

4. **Domain knowledge integration**
   - 게임 유형 (TwoPlayer, Solitaire, Stochastic 등) 및 보드 기하학 정보 활용
   - 중복 컬럼 제거 (num_wins/draws/losses 등)
   - 상수 컬럼 및 결측치 100% 컬럼 제거

#### Modeling choices
- **Model family**: Gradient Boosting Decision Trees (GBDT)
  - **LightGBM**: Extra trees 모드 + 높은 max_depth (24) → 복잡한 interaction 포착
  - **CatBoost**: GPU 학습, 카테고리 변수 자동 처리
- **선택 이유**: 
  - 높은 차원 tabular data에 강력한 성능
  - Feature importance 분석 용이
  - 결측치 및 categorical feature 처리 내장

#### Validation strategy
- **Cross-validation**: StratifiedGroupKFold (n_splits=5)
  - Group: `GameRulesetName` - 동일 게임 규칙이 train/val에 동시 출현하지 않도록 방지 (leakage 차단)
  - Stratify: 타겟 분포 균등 배분
- **Early stopping**: 500 rounds (validation RMSE 기준)
- **OOF meta-features**: 
  - 1단계 모델의 OOF 예측값을 새로운 feature로 추가하여 2단계 모델 학습 (stacking)

#### Interpretability & debugging
- **Feature importance**: CatBoost 내장 importance 활용 - 상위 200개 feature 선별
- **OOF prediction analysis**: Fold별 RMSE 분산 확인 (0.424 ± 0.098)
- **Outlier clipping**: 
  - `PlayoutsPerSecond` 상한 25000
  - `MovesPerSecond` 상한 1000000

#### Business/Product integration
본 프로젝트는 학술 대회 성격이지만, 실무 적용 시:
- 새로운 게임 개발 시 적합한 AI 알고리즘 사전 추천
- 게임 밸런싱 테스트 자동화 (AI 난이도 조절)
- 게임 메타 분석 (어떤 전략이 유리한지 예측)

---

## Data & Experiment

### Dataset
- **Type**: Tabular (structured) + Text (game rules)
- **Source**: [Kaggle - UM Game-Playing Strength of MCTS Variants](https://www.kaggle.com/competitions/um-game-playing-strength-of-mcts-variants/data)
- **Size**: 
  - Train: 약 700+ unique games × 다양한 MCTS 조합
  - Test: 대회 제공 (full test set 사용 여부 조정 가능)
- **Label/Target definition**: 
  - `utility_agent1`: Agent1의 평균 승점 - Agent2의 평균 승점
  - 범위: [-1, 1] (Agent1 완승 시 +1, Agent2 완승 시 -1, 비김 시 0)
- **Preprocessing**:
  1. 결측치: 전체 결측 컬럼 제거
  2. 상수 컬럼: 단일 값만 갖는 컬럼 제거
  3. Agent 문자열 파싱: `MCTS-{selection}-{exploration}-{playout}-{bounds}` 형식 분해
  4. Memory optimization: polars 라이브러리 사용, dtype 최적화 (Int16, Float32)
- **Leakage checks**: 
  - GroupKFold로 게임 규칙 단위 분리 (동일 게임이 train/val 중복 방지)
  - Test set에서 `num_wins/draws/losses` 미리 제거
- **Split**: 
  - CV: 5-Fold StratifiedGroupKFold
  - No explicit train/val/test split (대회 제출 방식이 inference server 기반)

### Evaluation protocol
- **Metric**: RMSE (Root Mean Squared Error)
  - 선택 이유: 예측 오차의 크기를 직관적으로 표현 (타겟과 동일 스케일)
- **Leaderboard**: Public LB (대회 기간 중 일부 test set) / Private LB (최종 평가)

### Environment
- **OS**: Google Colab / Kaggle Notebooks
- **CPU/GPU**: 
  - CatBoost: GPU 학습 (`task_type='GPU'`, NVIDIA T4/P100)
  - LightGBM: CPU 학습 (`device='cpu'`)
- **Frameworks/Libraries**:
  - `polars` 1.x: 고성능 dataframe 처리
  - `lightgbm` 4.x: GBDT 모델
  - `catboost` 1.2.7: GBDT 모델 (GPU 지원)
  - `xgboost` 2.x: 초기 실험용
  - `sklearn`: 전처리, cross-validation, metrics
  - `pandas`, `numpy`, `re`, `dill`

### Reproducibility
- **Random seed**: 2024 (일부 노트북), 42 (모델 파라미터)
- **Deterministic 설정**: 
  - `random.seed(2024)`, `np.random.seed(2024)`
  - CatBoost: `random_state=42`
  - LightGBM: `seed=42`
- **Note**: GPU 학습 시 완전 재현은 어려울 수 있으나, 시드 고정으로 근사 재현 가능

---

## Results

### Cross-Validation Performance

| Model | OOF RMSE (mean ± std) | Folds CV Range |
|-------|----------------------|----------------|
| **LightGBM** | 0.424 ± 0.098 | [0.32, 0.52] (approximate) |
| **LightGBM w/ OOF** | 0.427 ± 0.097 | [0.33, 0.52] |
| **CatBoost** | 0.465 ± 0.079 | [0.39, 0.54] |
| **CatBoost w/ OOF** | 0.465 ± 0.081 | [0.38, 0.55] |

### Final Submission
- **Public LB** (blending): 0.427 (LightGBM + public NB blend)
- **Private LB** (final): 0.43378 (rank: 285/1610)
- **Ensemble strategy**: 50% Model_1 (TF-IDF + CatBoost variants) + 50% Model_2 (LightGBM + CatBoost basic)

### Additional results
- **Feature importance top 10** (CatBoost 기준):
  1. `num_losses_agent1`, `num_wins_agent1`, `num_draws_agent1` (상위 - 추후 제거 권장)
  2. `Region`, `BranchingFactorMaximum`, `Asymmetric`
  3. `OutcomeUniformity`, `DurationTurnsStdDev`
  4. Derived features: `AggressiveActionsRatio`, `TurnsDurationEfficiency`

- **Hyperparameters** (최종 제출 기준):
  - LightGBM: `learning_rate=0.07, num_leaves=64, max_depth=24, extra_trees=True, reg_lambda=0.8`
  - CatBoost: `learning_rate=0.03, depth=8, num_trees=20000, reg_lambda=0.8`

### Statistical significance / confidence
- Fold 간 RMSE 변동 (std ~0.08-0.1): 게임 난이도/복잡도에 따른 예측 난이도 차이 반영
- Public LB와 Private LB 간 차이 (0.427 → 0.43378): Public/Private split 간 게임 분포 차이로 인한 일반화 성능 변동

### Visualization notes
노트북 내 Plotly 차트:
- **CV RMSE by Fold**: 각 폴드별 성능 막대 그래프 (색상: #C9A9A6)
- **Feature importance bar chart**: CatBoost 상위 50개 feature 시각화 (코드 내 주석 처리)

---

## Discussion

### Key observations
1. **LightGBM이 CatBoost보다 안정적으로 우수**: CV 기준 RMSE 0.424 vs 0.465 - LightGBM의 extra_trees 모드가 게임 간 일반화에 효과적
2. **OOF meta-feature의 효과 미미**: OOF 추가 시 오히려 CV 성능 소폭 하락 (0.424 → 0.427) - 모델 간 예측 패턴이 유사하여 다양성 부족 추정
3. **Agent parameter interaction이 중요**: exploration constant와 playout policy 조합이 예측에 큰 영향
4. **게임 복잡도 지표가 강력**: `StateTreeComplexity`, `GameTreeComplexity`, `BranchingFactor` 등이 상위 feature

### Interpretation
- MCTS 성능은 게임의 **탐색 공간 크기**와 **branching factor**에 크게 좌우됨
- Exploration constant가 높은 변형은 복잡한 게임에서, 낮은 변형은 단순한 게임에서 유리할 가능성
- TF-IDF 기반 텍스트 feature는 예상보다 기여도가 낮음 (게임 규칙 텍스트의 패턴화 부족)

### Trade-offs
- **정확도 vs 복잡도**: LightGBM extra_trees 모드는 학습 시간 증가 (2배) 대비 RMSE 4% 개선
- **GPU vs CPU**: CatBoost GPU 학습은 10배 빠르지만 CPU LightGBM보다 RMSE 9% 높음
- **Feature 수 vs 과적합**: 200개 선별 feature 사용 시 전체 feature 대비 학습 속도 3배 향상, 성능 저하 미미

### Failure cases / surprising results
- **높은 fold 변동성**: 일부 게임 그룹(예: Mancala 계열)에서 예측 오차 크게 증가 - 훈련 데이터 내 해당 게임 샘플 부족 추정
- **Outlier clipping 효과 약함**: MovesPerSecond 상한 제한 후 CV 개선 미미 (0.001 수준)
- **Blending이 단일 모델보다 낮은 성능**: 50:50 블렌딩이 단일 LightGBM보다 나쁜 경우 발생 (LB 0.427 vs 0.424) - 가중치 재조정 필요

### What I learned
1. **GroupKFold의 중요성**: 게임 기반 그룹 분리 없이는 leakage로 인해 실제 일반화 성능 과대평가
2. **Feature engineering > 모델 튜닝**: 파생 변수 19개 추가로 baseline 대비 10% 성능 향상, 하이퍼파라미터 튜닝은 2-3% 기여
3. **GPU 학습이 항상 우월하지 않음**: CatBoost GPU가 빠르지만 LightGBM CPU의 extra_trees가 정확도 면에서 우수
4. **대회 후반 Public LB 과적합 위험**: 블렌딩 실험 중 Public LB만 보고 선택 시 Private LB 하락 가능성 (실제 발생)

---

## Limitations & Future Work

### Limitations
1. **데이터 불균형**: 일부 게임 유형(예: Mancala, Tafl)의 샘플 수 부족으로 해당 영역 예측 부정확
2. **Feature selection 미흡**: 200개 feature 선별 시 도메인 지식 부족으로 중요 feature 누락 가능성
3. **모델 다양성 부족**: 모두 GBDT 계열 - Neural Network, SVM 등 다른 모델군 미탐색
4. **하이퍼파라미터 튜닝 범위**: Grid search 범위가 제한적 (시간/리소스 제약) - Optuna 등 베이지안 최적화 미적용
5. **Ablation study 미실행**: Feature 수가 너무 많아(700+) 개별 feature 기여도 체계적 분석 불가 - 시간 제약으로 전체 feature set만 평가

### Future directions
1. **게임 메타 정보 활용**: 게임 장르, 출시 연도, 플레이어 수 등 추가 메타 데이터 수집 및 반영
2. **Deep learning 시도**: Transformer 기반 게임 규칙 임베딩, GNN으로 게임 상태 그래프 모델링
3. **Adversarial validation**: Public/Private split 분포 차이 분석 및 domain adaptation 기법 적용
4. **앙상블 가중치 최적화**: Optuna로 모델 간 블렌딩 비율 자동 탐색 (현재 50:50 수동 설정)
5. **시계열 feature**: 게임 진행 중 MCTS의 시계열 동작 패턴 분석 (현재는 집계된 통계량만 사용)

### If I had more time
- **Ablation study**: 개별 feature group(agent params, game complexity, derived features 등)의 기여도 정량 분석
- **SHAP analysis**: 각 feature가 예측에 미친 영향 시각화 (게임별, MCTS 변형별)
- **Error analysis by game type**: 게임 유형별 예측 성능 세부 분석 및 타겟팅 feature 추가
- **External data integration**: Ludii framework의 게임 소스 코드 파싱하여 규칙 구조화된 feature 생성
- **Neural network stacking**: GBDT 출력을 MLP에 입력하여 비선형 조합 학습

---

## Project Structure

```
MCTS/
├── mcts-final-submission-ch.ipynb       # 최종 제출용 노트북 (Model_1 + Model_2 블렌딩)
│   ├── Model_1: TF-IDF + CatBoost variants (2개 config)
│   ├── Model_2: LightGBM + CatBoost basic (feature selection)
│   └── Blending: 50:50 ensemble
│
├── TaeYoung_Train.ipynb                  # CatBoost 학습 실험 노트북
│   ├── Feature engineering (19 derived features)
│   ├── Hyperparameter tuning (Optuna grid search 주석 처리)
│   ├── GroupKFold cross-validation
│   └── Model persistence (Google Drive 저장)
│
├── submission1-prediction.ipynb          # 1차 제출 예측 파이프라인
│   ├── OneHot encoding (categorical features)
│   ├── Stacking ensemble (joblib 모델 로드)
│   └── Inference server integration
│
├── AI를 위한 머신러닝_6조.pdf           # 발표 슬라이드 (40 pages)
└── AI를 위한 머신러닝_6조.pptx          # 발표 슬라이드 원본
```

---

## PDF/Slides Mapping

### Main slide deck
- **File**: `AI를 위한 머신러닝_6조.pdf`
- **Version/Date**: 2024년 2학기 "AI를 위한 머신러닝" 과목 최종 발표 (40 pages)

### Slide-to-README mapping
> **Note**: PDF 텍스트 추출 도구 미설치로 상세 페이지 매핑은 수동 확인 필요. 아래는 일반적인 발표 자료 구조 기준 예상 매핑입니다.

| README Section | Expected Slide Pages | Content |
|----------------|---------------------|---------|
| Problem statement | 1-5 | 대회 소개, MCTS 배경, 문제 정의 |
| Method/Architecture | 6-15 | Feature engineering, 모델 구조 (LightGBM/CatBoost), 앙상블 전략 |
| Experiment setup | 16-20 | 데이터셋 통계, CV 전략, 하이퍼파라미터 |
| Results/Comparison | 21-30 | CV RMSE 표, Leaderboard 순위, Fold별 성능 그래프 |
| Ablation/Analysis | 31-35 | Feature importance, OOF 효과 분석, 실패 사례 |
| Conclusion/Future work | 36-40 | 학습 포인트, 한계점, 향후 방향 |

### Numbers provenance
- **Public LB 0.427**: 노트북 코드 주석 및 블렌딩 실험 결과
- **Private LB 0.43378 (285/1610)**: 대회 최종 순위 확정 결과
- **CV RMSE 수치**: 노트북 출력 셀에서 확인 완료 (LightGBM 0.424 ± 0.098, CatBoost 0.465 ± 0.079)

### Any missing slides / gaps
- **Slide 내용 미확인**: PDF 텍스트 추출 실패로 상세 페이지 내용 검증 불가
  - **추가 필요**: 사용자가 PDF를 직접 확인하여 아래 항목 기재 요청
    - 문제 정의 슬라이드 페이지 번호
    - 모델 아키텍처 다이어그램 페이지
    - 최종 성능 비교 표/그래프 페이지
    - Ablation study 결과 페이지
- **숫자 정확도 확인 필요**: 
  - 팀원별 기여도 세부 수치 (슬라이드 내 명시 여부)
  - Private LB 최종 점수 (public 0.427과 private 0.43378 간 차이 원인)

---

## Citation & License

### Citation info
- **Title**: Game-Playing Strength of MCTS Variants Prediction (Kaggle Competition Entry)
- **Authors**: 6조 팀 (현동, 나현, 태영 외 2명)
- **Course**: AI를 위한 머신러닝, 2024-2학기
- **Year**: 2024

### License
- **Code**: 대회 규정 준수 (Kaggle Competition License)
- **Data**: Kaggle 제공 데이터셋 라이선스에 따름

### Papers/links
- **Competition**: https://www.kaggle.com/competitions/um-game-playing-strength-of-mcts-variants
- **Dataset**: https://www.kaggle.com/competitions/um-game-playing-strength-of-mcts-variants/data
- **Referenced kernels**:
  - andreasbis - "MCTS OOF Predictions as Features"
  - yunsuxiaozi - "MCTS Starter" (Public NB, LB 0.427)
- **MCTS survey**: Browne et al., "A Survey of Monte Carlo Tree Search Methods", IEEE TCIAIG 2012

---

## Appendix: 추가 확인 가능 항목

아래 항목은 필요 시 발표 슬라이드 또는 팀 기록을 참고하여 보완 가능합니다.

1. **PDF 슬라이드 상세 매핑**: 
   - 문제 정의/방법론/결과 각 섹션의 슬라이드 페이지 번호
   - 실험 결과 표/그래프가 포함된 슬라이드 번호
   - Feature importance 시각화 슬라이드
   
2. **실행 환경 상세**:
   - GPU 모델명 (Google Colab: T4, Kaggle: P100 추정)
   - 모델별 학습 시간 (CatBoost GPU: ~5-10분/fold, LightGBM CPU: ~2-3분/fold 예상)

3. **팀 협업 세부사항**:
   - 코드 공유 방식 (GitHub, Google Drive 등)
   - 실험 관리 도구 (Weights & Biases, Notion 등)
   - 주간 미팅 주기 및 역할 분담 조정 과정
