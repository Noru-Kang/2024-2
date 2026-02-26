# 수도권 쓰레기 매립지 최적 위치 선정

> **2024 응용통계학과 데이터 분석 공모전** | Team 쓸애기들 | **장려상 (3위)**

---

## 프로젝트 기본

| 항목 | 내용 |
|---|---|
| **Project Title** | 수도권 쓰레기 매립지 문제 해결을 위한 최적 위치 선정 |
| **One-line Summary** | 2025년 종료 예정인 수도권 쓰레기 매립지를 대체할 후보지를 QGIS 공간분석 + MCDA(TOPSIS)로 정량적·객관적으로 선정한다. |
| **Project Type** | Algorithm / Statistics (공간 데이터 분석 + 다기준 의사결정 분석) |
| **My Role** | geo 데이터 전처리(geopandas), PCA 기반 스코어링, 클러스터링 연구(K-Means·Medoid·X-Means, 최종 미채택), 작업 환경 구축 및 코드 총괄 |

---

## TL;DR

- **Problem**: 1992년부터 운영된 수도권 쓰레기 매립지(인천 서구·김포시)가 2025년 종료 예정이나, 3차 공모까지 진행했음에도 어떤 자치단체도 자발적으로 유치에 나서지 않아 대체지 선정이 시급함.
- **Approach**: QGIS로 법적 제한 구역을 필터링(98개 감소) → Python으로 PCA 기반 스코어링(→20개) → TOPSIS 다기준 평가 + 민감도 분석으로 최종 후보지 확정.
- **Main Result**: **화성시 우정읍**이 모든 가중치 변화 시나리오에서 1위(Rank Range = 0, Performance Score 0.7646)로 최적 입지로 선정됨.
- **Keywords**: `QGIS`, `MCDA`, `TOPSIS`, `PCA`, `geopandas`, `공간분석`, `매립지 입지선정`, `민감도 분석`

---

## Motivation & Background

### Background

서울·경기·인천 64개 자치구에서 발생하는 쓰레기가 집중되는 수도권 매립지는 1992년 개장 이후 전국 매립지의 3분의 1에 해당하는 쓰레기를 처리해왔다. 현재 수도권의 일평균 폐기물 발생량은 2019년 급증 이후 높은 수준을 유지하고 있으며, 매립지 운영 종료 시 수도권 전역의 폐기물 처리 체계가 붕괴될 위험이 있다. (출처: KBS "버려진 풍요, 쓰레기 여행", 2021)

### Why This Problem Matters

- 수도권 매립지 2025년 종료 확정 → 대안 부재 시 수도권 대규모 쓰레기 대란 발생 가능.
- 서울시와 인천광역시 간 쓰레기 매립지 갈등이 지속되고 있으며, 기존 공모 방식은 지자체의 자발적 참여에 의존해 모두 무산됨.
- 정치적 갈등과 주민 반발을 줄이기 위해 **정량적·객관적 데이터 기반 의사결정**이 필요함.

### Gap in Existing Work

기존 공모 방식은 지자체의 주관적·정치적 판단에 의존하여 다양한 환경·사회·법적 요인을 정량화하지 못했다. 법적 기준 충족 여부와 실제 입지 적합성(인구밀도·지형·접근성 등)을 통합한 체계적 분석이 부재했다.

### Related Work

- TOPSIS 기법을 활용한 한국형 항공모함 최적설계 방안 연구 ([KAIS, Vol.25 No.07](https://www.kais99.org/jkais/journal/Vol25no07/Vol25no07p32.pdf))
- 다기준-공간의사결정 관련 연구 (슬라이드 참고문헌 16번)
- 환경부 공간정보 포털 활용 입지 분석 ([egis.me.go.kr](https://egis.me.go.kr/map/map.do))

---

## Approach

> 프로젝트 유형: **Algorithm / Statistics**

### Formulation / Variables

**후보지 평가 기준 (6개 변수)**:

| 변수 | 방향 | 가중치(TOPSIS) | 의미 |
|---|---|---|---|
| 인구밀도 (명/km²) | 낮을수록 유리 | 0.20 | 거주민 영향 최소화 |
| 면적 (km²) | 높을수록 유리 | 0.10 | 사용 가능 부지 크기 |
| 접근성 점수 | 낮을수록 유리 | 0.10 | Σ(서울 구별 생활폐기물 발생량 × 관할 자원회수시설까지 경로 거리, 카카오 API) |
| 하수처리장 수 | 높을수록 유리 | 0.20 | 반경 내 하수처리시설 개수 |
| 침수면적 (100년 빈도, km²) | 낮을수록 유리 | 0.20 | 침수 위험 회피 |
| 경사도 (15도 이상 비율 합계) | 낮을수록 유리 | 0.20 | 지형 안정성 |

### Objective / Statistical Model

**3단계 파이프라인**:

1. **1차 후보 선정**: QGIS 공간 연산(합집합·차집합)으로 법적 제한 구역 제거 후 부지면적 50만㎡ 이상 필터링 → **98개 읍면동** 추출
2. **2차 후보 선정**: MinMaxScaler 정규화 후 PCA 기반 가중치 적용 스코어링 → 내림차순 상위 **20개 후보지** 추출
3. **최종 평가**: TOPSIS(Technique for Order Preference by Similarity to Ideal Solution)로 20개 후보지 최종 순위 도출 + 민감도 분석

**PCA 설명력 기반 가중치** (2차 스코어링용):

| PC1 | PC2 | PC3 | PC4 |
|---|---|---|---|
| 0.5574 | 0.2353 | 0.1308 | 0.0765 |

**TOPSIS 이상적/비이상적 해 설정**:
```python
benefit_criteria = [False, True, False, True, False, False]
# 인구밀도(↓), 면적(↑), 접근성(↓), 하수처리장(↑), 침수면적(↓), 경사도(↓)
```

### Assumptions

- 법적 제한 구역(개발제한구역, 농업보호구역, 상수원보호구역, 생태경관핵심보전지역, 습지보호지역 등)에는 매립지 입지 불가.
- 부지 면적 최소 50만㎡ (3차 공모 기준 90만㎡보다 보수적으로 완화 적용).
- 클러스터링(K-Means, Medoid, X-Means) 방식은 연구 후 채택하지 않음.

### Derivation / Key Steps

```
[원시 데이터] geo_data.shp + data98.csv
        ↓
[법적 필터링] EPSG:5186 투영 좌표계 변환 → 경기도 행정구역 추출 → 면적 ≥ 50만㎡ 필터
        ↓
[1차 전처리] 방향 통일(인구밀도, 접근성 역수 변환) → MinMaxScaler 정규화
        ↓
[PCA 스코어링] explained_variance_ratio_ 가중치 → Weighted Sum → 상위 20개 추출
        ↓
[추가 데이터 병합] float.xlsx(침수면적) + slope.csv(경사도) → final20.csv
        ↓
[TOPSIS] 벡터 정규화 → 가중치 적용 → 이상적/비이상적 해 계산 → Performance Score
        ↓
[민감도 분석] 가중치 ±0.05 변화 분석 + 기준 제외 분석
        ↓
[최종 결과] Top 3 후보지 확정
```

### Complexity / Notes

- 민감도 분석에서 **화성시 우정읍(Rank Range = 0)**과 **화성시 팔탄면(Rank Range = 0)**은 어떤 가중치 시나리오에서도 순위가 변하지 않아 결과 신뢰성이 높음.
- 하수처리장 제외 시 우정읍 순위 하락 → 우정읍의 하수처리장 환경 적합성 재확인.
- 경사도 제외 시 팔탄면 순위 하락 → 팔탄면의 경사도 조건 적합성 재확인.

---

## Data & Experiment

### Dataset Type

정형 데이터(표 형태) + 공간 데이터(Shapefile)

### Source (출처/링크)

| 데이터 | 출처 | URL |
|---|---|---|
| 행정구역 공간 데이터 (SHP) | 환경부 공간정보 포털 / GitHub 한국 행정구역 | https://egis.me.go.kr / https://github.com/cubensys/Korea_District |
| 인구밀도 | 통계청 KOSIS | https://kosis.kr/statHtml/statHtml.do?orgId=101&tblId=DT_1ZGA22 |
| 하수처리장 | 공공데이터포털 | https://www.data.go.kr/data/3073222/fileData |
| 접근성 점수 (경로 거리) | 카카오 Maps API | - |
| 침수면적 (100년 빈도) | 홍수 및 재해 지도 | https://floodmap.go.kr/natreg/natregList.do |
| 경사도 | 국토정보포털 (NEINS) | https://webgis.neins.go.kr/map.do |
| 생활폐기물 발생량 | 서울시 데이터 목록 | https://data.seoul.go.kr/dataList/370/S/2/datasetView.do |
| 토지 이용 규제 SHP | 환경부 공간정보 포털 | https://egis.me.go.kr/map/map.do |
| SGIS 인구 데이터 | 통계청 SGIS API | https://sgis.kostat.go.kr/developer/html/newOpenApi/api/dataApi/census.html |

### Size

- 1차: 경기·서울 전체 읍면동 → 법적 조건 충족 **98개 읍면동**
- 2차: PCA 스코어링 후 상위 **20개 읍면동**
- 최종 TOPSIS 입력: **15개 읍면동** (데이터 불충분·보안 지역 5개 제거)

### Label / Target Definition

정답 레이블 없음(비지도 학습 문제). TOPSIS Performance Score를 활용한 순위 기반 평가.

### Preprocessing

1. 경기도 행정구역 필터링: `ADM_CD` 앞 2자리 `'31'`로 경기도 추출
2. 좌표계 변환: `EPSG:5186` (한국 평면 직각 좌표계)로 통일
3. 면적 단위 변환: m² → km² (`/ 1,000,000`)
4. 방향 통일: 인구밀도, 접근성 점수는 역수 취해 "높을수록 유리"로 통일
5. 정규화: `MinMaxScaler` (0~1 범위로 압축)
6. 경사도 파생변수: 15도·20도·25도·30도 이상 구간 비율 합산 (`경사도 = '15~20' + '20~25' + '25~30' + '30~'`)
7. 결측치: slope.csv의 NaN → 0으로 대체

### Leakage Checks

해당 없음 (예측 문제가 아닌 다기준 평가 문제로 학습/테스트 분리 불필요).

### Split (Train / Val / Test)

해당 없음.

### Evaluation Protocol

TOPSIS Performance Score 기반 순위 도출 + 민감도 분석(가중치 ±0.05 변화, 기준 제외 분석) + 카카오맵 위성사진 현장 검증.

### Metrics

| 지표 | 설명 |
|---|---|
| **Performance Score** | TOPSIS 성능 점수 = (비이상적 해까지 거리) / (이상적 해까지 거리 + 비이상적 해까지 거리), 0~1, 높을수록 우수 |
| **Rank Range** | 민감도 분석 전 시나리오에서의 순위 최대값 - 최솟값, 낮을수록 안정적 |

### Environment

| 항목 | 사양 |
|---|---|
| OS | macOS |
| CPU | 추가 필요: 실행 환경 사양 미기재 |
| GPU | 해당 없음 (CPU 연산으로 충분) |
| Python | 추가 필요: 버전 미기재 |

### Frameworks / Libraries

```
pandas, numpy, matplotlib, seaborn
geopandas==0.14.4, fiona==1.10
shapely, pyproj
scikit-learn (MinMaxScaler, PCA, KMeans)
scipy
scikitmcda (TOPSIS, WSM, WPM, WASPAS, PROMETHEE_II, ELECTRE_I, VIKOR)
```

### Reproducibility

추가 필요: 랜덤 시드(random seed) 설정 코드 미기재. PCA·KMeans는 `random_state` 파라미터 지정 권장.

---

## Results

### TOPSIS 최종 순위 (15개 후보지)

| Rank | 위치 | Performance Score | 인구밀도 | 면적(km²) | 접근성 점수 | 하수처리장 | 침수면적 | 경사도 |
|---|---|---|---|---|---|---|---|---|
| **1** | **화성시 우정읍** | **0.7646** | 320 | 21.04 | 703,890 | 11 | 1.99 | 8.2 |
| **2** | **화성시 팔탄면** | **0.6738** | 268 | 42.31 | 567,051 | 5 | 2.70 | 19.5 |
| **3** | **화성시 봉담읍** | **0.6237** | 2,033 | 8.47 | 476,746 | 3 | 0.71 | 11.1 |
| 4 | 가평군 설악면 | 0.5885 | 72 | 67.09 | 646,763 | 5 | 0.70 | 70.5 |
| 5 | 고양시 고봉동 | 0.5748 | 949 | 5.81 | 355,783 | 0 | 1.36 | 17.5 |
| 6 | 양주시 장흥면 | 0.5698 | 184 | 0.77 | 358,996 | 2 | 0.07 | 55.1 |
| 7 | 고양시 고양동 | 0.5451 | 1,177 | 23.06 | 351,025 | 0 | 0.13 | 47.3 |
| 8 | 고양시 장항1동 | 0.5444 | 1,117 | 81.48 | 344,478 | 0 | 6.09 | 4.3 |
| 9 | 가평군 조종면 | 0.5358 | 86 | 97.42 | 698,373 | 5 | 2.46 | 84.5 |
| 10 | 고양시 관산동 | 0.5280 | 2,428 | 2.48 | 356,911 | 0 | 0.43 | 35.3 |
| 11 | 고양시 덕이동 | 0.4999 | 5,722 | 4.47 | 401,559 | 0 | 0.92 | 5.5 |
| 12 | 고양시 식사동 | 0.4812 | 6,019 | 0.84 | 352,019 | 0 | 0.10 | 22.3 |
| 13 | 고양시 풍산동 | 0.4805 | 6,700 | 9.65 | 358,656 | 0 | 1.39 | 4.8 |
| 14 | 김포시 고촌읍 | 0.4741 | 1,937 | 25.03 | 301,345 | 1 | 8.67 | 9.0 |
| 15 | 가평군 북면 | 0.4688 | 17 | 1.67 | 889,213 | 1 | 1.24 | 81.0 |

### 민감도 분석 결과 (안정도)

**가중치 ±0.05 변화 분석**:

| 위치 | Min Rank | Max Rank | Rank Range | 평가 |
|---|---|---|---|---|
| **화성시 우정읍** | **1** | **1** | **0** | 완전 안정 |
| **화성시 팔탄면** | **2** | **2** | **0** | 완전 안정 |
| 화성시 봉담읍 | 3 | 4 | 1 | 거의 안정 |
| (나머지 12개) | - | - | 2~8 | 상대적으로 불안정 |

### Visualization Notes

1. **Rank Range Bar Chart** (`bfd7c933` 셀): 15개 후보지를 가중치 변화 시나리오 전반에서의 순위 변동 범위(Rank Range) 기준 가로 막대 그래프. 화성시 우정읍·팔탄면의 Rank Range = 0으로 시각적으로 확인.
2. **Excluded Criteria Line Chart** (`3ed47b0e` 셀): 6개 기준 각각을 제거했을 때 15개 후보지의 순위 변화를 꺾은선 그래프로 표현. 하수처리장 제외 시 우정읍 하락, 경사도 제외 시 팔탄면 하락 패턴 명확히 확인 가능.

---

## Discussion

### Key Observations

1. **화성시 우정읍**은 모든 가중치 변화·기준 제외 시나리오에서 1위를 유지 → 가장 신뢰도 높은 최적 후보지.
2. **화성시 팔탄면**은 경사도 제외 시 순위가 눈에 띄게 하락 → 팔탄면 선정의 핵심 근거가 경사도 조건 충족임.
3. 접근성 점수 값 범위(`301,345 ~ 889,213`)가 다른 변수에 비해 압도적으로 커서 정규화 전 스케일 불균형이 존재했으나, MinMaxScaler로 해소.
4. 가평군 조종면·북면은 인구밀도가 매우 낮지만 경사도가 79~85에 달해 최종 하위권.
5. 기준 제외 분석에서 **하수처리장 기준 제거 시** 순위 변동이 상대적으로 크게 나타남 → 하수처리장 변수가 TOPSIS 결과에 큰 영향력.

### Interpretation

데이터 기반 접근 방식을 통해 화성시 우정읍이 인구밀도(낮음), 면적(중간), 하수처리 인프라(우수), 침수 위험(낮음), 지형 안정성(양호) 등 복합적 조건에서 가장 균형 잡힌 후보지임이 확인되었다. 최종적으로 카카오맵 위성사진을 통한 현장 검증에서도 적합한 토지 형태를 확인.

### Trade-offs

- TOPSIS는 해석이 쉽고 계산이 빠르지만, 가중치 설정이 결과에 민감하게 작용. → 민감도 분석으로 보완.
- PCA 가중치(2차 스코어링)는 데이터의 분산 구조를 반영하지만 실제 도메인 중요도와 다를 수 있음.
- 범주형 지표에 대한 엔트로피 가중치 방식은 연속형 데이터에 부적합하여 채택하지 않음.

### Failure Cases / Surprising Results

- 단순 등간격 가중치(모든 변수 동일 가중치)와 분산 기반 가중치 방법은 코드 내에서 구현 후 주석 처리됨 → 선택되지 않은 방법론의 비교 실험 결과는 노트북에 보존되어 있으나 최종 보고서에 미포함.
- 클러스터링(K-Means, K-Medoid, X-Means) 접근은 연구 단계에서 검토했으나 입지 선정 문제의 특성상 적합하지 않다고 판단하여 채택하지 않음(코드 없음).

### What I Learned

1. 공간 데이터 전처리에서 좌표계 통일(EPSG:5186)의 중요성 — 다른 좌표계로 면적 계산 시 오차 발생.
2. 다기준 의사결정에서 민감도 분석이 결과 신뢰성을 높이는 핵심 도구임.
3. 정량적 데이터 기반 접근이 주관적 갈등이 큰 사회 문제(혐오시설 입지)에 설득력 있는 대안을 제시할 수 있음.

---

## Limitations & Future Work

### Limitations

1. 실제 현장 조사 없이 위성사진 수준의 정성 검증에 그침 — 토질·지하수·소음 등 실측 데이터 부재.
2. 접근성 점수 산정 시 일부 구(금천구 등 민간 소각 의존 지역)는 제외하여 완전한 수도권 커버리지 미달.
3. 보안 지역 및 데이터 불충분 지역(5개 읍면동)은 사전 제거 처리 — 해당 지역의 잠재성 미평가.
4. 지역 주민 수용성, 부동산 가격, 지역 경제 영향 등 사회경제적 요인 미반영.
5. 클러스터링(K-Means 등) 방법론은 채택하지 않았으나 공간적 분포 측면의 대안 검토 미완.

### Future Directions

1. **실측 데이터 통합**: 토질 조사, 지하수위, 대기 확산 모델 데이터 추가.
2. **AHP(Analytic Hierarchy Process)** 방식으로 전문가 의견을 반영한 가중치 도출.
3. **다중 MCDA 방법 비교**: VIKOR, PROMETHEE II, ELECTRE I 등 scikitmcda에 구현된 방법론 결과 비교 (현재 라이브러리 임포트만 되어 있고 미사용).
4. **GIS 시각화 고도화**: 최종 후보지를 지도 위에 중첩하여 인터랙티브한 결과 시각화.
5. **수도권 전체 포함**: 서울시 내부 지역까지 확장한 분석.

### If I Had More Time

- 랜덤 가중치 분석(`random_weight_analysis_topsis`, 100회 반복) 결과를 기준별로 집계하여 확률적 안정성 지표 산출 (함수 구현됨, 결과 미출력).
- 기준 제외 분석(`exclusion_analysis_topsis`) 결과 표 정리 및 보고서 반영.

---

## Project Structure

```
garbage_dump/
├── 분석공모전코드_쓸애기들.ipynb        # 전체 분석 코드 (메인 엔트리포인트)
│     ├── SetUp                          # 라이브러리 임포트, 작업 디렉토리 설정
│     ├── Area (env=test)                # QGIS 연계 geo 데이터 전처리, 경기도 면적 산출
│     ├── Data (env=TaeYoung)            # data98.csv + area.csv 병합, 방향 통일, 정규화
│     ├── Score                          # PCA 가중치 스코어링, Top 20 추출
│     │     ├── 등간격 (주석 처리)
│     │     ├── 분산 기반 (주석 처리)
│     │     └── PCA 기반 (채택)
│     ├── merge                          # 침수면적(float.xlsx) + 경사도(slope.csv) 병합
│     └── MCDA                           # TOPSIS, 민감도 분석, 시각화
│           ├── TOPSIS 구현 및 실행
│           ├── 가중치 변화 민감도 분석
│           ├── 기준 제외 분석
│           └── 랜덤 가중치 분석 (함수 구현, 결과 미출력)
├── 분석공모전보고서_쓸애기들 (1).pdf    # 최종 제출 보고서 (2페이지)
├── 수도권 쓰레기 매립지 최적 위치 선정 (1).pdf   # 발표 슬라이드 (30페이지)
└── 무제.txt                             # 데이터 Google Drive 링크
```

**외부 데이터 경로** (코드 내 하드코딩된 경로 기준):
```
/Users/kangtaeyoung/Desktop/working/apstat_kartell/
├── data/
│   ├── geo/geo_data.shp        # 원본 행정구역 공간 데이터
│   ├── data98.csv              # 98개 읍면동 1차 후보 데이터
│   ├── data20.csv              # 20개 읍면동 2차 후보 데이터
│   ├── float.xlsx              # 침수면적 데이터
│   ├── slope.csv               # 경사도 데이터
│   └── final20_v3.csv          # MCDA 최종 입력 데이터
└── area.csv                    # 경기도 읍면동 면적 (산출 파일)
```

---

## PDF / Slides Mapping

### Main Slide Deck

| 파일명 | 페이지 수 | 비고 |
|---|---|---|
| `수도권 쓰레기 매립지 최적 위치 선정 (1).pdf` | 30 | 발표 슬라이드 (메인) |
| `분석공모전보고서_쓸애기들 (1).pdf` | 2 | 최종 제출 보고서 |

### Slide-to-README Mapping

| 섹션 | 슬라이드 페이지 |
|---|---|
| **Problem Statement** | p.3–6 (Introduction: 배경, 목표, 기존 방식 한계) |
| **Method/Architecture** | p.7–16 (법적 기준 선정, 접근성·사회적 기준, 데이터 전처리, PCA 스코어링) |
| **Experiment Setup** | p.7–16 (1~2차 후보 선정 과정, 데이터 수집 방법) |
| **Results/Comparison** | p.25–28 (TOPSIS 민감도 분석, 최적 위치 지도 확인) |
| **Ablation/Analysis** | p.25–27 (가중치 변화 분석, 기준 제외 분석, 시각화) |
| **Conclusion/Future Work** | p.28, p.30 (우정읍 최종 선정, 감사 인사) |

### Numbers Provenance

| 수치 | 출처 |
|---|---|
| 98개 읍면동 (1차 후보) | 슬라이드 p.9 + 노트북 `0b8fbde4` 셀 출력 |
| 20개 읍면동 (2차 후보) | 슬라이드 p.16 + 노트북 `343ac5ce` 셀 출력 |
| 15개 읍면동 (최종 TOPSIS) | 노트북 `6b9a1a4f` 셀 출력 (5개 제거 이유: 데이터 불충분/보안 지역) |
| PCA 가중치 [0.5574, 0.2353, 0.1308, 0.0765] | 노트북 `343ac5ce` 셀 출력 |
| TOPSIS 가중치 [0.2, 0.1, 0.1, 0.2, 0.2, 0.2] | 노트북 `6b9a1a4f` 코드 |
| 화성시 우정읍 Performance Score 0.7646 | 노트북 `6b9a1a4f` 셀 출력 |
| Rank Range 0 (우정읍·팔탄면) | 노트북 `10e92c72` 셀 출력 |

### Missing / Not Found

- 슬라이드 p.9: "태영 컴으로 최종 코드 한 번 돌려서 캡처 부탁하기!!!!" 메모 → 해당 캡처 이미지 PDF에 미포함.
- 최종 지도 시각화(카카오맵 위성 캡처, 슬라이드 p.28) — PDF 기반이나 이미지로만 존재, 수치 추출 불가.

---

## Citation & License

### Citation Info

```bibtex
@misc{garbage_dump_2024,
  title  = {수도권 쓰레기 매립지 문제 해결을 위한 최적 위치 선정},
  author = {강태영, 왕용웅, 김재환, 이승재, 이송아},
  year   = {2024},
  note   = {2024 응용통계학과 데이터 분석 공모전, 장려상(3위)}
}
```

### License

추가 필요: 라이선스 미지정. (공모전 제출 프로젝트로 공개 배포 여부 미정)

### Papers / Links

| 번호 | 자료 | URL |
|---|---|---|
| 1 | KBS "버려진 풍요, 쓰레기 여행" (2021.11.19) | https://youtube.com/watch?v=BxaCDMNfw2I |
| 2 | TOPSIS 기법을 활용한 한국형 항공모함 최적설계 방안 연구 (KAIS, Vol.25 No.07) | https://www.kais99.org/jkais/journal/Vol25no07/Vol25no07p32.pdf |
| 3 | 홍수 및 재해 지도 | https://floodmap.go.kr/natreg/natregList.do |
| 4 | 통계청 국가통계포털 (KOSIS) | https://kosis.kr/index/index.do |
| 5 | 환경부 공간정보 포털 | https://egis.me.go.kr/map/map.do |
| 6 | 공공데이터포털 (하수처리장) | https://www.data.go.kr/data/3073222/fileData |
| 7 | 국토정보포털 NEINS | https://webgis.neins.go.kr/map.do |
| 8 | 통계청 SGIS API | https://sgis.kostat.go.kr/developer/html/newOpenApi/api/dataApi/census.html |
| 9 | 한국 행정구역 GitHub | https://github.com/cubensys/Korea_District |
| 10 | 서울시 데이터 목록 (생활폐기물) | https://data.seoul.go.kr/dataList/370/S/2/datasetView.do |
| 11 | 한국경제 기사 (매립지 관련) | https://www.hankyung.com/article/2024062508951 |
| 12 | 재활용정보시스템 | https://www.recycling-info.or.kr/rrs/viewPage.do?menuNo=M130401 |
