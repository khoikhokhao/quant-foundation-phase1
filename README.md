# Quant Foundation — Phase 1 (Week 2–5)

> **Mục tiêu:** Xây dựng nền tảng định lượng với pipeline dữ liệu → chỉ báo → tín hiệu → backtest (đúng & tái lập), sau đó **thực hành** 2 chiến lược cơ bản: **RSI (stateful)** và **SMA Crossover** trên crypto.

## Deliverables (đã hoàn thành)
- **01 Data Ingestion & Preprocessing** (crawl API + chuẩn hóa UTC)
- **02 Strategy Components** (RSI, SMA; tín hiệu không lookahead)
- **03 Backtesting Frameworks** (engine Pandas, metrics, blotter)
- **04 Code Quality & Repro** (Git, config YAML; cấu trúc repo)
- **Exercise 1:** **RSI Strategy** (crawl → chuẩn hóa → backtest → sensitivity & grid search)
- **Exercise 2:** **SMA Strategy** cho **ETH** & **BTC** (backtest & grid search FAST/SLOW)

---

## Repo Structure
```
.
├─ notebooks/phase1/
│ ├─ 01_Data_Ingest_Preprocess.ipynb
│ ├─ 02_Strategy_Components.ipynb
│ ├─ 03_Backtesting_Frameworks.ipynb
│ ├─ 06_RSI_Strategy.ipynb
│ ├─ 07_SMA_ETH_Strategy.ipynb
│ └─ 08_SMA_BTC_Strategy.ipynb
├─ src/
│ ├─ engine/
│ │ ├─ backtest_core.py # net_ret, equity, metrics, blotter
│ │ └─ plotting.py
│ ├─ indicators/
│ │ ├─ rsi.py # rsi_series(close, n)
│ │ └─ sma.py # sma_series(close, win)
│ ├─ strategies/
│ │ ├─ rsi_stateful.py # buy<TH, hold until sell>TH (shift+1)
│ │ └─ sma_crossover.py # SMA_fast > SMA_slow (shift+1)
│ └─ data/ccxt_fetch.py # crawl OHLCV: binance → okx → kraken → ...
├─ scripts/
│ ├─ fetch_ohlcv.py # tải dữ liệu theo config
│ ├─ run_backtest.py # chạy chiến lược & in báo cáo
│ └─ grid_search.py # quét RSI/SMA theo config.grid_search
├─ configs/
│ └─ config_phase1.yaml # cấu hình chung (RSI & SMA)
├─ reports/phase1/ # markdown + figures (equity, heatmap)
├─ data/ # không commit CSV (dùng .gitkeep)
├─ requirements.txt
├─ .gitignore
└─ README.md (file này)

> **Không push** dữ liệu thô lớn vào repo. Dùng `data/README.md` để hướng dẫn.

---

## Setup
```bash
pip install -r requirements.txt
```
`requirements.txt` (tối thiểu):
```
ccxt==4.*
pandas
numpy
matplotlib
pytz
PyYAML

```

---

## Data (local path, không commit CSV)
- File yêu cầu: **`data/BTC_2019_2023_1d.csv`**
- Schema: `datetime, open, high, low, close, volume` (datetime ở định dạng `dd-mm-YYYY`)
- Thời gian được parse và chuyển sang **UTC** trong pipeline.
- Đặt file ở: `data/BTC_2019_2023_1d.csv` và cấu hình trong `configs/config.yaml`:
```yaml
data:
  path: data/BTC_2019_2023_1d.csv
  tz: UTC
```

Ví dụ vài dòng đầu:
```
datetime,open,high,low,close,volume
08-09-2019,10000.00,10412.65,10000.00,10391.63,3096.291
09-09-2019,10316.62,10475.54,10077.22,10307.00,14824.373
```

---

## Config (YAML)
Mẫu `configs/config.yaml`:
```yaml
project: { name: "phase1-crypto-strategies", seed: 42, output_dir: "reports/phase1" }
data: { exchange_priority: ["binance","okx","kraken","kucoin","coinbase","bitfinex","gateio"],
        symbol: "ETH/USDT", timeframe: "1d", start_date: "2019-09-01", end_date: null, tz: "UTC" }
fees: { fee_bps: 5, slippage_bps: 2, start_cash: 10000 }
backtest: { shift_exec_bars: 1, report_metrics: ["cumret","sharpe_252","mdd","trades","exposure_pct"], plot_equity: true }
strategy:
  type: "rsi"            # "rsi" | "sma"
  rsi: { period: 14, buy_th: 30, sell_th: 70 }
  sma: { fast: 20, slow: 50 }
grid_search:
  enable: false
  rsi: { buy_range: [15,45,2], sell_range: [55,95,2], gap_min: 20, min_trades: 5 }
  sma: { fast_range: [5,60,5], slow_range: [50,250,10], gap_min: 10, min_trades: 10 }
  top_k: 10
experiments:
  - { name: "RSI_ETH_14_30_70", data: {symbol: "ETH/USDT"}, strategy: {type:"rsi"} }
  - { name: "SMA_ETH_5_60",     data: {symbol: "ETH/USDT"}, strategy: {type:"sma", sma:{fast:5,slow:60}} }
  - { name: "SMA_BTC_5_60",     data: {symbol: "BTC/USDT"}, strategy: {type:"sma", sma:{fast:5,slow:60}} }

```

> Điểm mấu chốt: **mọi tham số** thí nghiệm nằm trong **config** để tái lập & checkpoint bằng Git.

---

## How to Run (Local)
1. Đặt dữ liệu tại `data/BTC_2019_2023_1d.csv`; cập nhật `configs/config.yaml` nếu cần.
2. Mở notebook theo thứ tự:
   - `notebooks/01_Data_Ingest_Preprocess.ipynb`
   - `notebooks/02_Strategy_Components.ipynb`
   - `notebooks/03_Backtesting_Frameworks.ipynb`
3. Outputs sẽ lưu ở `outputs/`:
   - `equity_<signal>.csv`
   - `trades_<signal>.csv`
   - (tuỳ chọn) `metrics.json`

## How to Run (Google Colab)
- Upload `src/`, `configs/`, `notebooks/` lên Colab.
- Upload `data/BTC_2019_2023_1d.csv` qua `files.upload()` **hoặc** gắn Google Drive rồi trỏ `data.path` tới đúng đường dẫn.
- Chạy 01 → 03.

---

## Backtesting Notes
- **No lookahead**: tín hiệu dùng cho ngày **t+1** (`shift(1)`).
- **Position sizing**:
  - `full`: pos ∈ {−1, 0, +1}
  - `fixed_pct`: trọng số w ∈ {−k, 0, +k}; PnL = `w_{t-1} * r_t`
- **Metrics** (hàm `perf_summary`):
  - CAGR, Annualized Vol, Sharpe, Max Drawdown, EquityEnd, Ndays.
- **Artifacts**:
  - `trades_*.csv` (timestamp, action, price, size/weight, equity_after)
  - `equity_*.csv` (timestamp, equity, drawdown)

---

## Code Quality & Reproducibility
- **Git**: commit nhỏ–thường xuyên; dùng nhánh cho tính năng/experiment; tag mốc stable (`v1.0-week5`).
- **Docs**: README (repo-level) + inline comments/docstrings (tập trung “tại sao”).
- **Config I/O**: YAML/JSON cho tham số chiến lược; pin versions trong `requirements.txt`.
- **One-command run** (tùy chọn): script đọc `config.yaml` và chạy toàn pipeline, xuất `outputs/`.

---

## .gitignore (gợi ý)
```
data/*.*          # không commit CSV
!data/**/.gitkeep
reports/**/figures/*.png
.ipynb_checkpoints/
__pycache__/
*.pyc
.DS_Store
```

---

## Git Quickstart
```bash
git init
git add .
git commit -m "feat: notebooks 01-03 + qbacktest engine + configs"
git branch -M main
git remote add origin https://github.com/<USER>/quant-foundation-phase1.git
git push -u origin main

# Tag mốc nộp bài
git tag v1.0-week5
git push origin v1.0-week5
```
