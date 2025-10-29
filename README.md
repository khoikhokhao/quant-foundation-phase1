# Quant Foundation — Phase 1 (Week 2–5)

Backtesting hai chiến lược **RSI** và **SMA Crossover** trên crypto (BTC/ETH) theo tinh thần Phase 1: đúng đắn, minh bạch, tái lập. Dữ liệu crawl trực tiếp bằng `ccxt`, tín hiệu **no-lookahead**, có benchmark **Buy&Hold**, và lưu kết quả vào `results/`.

## 1) Cấu trúc repo
- `configs/config.yaml`: một file gom tất cả profiles (RSI_ETH, SMA_ETH, SMA_BTC) và preset grid.
- `notebooks/RSI_strategy.ipynb`, `notebooks/SMA_ETH_Strategy.ipynb`, `notebooks/SMA_BTC_Strategy.ipynb`: notebook thí nghiệm và phân tích.
- `reports/`: tóm tắt kết quả dạng markdown cho từng bài.
- `results/YYYY-MM-DD/`: ảnh equity và JSON metrics cho mỗi lần chạy.
- `src/backtest_core.py`: engine tối giản (PnL, metrics, blotter).
- `requirement.txt`, `.gitignore`.

## 2) Cài đặt và chạy nhanh
- Cài đặt: `pip install -r requirement.txt`
- Mở notebook trong thư mục `notebooks/` và chạy theo thứ tự cell.
- Tham số và cấu hình sửa trong `configs/config.yaml` (symbol, timeframe, phí/slippage, vốn, tham số chiến lược, grid).

## 3) Nguyên tắc backtest (Phase 1)
- Tín hiệu được dịch **+1 bar** để khớp lệnh tại T+1 (tránh lookahead).
- Lợi nhuận ròng ngày: vị thế của ngày hôm trước nhân với lợi nhuận ngày hiện tại, trừ chi phí khi đổi trạng thái (phí 5 bps, trượt giá 2 bps mặc định).
- Báo cáo gồm: Cumulative Return, Sharpe (daily, 252), Max Drawdown, số lệnh, phần trăm thời gian có vị thế.
- Buy&Hold được so sánh trên cùng khoảng warm-up để công bằng.

## 4) Kết quả mẫu (ngày 2025-10-29)
- RSI trên ETH (period 14, ngưỡng 30/70, stateful): giảm drawdown so với Buy&Hold nhưng lợi nhuận tích lũy thấp hơn do bỏ lỡ các đoạn bull dài; phơi nhiễm thấp khoảng một phần ba thời gian.
- SMA 20/50 trên ETH và BTC: giảm drawdown rõ rệt so với Buy&Hold; tổng lợi nhuận thấp hơn trong bull market vì phơi nhiễm khoảng một nửa thời gian và bị whipsaw khi thị trường đi ngang.
- Grid search theo Sharpe gợi ý cấu hình nhanh **SMA(5,60)** cho cả BTC và ETH; cấu hình này vào sớm khi có xu hướng nhưng số lệnh tăng, nhạy với chi phí; cần kiểm tra thêm ngoài mẫu.

## 5) Ý nghĩa và bài học
- Đúng quy trình trước tối ưu: no-lookahead, phí/slippage, warm-up theo cửa sổ dài là bắt buộc.
- Chiến lược phụ thuộc chế độ thị trường: RSI hợp mean-reversion; SMA hợp trend-following và sẽ whipsaw khi sideway.
- Tham số ảnh hưởng mạnh: FAST nhỏ giúp bắt trend sớm nhưng làm tăng chi phí; cần cân bằng giữa lợi nhuận, drawdown và số lệnh.
- Tránh overfit: grid trên toàn mẫu chỉ để tham khảo; nên dùng chia thời gian train/test hoặc walk-forward.

## 6) Artefacts và JSON metrics
- Mỗi lần chạy sinh ra ảnh đường vốn và một file JSON ghi ngữ cảnh (symbol, khoảng thời gian, phí), chỉ số chiến lược, chỉ số Buy&Hold và đường dẫn artefact.
- Ví dụ tên file: `rsi_eth_metrics.json`, `sma_eth_metrics.json`, `sma_btc_metrics.json` trong `results/YYYY-MM-DD/`.

## 7) Hướng mở rộng (Phase 2)
- Kiểm thử ngoài mẫu bằng chia mốc thời gian hoặc walk-forward.
- Thêm bộ lọc chế độ (SMA200, ADX/ATR%) để bật chiến lược khi có xu hướng rõ.
- Thêm quản trị lệnh: time-stop, trailing-stop, partial exit.
- Mở rộng danh mục nhiều tài sản và phân bổ theo rủi ro.

## 8) Bản quyền và liên hệ
- Giấy phép: MIT.
- Tác giả: Khoi Pham — Phase 1 Quant Trading Foundation.
