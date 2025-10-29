SMA Crossover Strategy — Project Script (BTC & ETH, Phase 1)

1) Mục tiêu
* Xây dựng và hiểu rõ chiến lược SMA Crossover (fast vs. slow) trên crypto.

* Pipeline: crawl dữ liệu → chuẩn hoá → tạo tín hiệu (no-lookahead) → backtest → tìm siêu tham số → so sánh BTC vs ETH.

* Trọng tâm Phase 1: tính đúng, giải thích được, dễ tái lập (không tối ưu hóa mù quáng).

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_


\2) Dữ liệu & tiền xử lý

* Nguồn: ccxt (Binance/OKX fallback); khung 1D; giai đoạn 2019-09-01 → 2025-10-29 (UTC).

* Chuẩn hoá: DatetimeIndex (UTC), cột open, high, low, close, volume; sort ↑; loại trùng; kiểm tra thiếu 1D = 0 cho cả BTC/ETH.

* Phí & trượt giá: fee = 5 bps, slippage = 2 bps mỗi lần đổi trạng thái.

* Vốn: $10,000.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_


\3) Chiến lược & backtest

3\.1 Logic SMA Crossover

* Tín hiệu: long = 1 khi SMA\_fast > SMA\_slow; ngược lại 0.

* No-lookahead: signal.shift(1) → quyết định hôm nay khớp lệnh tại T+1.

* Warm-up: chỉ backtest sau khi đủ cửa sổ SLOW.

3\.2 Engine (tối giản, vectorized)

* Lợi nhuận ròng ngày:

net\_ret\_t = pos\_{t-1} \* ret\_t − 1{trade\_t} \* (fee + slippage)

* Báo cáo: Cumulative Return, Sharpe (daily,252), Max Drawdown, Trades, Exposure%.

* Kiểm chứng: pos\_prev == signal.shift(1) ⇒ no-lookahead OK.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_


\4) Kết quả cơ sở (SMA 20/50)


Tài sản

`	`CumRet

`	`Sharpe

`	`MDD

`	`Trades

`	`Exposure%

`	`Buy&Hold CumRet

`	`Buy&Hold Sharpe

`	`Buy&Hold MDD

`	`BTC

`	`6.623

`	`0.822

`	`−0.552

`	      `50

`	    `55.90

`	`12.703

`	   `0.843

`	`−0.766

`	`ETH

`	`16.953

`	`0.893

`	`−0.622

`	      `44

`	    `53.50

`	`21.941

`	    `0.871

`	`−0.793

`	`Nhận xét nhanh

* Cả BTC & ETH: MDD giảm đáng kể so với Buy&Hold nhờ thoát khỏi giai đoạn mất xu hướng.

* Lợi nhuận tích lũy thấp hơn Buy&Hold vì exposure ~54–56% và whipsaw khi đi ngang.

* Sharpe của SMA(20/50) xấp xỉ hoặc nhỉnh hơn Buy&Hold trên ETH; trên BTC thì kém nhẹ.

\5) Tìm siêu tham số (grid search, tối ưu Sharpe)

* Lưới: FAST ∈ {5..60, step 5}, SLOW ∈ {50..250, step 10}, ràng buộc SLOW−FAST ≥ 10, lọc Trades ≥ 10.

* Cảnh báo: tối ưu toàn mẫu có nguy cơ overfit → dùng để khảo sát và khởi tạo, cần xác thực out-of-sample.


Tài sản

`	`Cấu hình tốt nhất

`	`Sharpe

`	`CumRet

`	`MDD

`	`Trades

`	`Exposure%

`	`BTC

`	`SMA(5,60)

`	    `1.034

`	     `13.436

`	     `−0.450

`	        `60

`	   `56.02

`	`ETH

`	`SMA(5,60)

`	    `0.969

`	      `24.503

`	      `−0.623

`	        `60

`	   `57.16

`	`Quan sát

* Cả BTC & ETH đều chọn FAST rất nhỏ (5) + SLOW trung bình (60) → vào sớm khi có trend, chấp nhận tăng số lệnh.

* BTC đạt Sharpe cao hơn ETH, nhưng ETH có CumRet lớn hơn (biên độ xu hướng mạnh hơn).

* MDD của BTC với SMA(5,60) giảm mạnh (−45%) so với Buy&Hold (−76%).

\7) Bài học Phase 1

* Đúng quy trình > điểm số: no-lookahead, phí/slippage, warm-up theo SLOW là bắt buộc.

* Regime matters: SMA hợp trend-following; khi sideways sẽ whipsaw → cân nhắc bộ lọc regime (SMA200, ADX, volatility).

* Tham số ảnh hưởng lớn: FAST nhỏ giúp bắt trend sớm nhưng tăng chi phí; SLOW quá lớn gây trễ & giảm exposure.

* Tối ưu cần kỷ luật: grid trên toàn mẫu chỉ để tham khảo; cần split thời gian (train/test) hoặc walk-forward.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_


\8) Khuyến nghị bước tiếp

1. Xác thực ngoài mẫu

* Chia train 2019–2023 / test 2024–2025; hoặc walk-forward 12–18 tháng.

2\. Bộ lọc regime

* Chỉ kích hoạt SMA khi price > SMA200 (bull) hoặc khi ATR% vượt ngưỡng (trend mạnh).

3\. Quản trị lệnh

* Thêm time-stop, trailing-stop, hoặc “partial exit” để giảm whipsaw.

4\. Danh mục

* Mở rộng sang ETH/BNB/SOL…, phân bổ theo volatility parity để giảm rủi ro idiosyncratic.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_


\9) Tóm tắt một câu

SMA Crossover ở mức cơ bản không đánh bại Buy&Hold về CumRet trong bull market dài, nhưng giảm drawdown đáng kể và cho Sharpe tốt khi chọn tham số hợp lý (đặc biệt là SMA(5,60)), với kết quả nhất quán trên cả BTC và ETH — nền tảng vững chắc để bước sang Phase 2 (regime filter & kiểm thử ngoài mẫu).
