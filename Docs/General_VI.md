# Hướng Dẫn Tổng Quan — Nền Tảng IMC Prosperity 4

> **Dành cho ai?** Bất kỳ ai muốn tham gia IMC Prosperity 4 — dù bạn chưa biết lập trình, chưa biết giao dịch, hay chưa biết toán. Hướng dẫn này giải thích MỌI THỨ từ đầu.

---

## Mục lục

- [Phần 1: Giới thiệu](#phan-1-gioi-thieu)
  - [1. IMC Prosperity là gì?](#1-imc-prosperity-la-gi)
  - [2. Prosperity 4 vs phiên bản trước](#2-prosperity-4-vs-phien-ban-truoc)
- [Phần 2: Thị trường và Sàn giao dịch (Exchange)](#phan-2-thi-truong-va-san-giao-dich-exchange)
  - [3. Exchange (Sàn giao dịch) là gì?](#3-exchange-san-giao-dich-la-gi)
  - [4. Order Book (Sổ lệnh)](#4-order-book-so-lenh)
  - [5. Các loại lệnh (Order Types)](#5-cac-loai-lenh-order-types)
  - [6. Order Matching — Cách khớp lệnh](#6-order-matching--cach-khop-lenh)
- [Phần 3: Hệ thống Mô phỏng](#phan-3-he-thong-mo-phong)
  - [7. Tick — Đơn vị thời gian](#7-tick--don-vi-thoi-gian)
  - [8. TradingState — Gói thông tin mỗi tick](#8-tradingstate--goi-thong-tin-moi-tick)
  - [9. Position Limit — Giới hạn vị thế](#9-position-limit--gioi-han-vi-the)
  - [10. Hàm run() — Trái tim của bot](#10-ham-run--trai-tim-cua-bot)
  - [11. traderData — Bộ nhớ giữa các tick](#11-traderdata--bo-nho-giua-cac-tick)
- [Phần 4: Lộ trình học](#phan-4-lo-trinh-hoc)
  - [12. Lộ trình Round 1 đến Round 5](#12-lo-trinh-round-1-den-round-5)
- [Phần 5: Tham khảo](#phan-5-tham-khao)
  - [13. Các lỗi thường gặp](#13-cac-loi-thuong-gap)
  - [14. Checklist trước khi nộp bài](#14-checklist-truoc-khi-nop-bai)
  - [15. Glossary / Từ điển thuật ngữ](#15-glossary--tu-dien-thuat-ngu)

---

# PHẦN 1: GIỚI THIỆU

---

## 1. IMC Prosperity là gì?

### Hình dung như thế này...

Bạn biết các cuộc thi lập trình như thi code trên HackerRank hay LeetCode không? IMC Prosperity cũng là một cuộc thi, nhưng thay vì giải bài tập thuật toán, bạn sẽ **viết code Python để điều khiển một con robot giao dịch**.

Hay tưởng tượng thế này: bạn đang ở chợ Bà Chiểu. Có rất nhiều người mua và bán trái cây. Bạn thuê một người giúp việc (con robot của bạn), và bạn viết một tờ giấy hướng dẫn cho người này: "Nếu thấy xoài giá dưới 20 ngàn thì mua, nếu thấy ai trả hơn 25 ngàn thì bán." Người giúp việc của bạn sẽ làm theo hướng dẫn đó tự động, không cần bạn đứng đó.

IMC Prosperity cũng tương tự — nhưng thay vì trái cây, bạn mua bán các **sản phẩm tài chính ảo** (như cổ phiếu, hàng hóa). Và thay vì viết trên giấy, bạn viết bằng **Python**.

### Chi tiết cuộc thi

- **5 vòng (rounds)** trong khoảng **15 ngày**
- Mỗi vòng thêm sản phẩm mới, nhưng sản phẩm cũ vẫn còn
- Bạn chỉ cần nộp **1 file Python** mỗi vòng — file này chứa toàn bộ logic của bot
- Bot của bạn sẽ tự động giao dịch trong một **mô phỏng (simulation)**:
  - Khi test: **1,000 lần lặp (iterations)**
  - Khi chấm điểm cuối: **10,000 lần lặp**
- Đơn vị tiền tệ: **XIRECs** (phiên bản Prosperity 4)
- Mục tiêu: **kiếm được nhiều XIRECs nhất có thể**

### Ví dụ đơn giản

Giả sử bot của bạn mua 1 đơn vị RAINFOREST_RESIN (nhựa cây) giá 9,998 XIRECs, rồi bán lại giá 10,002 XIRECs. Bạn vừa kiếm được:

```
Lợi nhuận = 10,002 - 9,998 = 4 XIRECs
```

Làm như vậy 10,000 lần một ngày, mỗi lần lời 4 XIRECs = 40,000 XIRECs/ngày. Nghe ít nhưng cộng dồn lại rất lớn!

> **Ví dụ thực tế:** Hãy nghĩ như bạn bán nước ở trước cổng trường. Bạn mua chai nước giá 3,000đ và bán lại giá 5,000đ. Mỗi chai lời 2,000đ. Nếu bán 100 chai/ngày thì lời 200,000đ. Bot của bạn làm điều tương tự — nhưng nhanh hơn nhiều và tự động!

### Tại sao nên tham gia?

1. **Học lập trình Python** qua dự án thực tế (không phải bài tập nhàm chán)
2. **Học về tài chính** và cách thị trường hoạt động
3. **Cơ hội nhận việc** tại IMC Trading — một trong những công ty giao dịch lớn nhất thế giới
4. **Giải thưởng** cho đội xếp hạng cao
5. **Vui** — cuộc thi được thiết kế như một trò chơi với câu chuyện hấp dẫn

---

## 2. Prosperity 4 vs phiên bản trước

Prosperity 4 có một số thay đổi so với các phiên bản trước. Điều này quan trọng vì nhiều tài liệu và code mẫu trên mạng là từ Prosperity 3 hoặc cũ hơn.

| | Prosperity 3 (ví dụ từ Frankfurt) | Prosperity 4 (hiện tại) |
|---|---|---|
| **Đơn vị tiền** | SeaShells | **XIRECs** |
| **Round 2+** | Không bắt buộc | **Cần method `bid()`** |
| **traderData** | Không giới hạn rõ ràng | **Tối đa 50,000 ký tự** |
| **Mô phỏng** | — | **1,000 test / 10,000 final** |
| **Giới hạn vị thế** | Cố định | **Có thể thay đổi — kiểm tra mỗi round** |

> **Lưu ý quan trọng:** Hướng dẫn này sử dụng code của **Frankfurt Hedgehogs** (đội xếp hạng #2, Prosperity 3) làm ví dụ. Code của họ là Prosperity 3, nên khi bạn thấy `SeaShells` hay nghĩ là `XIRECs`, và có thể cần điều chỉnh một số chi tiết nhỏ cho Prosperity 4.

### Tại sao dùng code Frankfurt?

Frankfurt Hedgehogs là một trong những đội giỏi nhất Prosperity 3. Họ đã chia sẻ code và chiến lược. Học từ code thật của đội top là cách nhanh nhất để hiểu cách làm đúng.

> **Điều cần nhớ:**
> - Thay `SeaShells` thành `XIRECs` trong suy nghĩ của bạn
> - Nếu dùng Round 2+ của Prosperity 4, bạn cần viết thêm method `bid()` — chi tiết trong hướng dẫn riêng của từng round
> - Luôn kiểm tra `traderData` không vượt quá 50,000 ký tự

---

# PHẦN 2: THỊ TRƯỜNG VÀ SÀN GIAO DỊCH (EXCHANGE)

---

## 3. Exchange (Sàn giao dịch) là gì?

### Ví dụ thực tế

Hãy tưởng tượng bạn đến **quầy đổi tiền ở sân bay**. Bạn muốn đổi USD sang VND. Quầy đổi tiền sẽ có:
- **Giá mua (bid):** "Chúng tôi mua 1 USD với giá 24,500 VND" — đây là giá họ sẵn sàng trả cho bạn
- **Giá bán (ask):** "Chúng tôi bán 1 USD với giá 25,000 VND" — đây là giá bạn phải trả để mua từ họ

Sự **chênh lệch** giữa 2 giá này (25,000 - 24,500 = 500 VND) là cách quầy đổi tiền kiếm lời. Trong tiếng Anh gọi là **spread**.

### Exchange trong Prosperity

Trong IMC Prosperity, **Exchange** là một **chợ trung tâm ảo** (simulated marketplace) nơi:
- Bot của bạn giao dịch cùng với **các bot khác** (do IMC tạo ra)
- Mọi thứ tự động — bạn **không cần bấm nút** gì cả
- Bot của bạn gửi **lệnh mua/bán**, và hệ thống tự động khớp các lệnh phù hợp

```
         ┌─────────────────────────────┐
         │       EXCHANGE (Sàn)         │
         │                             │
   Bạn → │  Bot bạn  ↔  Bot IMC #1    │
         │           ↔  Bot IMC #2    │
         │           ↔  Bot IMC #3    │
         │           ↔  Bot đối thủ   │
         └─────────────────────────────┘
```

### Mọi thứ diễn ra tự động

Đây là điều quan trọng nhất cần hiểu: khi cuộc thi đang chạy, bạn **không thể can thiệp**. Bot của bạn tự chạy theo code đã viết. Giống như bạn đã dạy robot làm việc, rồi ngồi nhìn nó làm — không thể nhảy vào giữa chừng đưa tay chỉ.

> **Ví dụ:** Giống như bạn viết chương trình cho máy giặt. Bạn cài đặt: giặt 30 phút, xả 2 lần, vắt khô. Máy giặt sẽ làm đúng như vậy — bạn không thể dừng giữa để thay đổi. Bot giao dịch của bạn cũng tương tự!

---

## 4. Order Book (Sổ lệnh)

### Tưởng tượng một cái bảng trắng

Hãy nghĩ Order Book như một **cái bảng trắng lớn** đặt giữa chợ. Bên trái là những người muốn **mua**, bên phải là những người muốn **bán**. Mỗi người ghi lên bảng: "Tôi muốn mua/bán X cái, giá Y đồng."

Khi có người mua và người bán đồng ý giá, họ trao đổi xong và xóa tên khỏi bảng. Những người chưa khớp thì vẫn nằm trên bảng, chờ đợi.

### Minh họa cho RAINFOREST_RESIN

Giả sử RAINFOREST_RESIN có giá trị thật (fair value) khoảng 10,000 XIRECs. Đây là những gì bạn có thể thấy trên Order Book:

```
============================================================
               ORDER BOOK: RAINFOREST_RESIN
============================================================

  PHÍA BÁN (sell_orders):          ← Những người muốn BÁN
  ┌─────────────────────────────────────────────────┐
  │  Giá 10,002  →  25 cái        ← ask_wall       │
  │  Giá 10,001  →  10 cái        ← best_ask       │
  └─────────────────────────────────────────────────┘

  ───────── GIÁ TRỊ THẬT (FAIR VALUE) ≈ 10,000 ─────────

  PHÍA MUA (buy_orders):           ← Những người muốn MUA
  ┌─────────────────────────────────────────────────┐
  │  Giá  9,999  →  10 cái        ← best_bid       │
  │  Giá  9,998  →  20 cái        ← bid_wall       │
  └─────────────────────────────────────────────────┘

============================================================
```

**Đọc bảng này thế nào?**

- **Phía bán (sell_orders):** Có người sẵn sàng bán 10 cái giá 10,001, và 25 cái giá 10,002
- **Phía mua (buy_orders):** Có người sẵn sàng mua 10 cái giá 9,999, và 20 cái giá 9,998
- **Chưa ai khớp** vì người mua cao nhất (9,999) vẫn thấp hơn người bán rẻ nhất (10,001)

### Trong code Python

Trong Prosperity, Order Book được thể hiện như 2 dictionary (từ điển Python):

```python
# Lấy order book của RAINFOREST_RESIN
order_depth = state.order_depths["RAINFOREST_RESIN"]

# =====================================================
# PHÍA BÁN (sell_orders)
# LƯU Ý QUAN TRỌNG: Volume là SỐ ÂM!!!
# IMC quy định: sell_orders có volume âm
# =====================================================
order_depth.sell_orders = {
    10001: -10,    # Có 10 cái đang bán giá 10,001
                   # Volume là -10 (âm!) vì là lệnh bán
    10002: -25,    # Có 25 cái đang bán giá 10,002
                   # Đây là "ask_wall" = giá bán xa nhất
}

# =====================================================
# PHÍA MUA (buy_orders)
# Volume là SỐ DƯƠNG (bình thường)
# =====================================================
order_depth.buy_orders = {
    9999: 10,      # Có 10 cái đang mua giá 9,999
                   # Đây là "best_bid" = giá mua cao nhất
    9998: 20,      # Có 20 cái đang mua giá 9,998
                   # Đây là "bid_wall" = giá mua xa nhất
}
```

> **CẢNH BÁO:** Đây là lỗi **phổ biến nhất** của người mới! `sell_orders` có volume **ÂM**. Khi bạn muốn biết có bao nhiêu cái đang bán, phải dùng `abs()`:
> ```python
> # SAI — sẽ ra số âm!
> quantity = order_depth.sell_orders[10001]   # → -10
>
> # ĐÚNG — dùng abs() để lấy số dương
> quantity = abs(order_depth.sell_orders[10001])   # → 10
> ```

### Bảng thuật ngữ Order Book

| Thuật ngữ | Ý nghĩa | Code |
|-----------|---------|------|
| **best_ask** | Giá bán rẻ nhất (tốt nhất cho người mua) | `min(sell_orders.keys())` |
| **best_bid** | Giá mua cao nhất (tốt nhất cho người bán) | `max(buy_orders.keys())` |
| **spread** | Khoảng cách giữa best_ask và best_bid | `best_ask - best_bid` |
| **mid_price** | Giá ở giữa | `(best_ask + best_bid) / 2` |
| **bid_wall** | Giá mua xa nhất (thường volume lớn) | `min(buy_orders.keys())` |
| **ask_wall** | Giá bán xa nhất (thường volume lớn) | `max(sell_orders.keys())` |
| **wall_mid** | Trung bình của 2 tường | `(bid_wall + ask_wall) / 2` |

### Tính các giá trị trong code

```python
order_depth = state.order_depths["RAINFOREST_RESIN"]

# Best ask = giá bán rẻ nhất
best_ask = min(order_depth.sell_orders.keys())  # → 10,001

# Best bid = giá mua cao nhất
best_bid = max(order_depth.buy_orders.keys())   # → 9,999

# Spread = khoảng cách
spread = best_ask - best_bid                     # → 2

# Mid price = giá giữa
mid_price = (best_ask + best_bid) / 2            # → 10,000.0

# Volume tại best_ask (nhớ dùng abs()!)
ask_volume = abs(order_depth.sell_orders[best_ask])  # → 10

# Volume tại best_bid
bid_volume = order_depth.buy_orders[best_bid]        # → 10
```

### Sổ lệnh "Crossed" vs "Uncrossed"

Bình thường, `best_bid < best_ask` — chưa ai đồng ý giá với nhau. Đây gọi là **uncrossed book** (sổ lệnh bình thường).

```
Uncrossed (bình thường):
  Người bán rẻ nhất: 10,001
  Người mua đắt nhất: 9,999
  → Chưa ai khớp vì 9,999 < 10,001
```

Nhưng đôi khi, có người gửi lệnh mua giá cao hơn người bán (hoặc ngược lại). Khi đó, `best_bid >= best_ask`. Đây gọi là **crossed book** — và giao dịch xảy ra ngay lập tức!

```
Crossed (giao dịch ngay):
  Người bán rẻ nhất: 10,000
  Người mua đắt nhất: 10,001
  → Khớp ngay vì 10,001 >= 10,000!
```

> **Ví dụ thực tế:** Bạn đi chợ, thấy xoài giá 20,000đ. Bạn nói "Tôi mua 25,000đ!" — dĩ nhiên người bán đồng ý ngay vì bạn trả nhiều hơn họ muốn. Đây là crossed book — giao dịch xảy ra tức thì.

> **Vừa xảy ra gì?** Order Book giống như một cái bảng thông báo ở chợ. Một bên ghi giá mua, một bên ghi giá bán. Khi giá mua >= giá bán, giao dịch xảy ra. Bot của bạn đọc cái bảng này mỗi tick để quyết định mua hay bán.

---

## 5. Các loại lệnh (Order Types)

### Trong thế giới thực có 3 loại lệnh

Trước khi nói về Prosperity, hãy hiểu 3 loại lệnh cơ bản trong giao dịch thật:

**1. Market Order (Lệnh thị trường):**
- "Mua ngay lập tức, bất kể giá nào!"
- Giống như bạn vào cửa hàng và nói: "Cho tôi 1 kg xoài, bao nhiêu cũng được"
- Ưu điểm: mua được ngay
- Nhược điểm: có thể bị giá cao

**2. Limit Order (Lệnh giới hạn):**
- "Mua, nhưng chỉ khi giá bằng hoặc thấp hơn X"
- Giống như bạn nói: "Tôi chỉ mua xoài nếu giá 20,000đ hoặc rẻ hơn"
- Ưu điểm: kiểm soát được giá
- Nhược điểm: có thể không mua được nếu không ai bán giá đó

**3. Stop Order (Lệnh điều kiện):**
- "Khi giá chạm mức X, thì tự động đặt lệnh"
- Giống như bạn dặn: "Nếu xoài tăng lên 30,000đ thì bán hết xoài của tôi"
- Dùng để cắt lỗ hoặc chốt lời

### Prosperity CHỈ DÙNG Limit Order!

Trong Prosperity, bạn **chỉ có thể đặt Limit Order**. Điều này đơn giản hơn nhiều — bạn luôn phải chỉ rõ giá:

```python
# Cách tạo 1 lệnh trong Prosperity
Order(product, price, quantity)

# Ví dụ: Mua 5 cái RAINFOREST_RESIN giá 9,998
Order("RAINFOREST_RESIN", 9998, 5)      # quantity DƯƠNG = MUA

# Ví dụ: Bán 3 cái RAINFOREST_RESIN giá 10,002
Order("RAINFOREST_RESIN", 10002, -3)    # quantity ÂM = BÁN
```

> **Lưu ý quan trọng:**
> - `quantity > 0` nghĩa là **MUA**
> - `quantity < 0` nghĩa là **BÁN**
> - Quên dấu âm khi bán là một lỗi rất phổ biến!

### 2 cách hành xử của Limit Order

Mặc dù chỉ có 1 loại lệnh, nhưng nó có 2 cách hành xử tùy thuộc vào giá bạn đặt:

| Loại | Tên tiếng Anh | Ý nghĩa | Khi nào xảy ra | Ví dụ |
|------|---------------|---------|-----------------|-------|
| **Hung hăng** | Aggressive / Taking | "Ăn" lệnh có sẵn | MUA giá >= best_ask, hoặc BÁN giá <= best_bid | Mua giá 10,001 khi best_ask = 10,001 → khớp ngay! |
| **Thụ động** | Passive / Making | Đặt lệnh và chờ | MUA giá < best_ask, hoặc BÁN giá > best_bid | Mua giá 9,999 khi best_ask = 10,001 → chờ ai bán giá 9,999 |

#### Ví dụ minh họa:

```
Order Book hiện tại:
  best_ask = 10,001 (có 10 cái đang bán)
  best_bid = 9,999  (có 10 cái đang mua)
```

**Trường hợp 1 — Aggressive (Ăn lệnh):**
```python
# Bạn muốn mua NGAY LẬP TỨC
# Đặt giá MUA = 10,001 (bằng best_ask)
Order("RAINFOREST_RESIN", 10001, 5)
# → Khớp ngay 5 cái từ người bán giá 10,001
# → Bạn trả 5 x 10,001 = 50,005 XIRECs
```

**Trường hợp 2 — Passive (Đặt chờ):**
```python
# Bạn muốn mua GIÁ RẺ HƠN
# Đặt giá MUA = 9,999 (bằng best_bid)
Order("RAINFOREST_RESIN", 9999, 5)
# → Chưa khớp — lệnh của bạn nằm trên order book
# → Chờ đến khi có ai đó bán giá 9,999 hoặc rẻ hơn
# → Nhưng nhớ: lệnh hết hạn cuối tick!
```

> **Ví dụ thực tế:**
> - **Aggressive** giống như bạn đến chợ và nói: "Tôi lấy, tôi trả giá bạn nói." Bạn có hàng ngay nhưng có thể trả đắt.
> - **Passive** giống như bạn ghi giá lên bảng: "Tôi muốn mua giá này." Rồi bạn ngồi chờ. Có thể được giá tốt hơn, nhưng cũng có thể không ai bán cho bạn.

> **Vừa xảy ra gì?** Trong Prosperity, bạn chỉ dùng Limit Order. Nếu bạn đặt giá "tốt" (mua cao, bán thấp) thì khớp ngay (aggressive). Nếu đặt giá "chờ" (mua thấp, bán cao) thì nằm trên book chờ (passive). Mỗi lệnh chỉ tồn tại trong 1 tick.

---

## 6. Order Matching — Cách khớp lệnh

### Quy tắc ưu tiên: Giá trước, Thời gian sau

Khi có nhiều lệnh trên order book, hệ thống khớp theo thứ tự nào? IMC dùng quy tắc **Price-Time Priority** (Ưu tiên giá-thời gian):

**Bước 1 — Giá tốt nhất trước:**
- Nếu bạn gửi lệnh BÁN, hệ thống tìm người MUA trả giá CAO NHẤT trước
- Nếu bạn gửi lệnh MUA, hệ thống tìm người BÁN giá THẤP NHẤT trước
- Lý do: bạn muốn được giá tốt nhất có thể!

**Bước 2 — Cùng giá thì ai đến trước được trước (FIFO):**
- Nếu 2 lệnh cùng giá, lệnh nào đến trước được khớp trước
- Giống như xếp hàng mua vé xem phim — ai đến trước mua trước

### Ví dụ cụ thể

Giả sử trên order book có các lệnh MUA sau:
```
Lệnh A: MUA 10 cái giá 9,999 (đến trước)
Lệnh B: MUA  5 cái giá 10,000
Lệnh C: MUA  8 cái giá 9,999 (đến sau lệnh A)
```

Bây giờ bạn gửi lệnh BÁN 20 cái giá 9,998. Chuyện gì xảy ra?

```
Bước 1: Khớp với Lệnh B (giá 10,000 — cao nhất, tốt nhất cho bạn)
         → Bạn bán 5 cái giá 10,000
         → Còn lại: 20 - 5 = 15 cái cần bán

Bước 2: Khớp với Lệnh A (giá 9,999, đến trước Lệnh C)
         → Bạn bán 10 cái giá 9,999
         → Còn lại: 15 - 10 = 5 cái cần bán

Bước 3: Khớp với Lệnh C (giá 9,999, đến sau Lệnh A)
         → Bạn bán 5 cái giá 9,999
         → Còn lại: 0 — đã khớp hết!

Kết quả: Lệnh C còn 3 cái chưa khớp (8 - 5 = 3)
```

> **Lưu ý:** Bạn bán giá 9,998 nhưng được khớp tại giá 10,000 và 9,999 — **giá tốt hơn** mong đợi! Trong Prosperity, bạn luôn được giá **tốt nhất có thể**.

### Khớp một phần (Partial Fill)

Nếu lệnh của bạn lớn hơn số lượng có sẵn, chỉ một phần được khớp. Phần còn lại **không được giữ lại** — nó biến mất cuối tick.

```python
# Bạn gửi lệnh mua 20 cái giá 10,001
# Nhưng chỉ có 10 cái đang bán giá 10,001
# → Chỉ 10 cái được khớp
# → 10 cái còn lại MẤT (không chuyển sang tick sau)
```

### Trong Prosperity

- Tất cả lệnh của bot bạn trong 1 tick được xử lý cùng lúc
- Lệnh **không chuyển sang tick sau** — mỗi tick bắt đầu từ trắng (fresh)
- Nếu lệnh không khớp hết trong tick này, phần còn lại bị hủy

> **Ví dụ thực tế:** Giống như đấu giá. Người trả giá cao nhất thắng. Nếu 2 người trả cùng giá, ai giơ tay trước thắng. Và nếu bạn muốn mua 10 cái nhưng chỉ có 5, bạn chỉ mua được 5 — không có chuyện "để dành" 5 cái còn lại cho lần sau.

> **Vừa xảy ra gì?** Hệ thống khớp lệnh dùng quy tắc: giá tốt nhất trước, cùng giá thì ai đến trước. Lệnh có thể khớp một phần. Trong Prosperity, mỗi lệnh chỉ tồn tại 1 tick — chưa khớp thì mất.

---

# PHẦN 3: HỆ THỐNG MÔ PHỎNG

---

## 7. Tick — Đơn vị thời gian

### Prosperity không chạy theo thời gian thực

Trong giao dịch thật, mọi thứ xảy ra liên tục — giá thay đổi mỗi giây, mỗi mili-giây. Nhưng trong Prosperity, thời gian được chia thành các **bước rời rạc** gọi là **tick**.

Hãy nghĩ như thế này: xem phim là thời gian liên tục. Nhưng **flipbook** (sách lật) thì là từng khung hình — mỗi khung hình là 1 bước. Prosperity giống như flipbook — mỗi "trang" là 1 tick.

### Cách tick hoạt động

```
Tick 100  →  Tick 200  →  Tick 300  →  ...  →  Tick 999,900  →  Tick 1,000,000
   │            │            │
   │            │            └── Hệ thống gọi run() lần 3
   │            └── Hệ thống gọi run() lần 2
   └── Hệ thống gọi run() lần 1
```

- **Timestamp tăng 100 mỗi tick:** 100, 200, 300, 400...
- Mỗi tick, hệ thống gọi hàm `run()` của bạn 1 lần
- Bạn nhận thông tin thị trường **tại thời điểm đó** và trả về lệnh
- **Khoảng 10,000 tick** mỗi ngày giao dịch trong mô phỏng cuối

### Mỗi tick là một "thế giới mới"

Đây là điều quan trọng: **lệnh từ tick trước không tồn tại ở tick sau**. Mỗi tick, bot của bạn bắt đầu từ trắng:

```
Tick 100:
  - Bạn đặt lệnh mua 10 cái giá 9,999
  - Chỉ 5 cái được khớp
  - 5 cái còn lại → BIẾN MẤT

Tick 200:
  - Lệnh từ tick 100 đã KHÔNG CÒN
  - Bạn phải đặt lệnh mới nếu muốn mua tiếp
  - Bot của bạn "thức dậy" với trạng thái mới
```

> **Ví dụ:** Giống như trò chơi Groundhog Day (phim Mỹ). Mỗi sáng bot của bạn thức dậy, không nhớ gì từ hôm qua. Nó chỉ biết những gì ghi trong `traderData` (giống như ghi chú để trên bàn).

### Tốc độ xử lý

Bot của bạn phải trả về kết quả **nhanh**. Nếu code của bạn chạy quá lâu, bạn có thể bị phạt hoặc bỏ qua. Viết code đơn giản, hiệu quả.

> **Vừa xảy ra gì?** Thời gian trong Prosperity chia thành các bước gọi là tick. Mỗi tick, bot nhận thông tin mới, đặt lệnh mới. Lệnh cũ biến mất. Bot không có bộ nhớ tự nhiên giữa các tick.

---

## 8. TradingState — Gói thông tin mỗi tick

### Hệ thống gửi gì cho bot bạn?

Mỗi tick, trước khi bot bạn quyết định, hệ thống "gửi" cho bạn một gói thông tin gọi là `TradingState`. Gói này chứa **mọi thứ bạn cần biết** về thị trường tại thời điểm đó.

Hãy tưởng tượng bạn là giám đốc một công ty. Mỗi sáng, trợ lý gửi cho bạn một **báo cáo tổng hợp**: giá thị trường, hàng tồn kho, giao dịch hôm qua, ghi chú của bạn từ hôm trước. Đó chính là `TradingState`.

### Cấu trúc TradingState

```python
def run(self, state: TradingState):
    # state chứa những gì?

    state.timestamp
    # Số tick hiện tại: 100, 200, 300...
    # Giống như đồng hồ của thị trường

    state.order_depths
    # Order book của tất cả sản phẩm
    # Là một dictionary: {"RAINFOREST_RESIN": OrderDepth(...), "KELP": OrderDepth(...)}
    # Đây là thông tin quan trọng nhất — cho bạn biết ai đang mua/bán gì

    state.position
    # Vị thế (hàng tồn kho) của bạn
    # Là một dictionary: {"RAINFOREST_RESIN": 25, "KELP": -10}
    # Dương = bạn đang giữ, Âm = bạn đang nợ
    # Nếu sản phẩm chưa có, nó KHÔNG có trong dict này (cần dùng .get()!)

    state.traderData
    # Chuỗi ký tự bạn gửi từ tick trước
    # Đây là "ghi chú" duy nhất bạn có thể để lại cho mình
    # Tick đầu tiên: đây là chuỗi rỗng ""

    state.market_trades
    # Giao dịch của CÁC BOT KHÁC từ tick trước
    # {"KELP": [Trade(symbol, price, quantity, buyer, seller, timestamp), ...]}
    # Giúp bạn biết "ai mua gì, giá bao nhiêu"

    state.own_trades
    # Giao dịch CỦA BẠN từ tick trước
    # Giống market_trades nhưng chỉ là lệnh của bạn đã khớp

    state.observations
    # Dữ liệu bên ngoài (dùng ở các round sau)
    # Ví dụ: giá từ sàn giao dịch khác, dữ liệu kinh tế
```

### Đọc position an toàn

Đây là lỗi rất phổ biến: nếu bạn chưa giao dịch sản phẩm nào, nó **không có** trong `state.position`. Nếu bạn truy cập trực tiếp, sẽ bị **KeyError**!

```python
# ======================================
# SAI — sẽ bị lỗi nếu chưa có vị thế!
# ======================================
pos = state.position["RAINFOREST_RESIN"]
# KeyError: 'RAINFOREST_RESIN'   ← LỖI!

# ======================================
# ĐÚNG — dùng .get() với giá trị mặc định
# ======================================
pos = state.position.get("RAINFOREST_RESIN", 0)
# Nếu có vị thế → trả về vị thế (vd: 25)
# Nếu chưa có → trả về 0
```

### Ý nghĩa của position

```python
pos = state.position.get("RAINFOREST_RESIN", 0)

# pos = 25  → Bạn đang GIỮ 25 cái (long)
#             Giống như bạn có 25 quả xoài trong kho

# pos = 0   → Không giữ gì cả
#             Kho trống

# pos = -15 → Bạn đang NỢ 15 cái (short)
#             Giống như bạn đã bán 15 quả xoài mà chưa có
#             → Cần mua lại 15 quả để trả nợ
```

> **Ví dụ thực tế:** Nghĩ như quản lý kho hàng:
> - **Dương:** Bạn có hàng trong kho → muốn bán để kiếm lời
> - **Không:** Kho trống → tự do mua hoặc bán
> - **Âm:** Bạn đã "mượn" hàng và bán rồi → cần mua lại để trả

### Xem market_trades để học từ bot khác

```python
# Ai đã giao dịch KELP ở tick trước?
if "KELP" in state.market_trades:
    for trade in state.market_trades["KELP"]:
        print(f"  {trade.buyer} mua từ {trade.seller}")
        print(f"  Giá: {trade.price}, Số lượng: {trade.quantity}")
        # Ví dụ: "Olivia mua từ Bot_A, Giá 2050, Số lượng 5"
        # → Olivia là "informed trader" — có thể theo dõi cô ấy!
```

> **Vừa xảy ra gì?** Mỗi tick, bot bạn nhận một TradingState chứa: order book, vị thế, ghi chú từ tick trước, giao dịch của người khác, và giao dịch của bạn. Dùng `.get("PRODUCT", 0)` để đọc position an toàn.

---

## 9. Position Limit — Giới hạn vị thế

### Bạn không thể mua/bán vô hạn

Trong thế giới thật, nếu bạn có nhiều tiền, bạn có thể mua bao nhiêu tùy thích. Nhưng trong Prosperity, mỗi sản phẩm có **giới hạn vị thế (position limit)** — bạn chỉ được giữ tối đa ±N đơn vị.

### Giống như sức chứa của kho

Hãy tưởng tượng bạn có một cái kho chứa được **50 quả xoài**:
- Bạn có thể chứa **tối đa 50** quả (long +50)
- Bạn cũng có thể "nợ" **tối đa 50** quả (short -50)
- Tổng cộng phạm vi là -50 đến +50

```
         Position Limit = 50
  ←───────────────┼───────────────→
  -50            0             +50
  (nợ tối đa)   (trống)    (đầy kho)
```

### Giới hạn cho các sản phẩm

| Sản phẩm | Giới hạn |
|----------|----------|
| RAINFOREST_RESIN | ±50 |
| KELP | ±50 |
| SQUID_INK | ±50 |
| (sản phẩm khác) | Kiểm tra đề bài mỗi round |

> **Lưu ý:** Giới hạn có thể thay đổi giữa các round và các sản phẩm. Luôn đọc đề bài kỹ!

### Tính "còn chỗ" (remaining capacity)

Trước khi đặt lệnh, bạn phải biết mình còn mua/bán được bao nhiêu:

```python
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)  # Ví dụ: pos = 20

# Bạn đã giữ 20 cái, giới hạn 50
# Còn mua được: 50 - 20 = 30 cái
max_buy = LIMIT - pos     # 50 - 20 = 30

# Còn bán được: 50 + 20 = 70?? Không, max là 50!
# Nhưng thực ra, nếu pos = 20, bạn có thể bán 20 (để về 0) + bán khống 50 = 70
# → Nhưng giới hạn vị thế là ±50, nên:
max_sell = LIMIT + pos    # 50 + 20 = 70 → nhưng thực sự bán được 70?
# ĐÚNG! Vì bạn đang ở +20, bạn có thể đi từ +20 xuống -50 = 70 bước
```

**Giải thích chi tiết:**

```
Hiện tại: pos = +20

  -50 ......... 0 ......... +20 ....... +50
                              ^-- Bạn đang đây

  ← max_sell = 70 →          ← max_buy = 30 →
  (đi từ +20 đến -50 = 70)   (đi từ +20 đến +50 = 30)
```

Một ví dụ khác với pos = -15:

```
Hiện tại: pos = -15

  -50 ... -15 ......... 0 ......... +50
              ^-- Bạn đang đây

  ← max_sell = 35 →    ← max_buy = 65 →
  (đi từ -15 đến -50)  (đi từ -15 đến +50)
  LIMIT + pos           LIMIT - pos
  50 + (-15) = 35      50 - (-15) = 65
```

### Hệ thống KHÔNG báo lỗi!

Đây là điều nguy hiểm: nếu bạn đặt lệnh vượt quá giới hạn, IMC **âm thầm từ chối** lệnh của bạn. Không có thông báo lỗi, không có cảnh báo. Lệnh đơn giản là không được thực thi.

```python
# Ví dụ: pos = 45, LIMIT = 50
# Bạn đặt lệnh mua 10 cái
Order("RAINFOREST_RESIN", 9999, 10)
# Chỉ được mua 5 cái (50 - 45 = 5)
# 5 cái còn lại bị TỪ CHỐI ÂM THẦM
# Bạn sẽ không biết tại sao lệnh không khớp hết!
```

### QUAN TRỌNG: Cập nhật capacity sau mỗi lệnh!

Nếu bạn đặt nhiều lệnh trong cùng 1 tick, bạn phải tự tính lại capacity sau mỗi lệnh:

```python
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)  # pos = 30
orders = []

# Lệnh 1: Mua 10 cái giá 9,998
buy_amount_1 = 10
max_buy = LIMIT - pos                             # 50 - 30 = 20, đủ!
orders.append(Order("RAINFOREST_RESIN", 9998, buy_amount_1))
pos += buy_amount_1                                # Cập nhật: pos = 40

# Lệnh 2: Mua 15 cái giá 9,999
buy_amount_2 = 15
max_buy = LIMIT - pos                             # 50 - 40 = 10, không đủ 15!
buy_amount_2 = min(buy_amount_2, max_buy)          # → chỉ mua 10
orders.append(Order("RAINFOREST_RESIN", 9999, buy_amount_2))
pos += buy_amount_2                                # Cập nhật: pos = 50 (đầy!)

# Lệnh 3: Mua thêm?
max_buy = LIMIT - pos                             # 50 - 50 = 0 → không mua được nữa!
```

> **Ví dụ thực tế:** Giống như kho hàng có sức chứa 50. Bạn đặt mua 3 lô hàng khác nhau. Sau mỗi lô hàng, bạn phải kiểm tra kho còn bao nhiêu chỗ. Nếu không, lô hàng thứ 3 có thể không vào được kho — và bạn mất tiền vận chuyển!

> **Vừa xảy ra gì?** Mỗi sản phẩm có giới hạn vị thế (vd ±50). Bạn phải tự tính còn mua/bán được bao nhiêu. Hệ thống không báo lỗi khi vượt giới hạn — lệnh bị từ chối âm thầm. Luôn cập nhật capacity sau mỗi lệnh.

---

## 10. Hàm run() — Trái tim của bot

### Cấu trúc bắt buộc

Bot của bạn PHẢI có dạng này:

```python
# ================================================
# CÁC IMPORT CẦN THIẾT
# ================================================
from datamodel import OrderDepth, TradingState, Order
from typing import List
import json  # Nếu bạn dùng traderData dạng JSON

# ================================================
# CLASS TRADER — PHẢI TÊN LÀ "Trader"
# ================================================
class Trader:

    # ================================================
    # HÀM run() — HỆ THỐNG GỌI HÀM NÀY MỖI TICK
    # ================================================
    def run(self, state: TradingState):

        # 1. Tạo dict chứa lệnh cho từng sản phẩm
        result = {}
        # result sẽ có dạng: {"RAINFOREST_RESIN": [Order(...), Order(...)]}

        # 2. Conversions — dùng ở round sau
        conversions = 1
        # Round 1: để là 1
        # Round 2+: liên quan đến chuyển đổi sản phẩm (xem hướng dẫn round cụ thể)

        # 3. traderData — ghi chú gửi sang tick sau
        traderData = ""
        # Bạn có thể ghi bất kỳ chuỗi nào (tối đa 50,000 ký tự)

        # ==========================================
        # LOGIC GIAO DỊCH CỦA BẠN Ở ĐÂY
        # ==========================================

        # Ví dụ: đọc order book của RAINFOREST_RESIN
        if "RAINFOREST_RESIN" in state.order_depths:
            order_depth = state.order_depths["RAINFOREST_RESIN"]
            orders = []

            # ... logic quyết định mua/bán ...

            result["RAINFOREST_RESIN"] = orders

        # ==========================================
        # TRẢ VỀ KẾT QUẢ — PHẢI ĐÚNG 3 GIÁ TRỊ
        # ==========================================
        return result, conversions, traderData
```

### Giải thích từng phần

**`result` — Lệnh của bạn:**
```python
result = {}

# Thêm lệnh cho RAINFOREST_RESIN
result["RAINFOREST_RESIN"] = [
    Order("RAINFOREST_RESIN", 9998, 5),    # Mua 5 cái giá 9,998
    Order("RAINFOREST_RESIN", 10002, -3),   # Bán 3 cái giá 10,002
]

# Thêm lệnh cho KELP
result["KELP"] = [
    Order("KELP", 2048, 10),               # Mua 10 cái KELP giá 2,048
]

# Sản phẩm không có lệnh? Không cần thêm vào result
```

**`conversions` — Chuyển đổi:**
```python
conversions = 1    # Round 1: để là 1, không ảnh hưởng gì
                   # Round 2+: số lượng chuyển đổi (xem hướng dẫn round)
```

**`traderData` — Ghi chú:**
```python
# Chuỗi gì cũng được, miễn là không quá 50,000 ký tự
traderData = "hello"                           # Đơn giản
traderData = str(10000.5)                      # Lưu 1 số
traderData = json.dumps({"price": 10000.5})    # Lưu nhiều dữ liệu
```

### Quy tắc bắt buộc

1. **Class phải tên là `Trader`** — không phải `MyBot`, không phải `Algorithm`
2. **Hàm phải tên là `run`** — không phải `trade`, không phải `execute`
3. **Phải trả về ĐÚNG 3 giá trị:** `result, conversions, traderData`
   - Thiếu 1 giá trị → LỖI
   - Thừa 1 giá trị → LỖI
4. **result là dict** — key là tên sản phẩm (string), value là list của Order
5. **Mỗi Order phải đúng tên sản phẩm:** `Order("RAINFOREST_RESIN", price, qty)` — không được viết sai tên

### Ví dụ bot đơn giản nhất

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:
    def run(self, state: TradingState):
        result = {}

        # Bot này chỉ làm 1 việc: mua RAINFOREST_RESIN giá 9,995
        orders = []
        orders.append(Order("RAINFOREST_RESIN", 9995, 1))  # Mua 1 cái
        result["RAINFOREST_RESIN"] = orders

        return result, 1, ""
```

Bot này rất ngu — nó chỉ mua mà không bao giờ bán, và sẽ nhanh chóng đạt giới hạn. Nhưng nó cho thấy cấu trúc cơ bản!

> **Vừa xảy ra gì?** Hàm run() là nơi bạn viết logic giao dịch. Hệ thống gọi nó mỗi tick. Bạn PHẢI trả về 3 giá trị: result (dict chứa lệnh), conversions (số), và traderData (chuỗi). Class phải tên Trader, hàm phải tên run.

---

## 11. traderData — Bộ nhớ giữa các tick

### Vấn đề: Bot mất trí nhớ

Như đã nói ở phần Tick, bot của bạn **hoàn toàn bị reset** sau mỗi tick. Giống như bạn bị mất trí nhớ mỗi 100ms. Bạn không nhớ giá tick trước, không nhớ đã giao dịch gì, không nhớ gì cả.

Nhưng để giao dịch thông minh, bạn CẦN thông tin từ quá khứ! Ví dụ:
- Giá trung bình 20 tick gần nhất (để tính EMA)
- Bạn đã mua/bán bao nhiêu lần hôm nay
- Xu hướng giá đang tăng hay giảm

### Giải pháp: traderData

`traderData` là một **chuỗi ký tự (string)** mà bạn gửi ở cuối tick này, và nhận lại ở đầu tick sau.

```
Tick 100:
  state.traderData = ""          ← Tick đầu tiên, chuỗi rỗng
  ... logic ...
  return result, 1, "my_note"   ← Gửi "my_note" sang tick sau

Tick 200:
  state.traderData = "my_note"   ← Nhận lại "my_note" từ tick 100!
  ... logic ...
  return result, 1, "new_note"  ← Gửi "new_note" sang tick 300

Tick 300:
  state.traderData = "new_note"  ← Nhận lại "new_note" từ tick 200!
```

### Ví dụ đơn giản: Lưu 1 số

```python
class Trader:
    def run(self, state: TradingState):
        result = {}

        # Đọc giá từ tick trước
        if state.traderData:
            # Có dữ liệu từ tick trước
            last_mid_price = float(state.traderData)
            print(f"Giá mid tick trước: {last_mid_price}")
        else:
            # Tick đầu tiên — chưa có dữ liệu
            last_mid_price = None
            print("Tick đầu tiên, chưa có dữ liệu")

        # Tính mid price hiện tại
        od = state.order_depths["RAINFOREST_RESIN"]
        best_ask = min(od.sell_orders.keys())
        best_bid = max(od.buy_orders.keys())
        current_mid = (best_ask + best_bid) / 2

        # Lưu mid price để tick sau đọc
        traderData = str(current_mid)   # Ví dụ: "10000.5"

        return result, 1, traderData
```

### Ví dụ nâng cao: Lưu nhiều dữ liệu với JSON

Khi bạn cần lưu nhiều thông tin, dùng JSON:

```python
import json

class Trader:
    def run(self, state: TradingState):
        result = {}

        # =============================================
        # ĐỌC dữ liệu từ tick trước
        # =============================================
        if state.traderData:
            data = json.loads(state.traderData)
            # data là 1 dictionary Python
        else:
            # Tick đầu tiên — khởi tạo dữ liệu trống
            data = {
                "prices": [],         # Lưu lịch sử giá
                "trade_count": 0,     # Đếm số giao dịch
                "last_action": None   # Hành động cuối
            }

        # =============================================
        # CẬP NHẬT dữ liệu với thông tin tick này
        # =============================================
        od = state.order_depths["RAINFOREST_RESIN"]
        best_ask = min(od.sell_orders.keys())
        best_bid = max(od.buy_orders.keys())
        current_mid = (best_ask + best_bid) / 2

        # Thêm giá hiện tại vào danh sách
        data["prices"].append(current_mid)

        # Chỉ giữ 20 giá gần nhất (tiết kiệm bộ nhớ)
        if len(data["prices"]) > 20:
            data["prices"] = data["prices"][-20:]

        # Tính EMA nếu có đủ dữ liệu
        if len(data["prices"]) >= 5:
            ema = sum(data["prices"][-5:]) / 5  # Trung bình 5 giá gần nhất
            print(f"EMA(5): {ema}")

        # =============================================
        # GỬI dữ liệu sang tick sau
        # =============================================
        traderData = json.dumps(data)
        # Ví dụ: '{"prices": [10000, 10001, 9999], "trade_count": 0, "last_action": null}'

        return result, 1, traderData
```

### Giới hạn: 50,000 ký tự

Trong Prosperity 4, traderData **tối đa 50,000 ký tự**. Nghe nhiều nhưng có thể hết nhanh nếu bạn lưu nhiều dữ liệu:

```python
# Ví dụ: mỗi số chiếm khoảng 7-10 ký tự
# 50,000 / 10 = khoảng 5,000 số
# → Đủ cho 5,000 giá lịch sử, hoặc 250 giá x 20 sản phẩm

# Mẹo tiết kiệm:
# 1. Chỉ giữ N giá gần nhất (không lưu hết)
# 2. Làm tròn số (10000.12345 → 10000.1)
# 3. Dùng key ngắn ("p" thay vì "prices")
```

### Frankfurt Hedgehogs dùng traderData như thế nào?

Họ lưu: giá EMA của mỗi sản phẩm, thông tin của các trader (ai mua gì), premium của ETF, và nhiều thông tin chiến lược khác — tất cả dưới dạng JSON.

> **Ví dụ thực tế:** Giống như bạn bị mất trí nhớ mỗi ngày. Trước khi ngủ, bạn viết 1 tờ giấy ghi lại những gì quan trọng: "Giá xoài hôm nay 20k, đã bán 50 quả, khách tên Olivia hay mua nhiều." Sáng hôm sau, bạn đọc tờ giấy và biết mình cần làm gì. traderData chính là tờ giấy đó.

> **Vừa xảy ra gì?** traderData là cách duy nhất để bot "nhớ" thông tin giữa các tick. Nó là 1 chuỗi ký tự bạn gửi cuối tick này và nhận đầu tick sau. Dùng JSON để lưu nhiều dữ liệu. Tối đa 50,000 ký tự trong Prosperity 4.

---

# PHẦN 4: LỘ TRÌNH HỌC

---

## 12. Lộ trình Round 1 đến Round 5

### Tổng quan các round

```
Round 1: Market Making (Tạo lập thị trường)
├── RAINFOREST_RESIN  ← Giá trị cố định = 10,000
│   └── Kiểu: Giá ổn định, ít thay đổi
│   └── Chiến lược: Mua dưới 10,000, bán trên 10,000
│
├── KELP              ← Giá thay đổi chậm (random walk)
│   └── Kiểu: Giá đi "lang thang" lên xuống nhẹ
│   └── Chiến lược: Tính EMA để theo dõi giá trị thật
│
└── SQUID_INK         ← Giá biến động lớn, có "informed trader" (Olivia)
    └── Kiểu: Giá nhảy nhiều, khó đoán
    └── Chiến lược: Theo dõi Olivia và các trader khác

Round 2: ETF Statistical Arbitrage (Chênh lệch giá rổ hàng)
├── PICNIC_BASKET1 = 6 x Croissants + 3 x Jams + 1 x Djembes
├── PICNIC_BASKET2 = 4 x Croissants + 2 x Jams
└── Chiến lược: Giá basket dao động quanh tổng giá thành phần
    └── Khi basket đắt hơn thành phần → bán basket, mua thành phần
    └── Khi basket rẻ hơn thành phần → mua basket, bán thành phần

Round 3: Options (Quyền chọn)
├── VOLCANIC_ROCK (tài sản cơ sở)
├── VOLCANIC_ROCK_VOUCHER (quyền chọn mua — call options, 5 giá thực hiện)
└── Chiến lược: IV scalping + mean reversion
    └── Cần hiểu Black-Scholes, implied volatility, delta

Round 4: Location Arbitrage (Chênh lệch giá giữa các sàn)
├── MAGNIFICENT_MACARONS
└── Chiến lược: Mua từ sàn giao dịch bên ngoài → bán trên sàn nội bộ
    └── Dùng conversions và observations

Round 5: Trader IDs (Nhận diện trader)
└── Không có sản phẩm mới — tối ưu hóa tất cả chiến lược trước đó
    └── Market trades có thêm thông tin: ai mua/bán
    └── Dùng để nhận diện "informed traders" như Olivia
```

### Lộ trình học theo bước

Đây là thứ tự học đề nghị — từ dễ đến khó:

| Bước | Khái niệm cần học | Dùng cho |
|------|-------------------|----------|
| 1 | Order book, taking, position limit | RAINFOREST_RESIN cơ bản |
| 2 | Wall mid, making, overbidding | RAINFOREST_RESIN nâng cao |
| 3 | Giá trị động (EMA), traderData JSON | KELP |
| 4 | market_trades, nhận diện pattern | SQUID_INK |
| 5 | Giá tổng hợp, spread, mean reversion | Baskets (Round 2) |
| 6 | Black-Scholes, implied volatility, delta | Options (Round 3) |
| 7 | Conversion, external market, arbitrage | Macarons (Round 4) |

### Lời khuyên

1. **Bắt đầu từ RAINFOREST_RESIN** — sản phẩm dễ nhất vì giá cố định
2. **Làm tốt 1 sản phẩm trước khi qua sản phẩm tiếp** — đừng cố làm tất cả cùng lúc
3. **Đọc đề bài kỹ mỗi round** — luật và sản phẩm có thể thay đổi
4. **Test với backtester** trước khi nộp — đừng nộp code chưa test
5. **Xem log** sau mỗi lần nộp để hiểu bot làm gì sai

> **Vừa xảy ra gì?** Cuộc thi có 5 round, tăng dần độ khó. Bắt đầu với market making (mua thấp, bán cao), rồi qua statistical arbitrage, options, location arbitrage, và cuối cùng là tối ưu hóa với trader IDs.

---

# PHẦN 5: THAM KHẢO

---

## 13. Các lỗi thường gặp

### Lỗi 1: Quên abs() cho sell_orders

```python
# ======== SAI ========
od = state.order_depths["RAINFOREST_RESIN"]
best_ask = min(od.sell_orders.keys())
volume = od.sell_orders[best_ask]       # → -10 (SỐ ÂM!)
# Nếu bạn dùng volume này để đặt lệnh mua:
Order("RAINFOREST_RESIN", best_ask, volume)  # → Mua -10 = BÁN 10?! SAI!

# ======== ĐÚNG ========
volume = abs(od.sell_orders[best_ask])  # → 10 (SỐ DƯƠNG)
Order("RAINFOREST_RESIN", best_ask, volume)  # → Mua 10 cái. ĐÚNG!
```

**Tại sao xảy ra?** Sell orders trong IMC có volume âm theo quy ước. Người mới thường quên điều này.

### Lỗi 2: Không kiểm tra position limit trước khi đặt lệnh

```python
# ======== SAI ========
# Không kiểm tra giới hạn, đặt mua 30 cái
orders.append(Order("RAINFOREST_RESIN", 9998, 30))
# Nếu pos đã là 40 và LIMIT = 50 → chỉ mua được 10, 20 cái bị từ chối!

# ======== ĐÚNG ========
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)
max_buy = LIMIT - pos
buy_amount = min(30, max_buy)  # Đảm bảo không vượt giới hạn
if buy_amount > 0:
    orders.append(Order("RAINFOREST_RESIN", 9998, buy_amount))
```

**Tại sao xảy ra?** Hệ thống không báo lỗi, nên bạn không biết lệnh bị từ chối.

### Lỗi 3: Quên dấu âm cho lệnh bán

```python
# ======== SAI ========
Order("RAINFOREST_RESIN", 10002, 5)    # Quantity DƯƠNG = MUA, không phải BÁN!

# ======== ĐÚNG ========
Order("RAINFOREST_RESIN", 10002, -5)   # Quantity ÂM = BÁN. Đúng!
```

**Tại sao xảy ra?** Quen reflex ghi số dương. Cần nhớ: âm = bán.

### Lỗi 4: Không dùng .get() cho position

```python
# ======== SAI ========
pos = state.position["KELP"]           # KeyError nếu chưa giao dịch KELP!

# ======== ĐÚNG ========
pos = state.position.get("KELP", 0)    # Trả về 0 nếu chưa có
```

**Tại sao xảy ra?** Tick đầu tiên hoặc nếu bạn chưa giao dịch sản phẩm đó, position không có key đó.

### Lỗi 5: Trả về sai số lượng giá trị từ run()

```python
# ======== SAI — trả về 2 giá trị ========
return result, traderData
# TypeError: Phải trả về 3 giá trị!

# ======== SAI — trả về 4 giá trị ========
return result, conversions, traderData, extra_data
# TypeError: Trả về nhiều quá!

# ======== ĐÚNG — trả về đúng 3 giá trị ========
return result, conversions, traderData
# result: dict, conversions: int, traderData: str
```

### Lỗi 6: Không cập nhật capacity sau mỗi lệnh trong cùng tick

```python
# ======== SAI ========
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)  # pos = 40
orders = []

# Lệnh 1: Mua 8 cái
orders.append(Order("RAINFOREST_RESIN", 9998, 8))
# pos VẪN LÀ 40 trong code — chưa cập nhật!

# Lệnh 2: Mua 8 cái nữa
max_buy = LIMIT - pos  # 50 - 40 = 10, tưởng được
orders.append(Order("RAINFOREST_RESIN", 9999, 8))
# TỔNG = 16 cái! Nhưng chỉ mua được 10 (50 - 40)
# → 6 cái bị từ chối âm thầm!

# ======== ĐÚNG ========
LIMIT = 50
pos = state.position.get("RAINFOREST_RESIN", 0)  # pos = 40
orders = []

# Lệnh 1: Mua 8 cái
buy1 = min(8, LIMIT - pos)  # min(8, 10) = 8
orders.append(Order("RAINFOREST_RESIN", 9998, buy1))
pos += buy1                  # CẬP NHẬT! pos = 48

# Lệnh 2: Mua 8 cái nữa
buy2 = min(8, LIMIT - pos)  # min(8, 2) = 2 — chỉ còn 2 chỗ!
if buy2 > 0:
    orders.append(Order("RAINFOREST_RESIN", 9999, buy2))
    pos += buy2              # CẬP NHẬT! pos = 50
```

---

## 14. Checklist trước khi nộp bài

Trước khi nộp file Python, hãy kiểm tra tất cả các mục sau:

### Cấu trúc cơ bản
- [ ] Class tên là `Trader` (không phải tên khác)
- [ ] Hàm tên là `run` (không phải tên khác)
- [ ] `run()` trả về **đúng 3 giá trị:** `result, conversions, traderData`
- [ ] Tất cả import cần thiết đều có (`from datamodel import ...`)

### Xử lý dữ liệu
- [ ] Dùng `abs()` khi đọc volume từ `sell_orders`
- [ ] Dùng `.get("PRODUCT", 0)` khi đọc `state.position`
- [ ] Xử lý trường hợp `state.traderData` rỗng (tick đầu tiên)

### Position limit
- [ ] Kiểm tra position limit trước khi đặt lệnh
- [ ] Cập nhật capacity sau **mỗi** lệnh trong cùng tick
- [ ] Lệnh bán có quantity **âm** (`-5`, không phải `5`)

### traderData
- [ ] traderData là **string** (dùng `json.dumps()` nếu cần)
- [ ] Không vượt quá **50,000 ký tự**
- [ ] Xử lý `state.traderData` rỗng ở tick đầu tiên

### Code sạch
- [ ] Không có `input()` (không được nhập từ bàn phím)
- [ ] Không có `time.sleep()` (không được chờ)
- [ ] Không dùng thư viện bị cấm (kiểm tra đề bài)
- [ ] Đã test với backtester
- [ ] Xem log sau khi test — không có lỗi

### Prosperity 4 riêng
- [ ] (Round 2+) Có method `bid()` nếu dùng conversions
- [ ] traderData dưới 50,000 ký tự

> **Mẹo:** In checklist này ra và đánh dấu mỗi khi nộp bài!

---

## 15. Glossary / Từ điển thuật ngữ

| Tiếng Anh | Tiếng Việt | Ý nghĩa |
|------------|------------|---------|
| **Order Book** | Sổ lệnh | Tất cả các lệnh mua/bán đang chờ |
| **Bid** | Giá mua | Giá cao nhất mà người mua sẵn sàng trả |
| **Ask** | Giá bán | Giá thấp nhất mà người bán sẵn sàng chấp nhận |
| **Spread** | Chênh lệch | Khoảng cách giữa giá Ask và Bid |
| **Position** | Vị thế | Số lượng đơn vị bạn đang nắm giữ |
| **Long** | Giữ hàng | Vị thế dương (position > 0) — bạn đang sở hữu |
| **Short** | Nợ hàng | Vị thế âm (position < 0) — bạn đang nợ |
| **Fill** | Khớp lệnh | Lệnh được thực thi thành công |
| **Fair Value** | Giá trị thật | Giá "đúng" ước tính của sản phẩm |
| **Wall Mid** | Giá tường trung bình | Trung bình của bid wall và ask wall |
| **Market Making** | Tạo lập thị trường | Đặt lệnh mua+bán quanh fair value để kiếm spread |
| **Taking** | Ăn lệnh | Đặt lệnh vượt qua spread để khớp ngay |
| **Making** | Đặt lệnh chờ | Đặt lệnh thụ động và chờ khớp |
| **Overbid** | Trả giá cao hơn | Lệnh mua cao hơn best bid hiện tại |
| **Undercut** | Bán giá thấp hơn | Lệnh bán thấp hơn best ask hiện tại |
| **PnL** | Lãi/Lỗ | Profit and Loss — lợi nhuận hoặc thua lỗ |
| **EMA** | Trung bình trượt | Exponential Moving Average — trung bình có trọng số |
| **Arbitrage** | Chênh lệch giá | Mua rẻ ở chỗ này, bán đắt ở chỗ khác |
| **Mean Reversion** | Hồi quy trung bình | Giá có xu hướng quay về mức trung bình |
| **Informed Trader** | Trader có thông tin | Bot biết trước tin (vd: Olivia trong Prosperity) |
| **XIRECs** | Đơn vị tiền tệ | Tiền tệ của Prosperity 4 |
| **SeaShells** | Tiền tệ cũ | Tiền tệ của Prosperity 3 |
| **Limit Order** | Lệnh giới hạn | Lệnh mua/bán tại 1 giá cụ thể hoặc tốt hơn |
| **Market Order** | Lệnh thị trường | Lệnh mua/bán ngay tại giá tốt nhất (KHÔNG dùng trong Prosperity) |
| **Price-Time Priority** | Ưu tiên giá-thời gian | Giá tốt nhất khớp trước, cùng giá thì ai đến trước |
| **Tick** | Đơn vị thời gian | 1 bước trong mô phỏng, timestamp tăng 100 |
| **Conversion** | Chuyển đổi | Đổi sản phẩm này lấy sản phẩm khác (Round 2+) |
| **Partial Fill** | Khớp 1 phần | Chỉ 1 phần lệnh được thực thi |
| **FIFO** | Vào trước ra trước | First In, First Out — ai đến trước được khớp trước |

---

*Based on IMC Prosperity 4 official documentation + Frankfurt Hedgehogs (Top 2, Prosperity 3)*
