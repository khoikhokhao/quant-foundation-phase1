# Quant Foundation — Phase 1 (Week 2–5)

Deliverables:
- **01 Data Ingestion & Preprocessing**
- **02 Strategy Components** (RSI, SMA/EMA, Bollinger Bands, Z-score + signals)
- **03 Backtesting Frameworks** (loop Pandas, metrics, trade log)
- **04 Code Quality & Repro** (Git, config YAML/JSON, cấu trúc repo)

---

## Repo Structure
```
.
├─ notebooks/
│  ├─ 01_Data_Ingest_Preprocess.ipynb
│  ├─ 02_Strategy_Components.ipynb
│  └─ 03_Backtesting_Frameworks.ipynb
├─ src/qbacktest/           # engine & utils tái sử dụng
│  ├─ __init__.py
│  ├─ utils.py              # calc_returns, drawdown, metrics, logger, load_config
│  └─ engine.py             # BaseStrategy, SignalColumnStrategy, run(), plotting helper
├─ configs/
│  └─ config.yaml
├─ data/
│  └─ README.md             # mô tả & cách đặt file dữ liệu (KHÔNG commit CSV)
├─ outputs/                 # equity, trades, metrics (sinh ra khi chạy)
├─ README.md
├─ requirements.txt
└─ .gitignore
```

> **Không push** dữ liệu thô lớn vào repo. Dùng `data/README.md` để hướng dẫn.

---

## Setup
```bash
pip install -r requirements.txt
```
`requirements.txt` (tối thiểu):
```
pandas==2.2.2
numpy==1.26.4
matplotlib==3.8.4
pyyaml==6.0.2   # nếu dùng YAML
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
project:
  name: quant-foundation-phase1
data:
  path: data/BTC_2019_2023_1d.csv
  tz: UTC
indicators:
  sma_short: 20
  sma_long: 50
  ema_short: 12
  ema_long: 26
  rsi_n: 14
  zscore_n: 20
  bollinger:
    win: 20
    k: 2.0
signals:
  rsi_low: 30
  rsi_high: 70
  z_long: -1.0
  z_short: 1.0
  use: sig_sma          # sig_sma | sig_rsi | sig_z
backtest:
  mode: fixed_pct       # full | fixed_pct
  risk_pct: 0.20
outputs:
  dir: outputs
  save_trades: true
  save_equity: true
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
# data & artifacts lớn
data/*.*
!data/README.md
outputs/*.png
outputs/*.parquet

# notebooks & hệ thống
.ipynb_checkpoints/
__pycache__/
.DS_Store
.env
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
