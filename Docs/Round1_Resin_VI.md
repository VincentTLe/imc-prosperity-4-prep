# Round 1 — RAINFOREST_RESIN: Bot Giao Dịch Đầu Tiên Của Bạn

> **Yêu cầu trước khi đọc:** Bạn đã đọc xong General Guide (Order Book, Tick, TradingState, `run()`, v.v.).
> Nếu chưa, hãy đọc General_VI.md trước.

---

# PHẦN 1: HIỂU VỀ RESIN

---

## 1. RAINFOREST_RESIN là gì?

Trong Round 1 của IMC Prosperity 4, bạn sẽ giao dịch **3 sản phẩm**:

| Sản phẩm | Độ khó | Đặc điểm |
|----------|--------|----------|
| **RAINFOREST_RESIN** | Dễ nhất | Giá trị cố định = 10,000 |
| KELP | Trung bình | Giá trị thay đổi liên tục |
| SQUID_INK | Khó nhất | Giá trị dao động mạnh |

**RAINFOREST_RESIN** (gọi tắt là "Resin") là sản phẩm **DỄ NHẤT** để giao dịch. Tại sao? Vì giá trị thực của nó **LUÔN LUÔN** là **10,000 XIRECs**. Không bao giờ thay đổi. Không bao giờ.

Hãy nghĩ về nó như thế này:

> **Tưởng tượng bạn ở chợ vàng:**
>
> Có một thanh vàng mà **mọi người đều biết** giá trị là đúng 10,000 đồng. Giá này được khắc trên bảng lớn giữa chợ. Không ai tranh cãi.
>
> Nhưng trong chợ, có những người bán vội và cần tiền gấp — họ bán thanh vàng với giá 9,997 đồng (rẻ hơn 3 đồng).
> Và có những người mua nóng vội — họ sẵn sàng trả 10,003 đồng để mua ngay (đắt hơn 3 đồng).
>
> **Bạn là người thông minh đứng giữa:**
> - Thấy ai bán 9,997 → MUA ngay (rẻ hơn giá trị 3 đồng → lãi 3 đồng)
> - Thấy ai mua 10,003 → BÁN ngay (đắt hơn giá trị 3 đồng → lãi 3 đồng)
>
> Đó là toàn bộ chiến lược Resin. Thật sự chỉ có thế.

**Quy tắc vàng (Golden Rule):**

```
╔══════════════════════════════════════════════════╗
║                                                  ║
║   GIÁ TRỊ RESIN = 10,000 XIRECs (LUÔN LUÔN)    ║
║                                                  ║
║   → Mua DƯỚI 10,000 = LÃI                       ║
║   → Bán TRÊN 10,000 = LÃI                       ║
║   → Mua/Bán ĐÚNG 10,000 = Hòa vốn              ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

**Giới hạn vị thế (Position Limit): ±50 đơn vị**

Bạn chỉ được giữ tối đa **50 đơn vị** Resin tại bất kỳ thời điểm nào. Nghĩa là:
- Nhiều nhất: +50 (đang giữ 50 đơn vị — "long")
- Ít nhất: -50 (đang nợ 50 đơn vị — "short")

> **Ví dụ:** Nếu bạn đang giữ +30 Resin, bạn chỉ có thể mua thêm tối đa 20 đơn vị nữa (30 + 20 = 50).
> Nhưng bạn có thể bán tối đa 80 đơn vị (vì từ +30 bán 80 sẽ thành -50).

---

## 2. Tại sao Resin dễ nhất?

Hãy so sánh 3 sản phẩm:

```
RAINFOREST_RESIN:
  Giá trị: ──────────────────────── 10,000 ──────────────────────── (đường thẳng)

KELP:
  Giá trị: ~~~~/\~~~~\/~~~~~/\~~~~/\~~~~\/~~~~~  (sóng lên xuống nhẹ)

SQUID_INK:
  Giá trị: ~~~/\~~\/~~~~/\\/\~~~~~/\/\~~\//\~~~  (sóng lên xuống mạnh)
```

Với Resin, bạn **LUÔN BIẾT** giá trị thực là 10,000. Không cần tính toán, không cần dự đoán, không cần lo lắng. Chỉ cần:

1. Có ai bán dưới 10,000 không? → Mua
2. Có ai mua trên 10,000 không? → Bán

**Thật là đơn giản.**

Với KELP, giá trị thay đổi mỗi tick — bạn phải **tính toán** giá trị thực trước khi quyết định. Với SQUID_INK, giá trị nhảy nhót không thể đoán trước.

> **Quan trọng:** Đội Frankfurt Hedgehogs (xếp hạng #2 thế giới, Prosperity 3) kiếm được khoảng **~39,000 SeaShells/round** chỉ từ Resin. Resin "dễ" không có nghĩa là "ít tiền". Nó là nguồn thu nhập ổn định nhất của bạn.

---

# PHẦN 2: CHIẾN LƯỢC CƠ BẢN — AGGRESSIVE TAKING (LESSON 1)

---

## 3. Ý tưởng cốt lõi: Mua rẻ, Bán đắt

Đây là ý tưởng đơn giản nhất trong giao dịch:

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   Ai BÁN dưới 10,000 → MUA ngay (mua rẻ hơn giá trị)      ║
║   Ai MUA trên 10,000 → BÁN ngay (bán đắt hơn giá trị)     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

Hãy đi chậm hơn với một ví dụ đời thường:

> **Tưởng tượng bạn bán nước cam:**
>
> Bạn biết một ly nước cam đáng giá đúng **50,000 đồng**.
>
> **Tình huống 1:** Có người đến nói "Tôi bán ly nước cam này cho bạn với giá 48,000 đồng."
> → Bạn mua ngay! Vì bạn có thể bán lại với giá 50,000 và lãi 2,000 đồng.
>
> **Tình huống 2:** Có người đến nói "Tôi muốn mua nước cam, tôi trả 52,000 đồng."
> → Bạn bán ngay! Vì bạn có thể mua lại với giá 50,000, lãi 2,000 đồng.
>
> **Tình huống 3:** Có người nói "Tôi bán/mua với giá 50,000 đồng."
> → Không làm gì cả. Giá đúng bằng giá trị → không có lãi.

Trong Prosperity, "ly nước cam" là Resin, "50,000 đồng" là 10,000 XIRECs, và "những người mua bán" là các bot khác trong thị trường.

**Tại sao chiến lược này hoạt động?**

Vì thị trường Prosperity có các **bot market maker** — chúng luôn đặt lệnh mua/bán quanh giá 10,000. Đôi khi, chúng đặt lệnh ở giá không hoàn hảo (9,997 hoặc 10,003), tạo cơ hội cho bạn.

Ngoài ra, có các **bot taker** — chúng mua/bán với bất kỳ giá nào, đôi khi tạo ra những lệnh rất tốt cho bạn.

---

## 4. Code từng bước — Xây bot đầu tiên

Đây là phần quan trọng nhất. Chúng ta sẽ xây một bot giao dịch Resin **từ con số 0**, và tôi sẽ giải thích **TỪNG DÒNG** một cách chi tiết.

### Bot hoàn chỉnh:

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:
    def run(self, state: TradingState):
        result = {}

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            if product == "RAINFOREST_RESIN":
                # --- Cấu hình ---
                FAIR_VALUE = 10000
                LIMIT = 50

                # --- Bước 1: Đọc vị thế hiện tại ---
                current_pos = state.position.get(product, 0)
                max_buy = LIMIT - current_pos
                max_sell = LIMIT + current_pos

                # --- Bước 2: Kiểm tra bên bán (sell orders) ---
                if order_depth.sell_orders:
                    best_ask = min(order_depth.sell_orders.keys())
                    if best_ask < FAIR_VALUE:
                        volume = abs(order_depth.sell_orders[best_ask])
                        buy_amount = min(max_buy, volume)
                        if buy_amount > 0:
                            orders.append(Order(product, best_ask, buy_amount))
                            max_buy -= buy_amount

                # --- Bước 3: Kiểm tra bên mua (buy orders) ---
                if order_depth.buy_orders:
                    best_bid = max(order_depth.buy_orders.keys())
                    if best_bid > FAIR_VALUE:
                        volume = order_depth.buy_orders[best_bid]
                        sell_amount = min(max_sell, volume)
                        if sell_amount > 0:
                            orders.append(Order(product, best_bid, -sell_amount))
                            max_sell -= sell_amount

            result[product] = orders

        return result, 1, ""
```

### Giải thích CHI TIẾT từng dòng:

---

**Dòng 1-2: Import thư viện**

```python
from datamodel import OrderDepth, TradingState, Order
from typing import List
```

- `OrderDepth`: Chứa thông tin Order Book (ai đang mua/bán ở giá nào).
- `TradingState`: Chứa TOÀN BỘ thông tin thị trường tại thời điểm hiện tại (vị thế, order book, giao dịch gần đây, v.v.).
- `Order`: Dùng để tạo lệnh mua/bán của bạn.
- `List`: Kiểu dữ liệu danh sách (list) của Python.

> **Nếu bỏ dòng này?** Code sẽ báo lỗi vì Python không biết `OrderDepth`, `TradingState`, `Order` là gì.

---

**Dòng 4-5: Khai báo class Trader và hàm run()**

```python
class Trader:
    def run(self, state: TradingState):
```

- **BẮT BUỘC** phải có class tên là `Trader` với hàm `run()`.
- Hệ thống Prosperity gọi hàm `run()` mỗi tick (100 lần/giây) và truyền vào `state` — toàn bộ thông tin thị trường.
- `self` là tham số bắt buộc của mọi method trong class Python. Không cần quan tâm nhiều.

> **Nếu đổi tên class?** Hệ thống không tìm được bot của bạn → bot không chạy.

---

**Dòng 6: Tạo dictionary kết quả**

```python
        result = {}
```

`result` là một dictionary sẽ chứa tất cả lệnh của bạn cho TỪNG sản phẩm. Cuối cùng, bạn trả về `result` cho hệ thống.

Cấu trúc của `result`:
```python
result = {
    "RAINFOREST_RESIN": [Order(...), Order(...), ...],
    "KELP": [Order(...), ...],
    "SQUID_INK": [Order(...), ...]
}
```

> **Nếu quên tạo `result`?** Không có gì để trả về → bot không đặt lệnh nào.

---

**Dòng 8-10: Lặp qua từng sản phẩm**

```python
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
```

- `state.order_depths` là dictionary chứa Order Book của MỌI sản phẩm.
- `for product in state.order_depths:` lặp qua từng sản phẩm (RAINFOREST_RESIN, KELP, SQUID_INK).
- `order_depth` là Order Book của sản phẩm hiện tại. Nó chứa:
  - `order_depth.sell_orders`: Dictionary {giá: số_lượng_âm} — lệnh bán đang chờ
  - `order_depth.buy_orders`: Dictionary {giá: số_lượng_dương} — lệnh mua đang chờ
- `orders` là danh sách lệnh của bạn cho sản phẩm này (bắt đầu rỗng).

> **Ví dụ cụ thể:**
> ```python
> order_depth.sell_orders = {9997: -30, 10001: -20, 10002: -50}
> #  Giá 9997: có 30 đơn vị đang được bán (số âm = bán)
> #  Giá 10001: có 20 đơn vị đang được bán
> #  Giá 10002: có 50 đơn vị đang được bán
>
> order_depth.buy_orders = {9998: 50, 9999: 5, 10003: 15}
> #  Giá 9998: có người muốn mua 50 đơn vị (số dương = mua)
> #  Giá 9999: có người muốn mua 5 đơn vị
> #  Giá 10003: có người muốn mua 15 đơn vị
> ```

---

**Dòng 12-14: Chỉ xử lý Resin + Cấu hình**

```python
            if product == "RAINFOREST_RESIN":
                FAIR_VALUE = 10000
                LIMIT = 50
```

- `if product == "RAINFOREST_RESIN":` — chỉ áp dụng logic cho Resin (các sản phẩm khác cần chiến lược riêng).
- `FAIR_VALUE = 10000` — giá trị thực của Resin, LUÔN là 10,000.
- `LIMIT = 50` — giới hạn vị thế tối đa.

> **Tại sao dùng BIẾN HẰNG thay vì số?**
> Thay vì viết `10000` khắp nơi trong code, dùng `FAIR_VALUE` để:
> 1. Code dễ đọc hơn
> 2. Nếu cần thay đổi (ví dụ cho sản phẩm khác), chỉ sửa 1 chỗ
> 3. Tránh lỗi gõ sai số (9000 thay vì 10000)

---

**Dòng 16-18: Đọc vị thế hiện tại và tính giới hạn**

```python
                current_pos = state.position.get(product, 0)
                max_buy = LIMIT - current_pos
                max_sell = LIMIT + current_pos
```

Đây là phần **CỰC KỲ QUAN TRỌNG** — tính xem bạn còn được mua/bán bao nhiêu.

**`current_pos = state.position.get(product, 0)`**

- `state.position` là dictionary chứa số lượng bạn đang giữ cho mỗi sản phẩm.
- `.get(product, 0)` có nghĩa là: "Lấy vị thế của sản phẩm này. Nếu chưa có (chưa giao dịch lần nào), trả về 0."

**`max_buy = LIMIT - current_pos`**

Bạn được mua tối đa bao nhiêu? = Giới hạn - Vị thế hiện tại.

| current_pos | max_buy = 50 - pos | Giải thích |
|-------------|---------------------|------------|
| 0 | 50 | Chưa giữ gì → mua tối đa 50 |
| 10 | 40 | Đang giữ 10 → chỉ mua thêm 40 |
| 50 | 0 | Đầy rồi! Không mua được nữa |
| -20 | 70 | Đang short 20 → mua được 70 (từ -20 lên +50) |
| -50 | 100 | Đang short tối đa → mua được 100 (từ -50 lên +50) |

**`max_sell = LIMIT + current_pos`**

Bạn được bán tối đa bao nhiêu? = Giới hạn + Vị thế hiện tại.

| current_pos | max_sell = 50 + pos | Giải thích |
|-------------|----------------------|------------|
| 0 | 50 | Chưa giữ gì → bán tối đa 50 |
| 10 | 60 | Đang giữ 10 → bán được 60 (từ +10 xuống -50) |
| 50 | 100 | Đang long tối đa → bán được 100 (từ +50 xuống -50) |
| -20 | 30 | Đang short 20 → chỉ bán thêm 30 |
| -50 | 0 | Đầy rồi! Không bán được nữa |

> **Tại sao phải tính max_buy và max_sell?**
>
> Nếu bạn không tính và mua quá nhiều, hệ thống sẽ **TỰ ĐỘNG HỦY** lệnh vượt giới hạn.
> Tệ hơn nữa, lệnh bị hủy mà không có thông báo rõ ràng — bạn mất cơ hội mà không biết tại sao.
>
> **Tưởng tượng:** Bạn có một cái túi chỉ chứa được 50 trái cam. Hiện tại bạn đang chứa 30 trái.
> Nếu bạn cố mua 30 trái nữa (tổng 60), người bán hàng sẽ nói "Túi bạn không đủ chỗ" và không bán cho bạn.

---

**Dòng 20-27: Bước 2 — Kiểm tra bên bán (Tìm cơ hội MUA)**

```python
                if order_depth.sell_orders:
                    best_ask = min(order_depth.sell_orders.keys())
                    if best_ask < FAIR_VALUE:
                        volume = abs(order_depth.sell_orders[best_ask])
                        buy_amount = min(max_buy, volume)
                        if buy_amount > 0:
                            orders.append(Order(product, best_ask, buy_amount))
                            max_buy -= buy_amount
```

Đây là nơi bạn **TÌM CƠ HỘI MUA RẺ**.

**`if order_depth.sell_orders:`** — Kiểm tra có ai đang bán Resin không. Nếu order book trống (không ai bán), bỏ qua.

**`best_ask = min(order_depth.sell_orders.keys())`** — Tìm giá bán THẤP NHẤT. Đây là giá tốt nhất mà bạn có thể mua.

> **Ví dụ:** `sell_orders = {9997: -30, 10001: -20, 10002: -50}`
> `min(9997, 10001, 10002) = 9997` ← Giá bán thấp nhất là 9,997

**`if best_ask < FAIR_VALUE:`** — Giá bán thấp nhất có rẻ hơn 10,000 không?
- 9,997 < 10,000? **CÓ!** → Cơ hội mua!
- Nếu best_ask là 10,001 → 10,001 < 10,000? **KHÔNG** → Bỏ qua (mua sẽ lỗ).

**`volume = abs(order_depth.sell_orders[best_ask])`** — Lấy số lượng đang bán ở giá đó.

> **Tại sao `abs()`?** Vì `sell_orders` lưu số lượng dưới dạng **SỐ ÂM** (quy ước của Prosperity).
> Ví dụ: `sell_orders[9997] = -30` nghĩa là có 30 đơn vị đang bán. `abs(-30) = 30`.

**`buy_amount = min(max_buy, volume)`** — Mua bao nhiêu? Lấy số NHỎ HƠN giữa:
- Số lượng bạn có thể mua thêm (`max_buy`)
- Số lượng đang được bán (`volume`)

> **Ví dụ 1:** `max_buy = 40`, `volume = 30` → `min(40, 30) = 30` → Mua 30 (hết hàng bán)
>
> **Ví dụ 2:** `max_buy = 10`, `volume = 30` → `min(10, 30) = 10` → Chỉ mua 10 (hết sức chứa)

**`if buy_amount > 0:`** — Chỉ đặt lệnh nếu thực sự mua được gì đó.

**`orders.append(Order(product, best_ask, buy_amount))`** — Tạo lệnh MUA:
- `product`: "RAINFOREST_RESIN"
- `best_ask`: Giá mua (9,997)
- `buy_amount`: Số lượng mua (30) — **SỐ DƯƠNG = MUA**

**`max_buy -= buy_amount`** — Cập nhật lại sức mua còn lại.

> **Ví dụ cụ thể:**
> `max_buy = 40`, mua 30 → `max_buy = 40 - 30 = 10` (còn mua được 10 nữa)

---

**Dòng 29-36: Bước 3 — Kiểm tra bên mua (Tìm cơ hội BÁN)**

```python
                if order_depth.buy_orders:
                    best_bid = max(order_depth.buy_orders.keys())
                    if best_bid > FAIR_VALUE:
                        volume = order_depth.buy_orders[best_bid]
                        sell_amount = min(max_sell, volume)
                        if sell_amount > 0:
                            orders.append(Order(product, best_bid, -sell_amount))
                            max_sell -= sell_amount
```

Tương tự bước 2 nhưng **ngược lại** — tìm người **MUA ĐẮT** để bán cho họ.

**`best_bid = max(order_depth.buy_orders.keys())`** — Tìm giá mua CAO NHẤT. Đây là giá tốt nhất mà bạn có thể bán.

> **Ví dụ:** `buy_orders = {9998: 50, 9999: 5, 10003: 15}`
> `max(9998, 9999, 10003) = 10003` ← Giá mua cao nhất là 10,003

**`if best_bid > FAIR_VALUE:`** — Giá mua cao nhất có đắt hơn 10,000 không?
- 10,003 > 10,000? **CÓ!** → Cơ hội bán!

**`volume = order_depth.buy_orders[best_bid]`** — Lấy số lượng mua.

> **Chú ý:** Không cần `abs()` vì `buy_orders` đã là **SỐ DƯƠNG**.

**`sell_amount = min(max_sell, volume)`** — Bán bao nhiêu?

**`Order(product, best_bid, -sell_amount)`** — Tạo lệnh BÁN:
- `-sell_amount`: **SỐ ÂM = BÁN**. Nếu `sell_amount = 15`, lệnh là `Order("RAINFOREST_RESIN", 10003, -15)`.

---

**Dòng 38: Lưu lệnh vào result**

```python
            result[product] = orders
```

Lưu danh sách lệnh của sản phẩm này vào `result`.

---

**Dòng 40: Trả về kết quả**

```python
        return result, 1, ""
```

Trả về 3 giá trị:
1. `result`: Dictionary chứa tất cả lệnh của bạn
2. `1`: Trader data — dữ liệu bạn muốn lưu giữa các tick (1 = không lưu gì đặc biệt)
3. `""`: Chuỗi rỗng — không ghi log

> **Lưu ý:** Từ Prosperity 4, giá trị thứ hai được gọi là "traderData" (int hoặc string). Giá trị `1` hoặc `""` đều hoạt động. Sau này khi cần lưu state giữa các tick, bạn sẽ dùng trường này.

---

## 5. Minh họa 1 tick cụ thể — Chạy qua từng bước

Hãy "chạy thử" bot trong đầu với một tình huống cụ thể. Đây là cách tốt nhất để hiểu code.

### Tình huống:

```
Tick t=500 (giây thứ 5):

Vị thế hiện tại: position = +10 (đang giữ 10 đơn vị Resin)

Order Book:
  sell_orders = {9997: -30, 10001: -20}
  buy_orders  = {10003: 15, 9999: 40}
```

### Chạy từng bước:

**Bước 0: Bắt đầu**

```
product = "RAINFOREST_RESIN"   ← đúng, vào khối if
FAIR_VALUE = 10000
LIMIT = 50
```

**Bước 1: Tính giới hạn**

```
current_pos = state.position.get("RAINFOREST_RESIN", 0) = 10

max_buy  = LIMIT - current_pos = 50 - 10 = 40   ← còn mua được 40
max_sell = LIMIT + current_pos = 50 + 10 = 60   ← còn bán được 60
```

> **Giải thích:** Bạn đang giữ +10. Từ +10 lên +50 là 40 đơn vị (mua thêm). Từ +10 xuống -50 là 60 đơn vị (bán đi).

**Bước 2: Kiểm tra bên bán**

```
sell_orders = {9997: -30, 10001: -20}

best_ask = min(9997, 10001) = 9997

9997 < 10000? CÓ! → Cơ hội MUA!

volume = abs(sell_orders[9997]) = abs(-30) = 30

buy_amount = min(max_buy, volume) = min(40, 30) = 30
  (có 30 đơn vị bán, bạn mua hết 30; còn dư sức chứa 40 nên OK)

buy_amount > 0? CÓ!

→ Tạo lệnh: Order("RAINFOREST_RESIN", 9997, +30)   ← MUA 30 đơn vị ở giá 9997

max_buy = 40 - 30 = 10   ← còn mua được 10 nữa
```

> **Diễn giải:** Có 30 đơn vị Resin đang bán với giá 9,997 (rẻ hơn giá trị 3 đồng mỗi đơn vị). Bạn mua hết 30 đơn vị. Lợi nhuận tiềm năng: 30 × 3 = 90 XIRECs.

**Bước 3: Kiểm tra bên mua**

```
buy_orders = {10003: 15, 9999: 40}

best_bid = max(10003, 9999) = 10003

10003 > 10000? CÓ! → Cơ hội BÁN!

volume = buy_orders[10003] = 15

sell_amount = min(max_sell, volume) = min(60, 15) = 15
  (có 15 đơn vị người ta muốn mua, bán hết)

sell_amount > 0? CÓ!

→ Tạo lệnh: Order("RAINFOREST_RESIN", 10003, -15)   ← BÁN 15 đơn vị ở giá 10003

max_sell = 60 - 15 = 45   ← còn bán được 45 nữa
```

> **Diễn giải:** Có người muốn mua 15 đơn vị Resin với giá 10,003 (đắt hơn giá trị 3 đồng mỗi đơn vị). Bạn bán cho họ 15 đơn vị. Lợi nhuận tiềm năng: 15 × 3 = 45 XIRECs.

**Kết quả tick này:**

```
Lệnh 1: MUA  30 đơn vị @ 9997   (chi 30 × 9997 = 299,910)
Lệnh 2: BÁN  15 đơn vị @ 10003  (nhận 15 × 10003 = 150,045)

Lợi nhuận từ cặp mua-bán này:
  15 đơn vị × (10003 - 9997) = 15 × 6 = 90 XIRECs

  (15 đơn vị còn lại từ lệnh mua chưa có lệnh bán tương ứng,
   nhưng chúng vẫn có lãi tiềm năng vì mua dưới giá trị)

Vị thế mới: 10 + 30 - 15 = +25 (đang giữ 25 đơn vị Resin)
```

> **Cái này có nghĩa là gì?**
>
> Trong chỉ 1 tick (0.01 giây), bot của bạn đã:
> 1. Mua 30 Resin rẻ (giá 9,997, giá trị 10,000 → lãi 3/đơn vị)
> 2. Bán 15 Resin đắt (giá 10,003, giá trị 10,000 → lãi 3/đơn vị)
> 3. Kiếm được ít nhất 90 XIRECs lợi nhuận "chắc chắn"
>
> Nhân với hàng ngàn tick mỗi round → tích lũy thành hàng chục ngàn XIRECs!

---

## 6. Hạn chế của chiến lược cơ bản

Bot trên hoạt động tốt, nhưng có nhiều điểm yếu:

### 6.1. Chỉ "ăn" (take) lệnh có sẵn — không "đặt" (make) lệnh mới

Bot chỉ tìm lệnh sẵn có trong Order Book và "ăn" chúng. Nó không bao giờ **đặt lệnh chờ** (passive order) để người khác đến ăn.

```
Bot cơ bản:
  → Thấy lệnh bán 9997 → MUA (ăn lệnh bán)
  → Thấy lệnh mua 10003 → BÁN (ăn lệnh mua)
  → Không thấy cơ hội? → KHÔNG LÀM GÌ → bỏ phí thời gian!

Bot nâng cao (Frankfurt):
  → Thấy lệnh bán 9997 → MUA (ăn lệnh bán)
  → Thấy lệnh mua 10003 → BÁN (ăn lệnh mua)
  → Không có cơ hội tốt? → ĐẶT LỆNH CHỜ ở giá 9998/10002 → CHỜ người khác đến ăn
```

### 6.2. Chỉ nhìn giá tốt nhất — bỏ qua các mức giá sau

```
sell_orders = {9995: -10, 9997: -30, 10001: -20}

Bot cơ bản:
  best_ask = 9997 → MUA 30 đơn vị
  → BỎ QUA 9995! (cũng rẻ nhưng không được xem)

Bot nâng cao:
  9995 < 10000 → MUA 10 đơn vị
  9997 < 10000 → MUA 30 đơn vị
  → MUA TẤT CẢ lệnh dưới 10000!
```

### 6.3. Không quản lý hàng tồn kho (inventory)

Nếu bot mua liên tục và đạt +50, nó bị "kẹt" — không mua được nữa kể cả khi có cơ hội tốt.

### 6.4. Kết quả thực tế

| Chiến lược | Lợi nhuận/round | Ghi chú |
|------------|-----------------|---------|
| Bot cơ bản (Lesson 1) | ~15,000-20,000 XIRECs | Chỉ taking, chỉ best price |
| Bot Frankfurt | ~39,000 XIRECs | Taking + Making + Inventory management |

→ Bot Frankfurt kiếm gấp **2 lần** với cùng sản phẩm!

---

# PHẦN 3: NÂNG CẤP — HỌC TỪ FRANKFURT HEDGEHOGS

> **Frankfurt Hedgehogs** là đội xếp hạng **#2 thế giới** tại Prosperity 3.
> Họ kiếm ~39,000 SeaShells/round chỉ từ Resin.
> Họ đã công khai chiến lược của họ — và chúng ta sẽ học từ họ.

---

## 7. Wall Mid — Ước lượng giá trị thật chính xác hơn

### Vấn đề với mid_price thông thường

Trong Order Book, `mid_price` (giá giữa) được tính = (giá mua tốt nhất + giá bán tốt nhất) / 2.

Nhưng có một vấn đề: **các bot taker làm lệch giá giữa**.

Hãy xem ví dụ:

```
Tình huống BÌNH THƯỜNG:
══════════════════════════════════════════════
  Sell: 10002(-50)  10001(-5)
  ─────────────── Giá giữa ──────────────────
  Buy:   9999(5)    9998(50)
══════════════════════════════════════════════

  best_ask = 10001       best_bid = 9999
  mid_price = (10001 + 9999) / 2 = 10000.0    ← ĐÚNG!
```

Nhưng khi một bot taker đặt lệnh mua ở 10,000:

```
Tình huống CÓ TAKER BOT:
══════════════════════════════════════════════
  Sell: 10002(-50)  10001(-5)
  ─────────────── Giá giữa ──────────────────
  Buy:  10000(3)    9998(50)       ← taker bot mua 3 đơn vị @ 10000
══════════════════════════════════════════════

  best_ask = 10001       best_bid = 10000
  mid_price = (10001 + 10000) / 2 = 10000.5    ← SAI! Giá bị kéo lên!
```

Giá trị thực vẫn là 10,000, nhưng `mid_price` báo là 10,000.5 vì bot taker kéo `best_bid` lên.

### Giải pháp: Wall Mid

**Ý tưởng:** Thay vì nhìn giá tốt nhất (dễ bị lệch), nhìn giá **XA NHẤT** — đây thường là lệnh của market maker bot (lớn, ổn định).

```
   Sell: 10002(-50)  10001(-5)
                         ↑ best_ask (dễ bị lệch bởi taker)
         ↑ ask_wall = MAX sell price (ổn định, từ market maker)

   Buy:  10000(3)    9998(50)
         ↑ best_bid (dễ bị lệch bởi taker)
                        ↑ bid_wall = MIN buy price (ổn định, từ market maker)
```

**Công thức:**

```
bid_wall = min(buy_orders.keys())      ← giá MUA xa nhất (thấp nhất)
ask_wall = max(sell_orders.keys())     ← giá BÁN xa nhất (cao nhất)
wall_mid = (bid_wall + ask_wall) / 2   ← giá giữa của 2 "bức tường"
```

**Ví dụ tính:**

```
sell_orders = {10001: -5, 10002: -50}
buy_orders  = {10000: 3,  9998: 50}

bid_wall = min(10000, 9998) = 9998
ask_wall = max(10001, 10002) = 10002

wall_mid = (9998 + 10002) / 2 = 10000.0    ← CHÍNH XÁC!
```

So với `mid_price`:
```
mid_price = (10001 + 10000) / 2 = 10000.5    ← Bị lệch 0.5
wall_mid  = (9998 + 10002) / 2  = 10000.0    ← Chính xác!
```

> **Tưởng tượng:**
>
> Trong một căn phòng, có nhiều người đứng (các lệnh mua/bán).
> Những người đứng sát tường (wall) là những người **ỔN ĐỊNH**, luôn đứng đó (market maker).
> Những người đứng giữa phòng đi lại liên tục (taker bot).
>
> Nếu bạn muốn biết **trung tâm phòng**, đừng đo khoảng cách giữa 2 bức tường — không phải giữa 2 người đang đi lại!

**Code:**

```python
def get_walls(self, order_depth):
    """Tính wall_mid — giá trị trung tâm ổn định"""
    # bid_wall: giá mua xa nhất (thấp nhất) — thường là market maker
    bid_wall = min(order_depth.buy_orders.keys())

    # ask_wall: giá bán xa nhất (cao nhất) — thường là market maker
    ask_wall = max(order_depth.sell_orders.keys())

    # wall_mid: trung bình của 2 bức tường — ước lượng giá trị thực
    wall_mid = (bid_wall + ask_wall) / 2

    return bid_wall, wall_mid, ask_wall
```

### Tại sao wall_mid quan trọng?

| Trường hợp | mid_price | wall_mid | Đúng? |
|------------|-----------|----------|-------|
| Bình thường | 10000.0 | 10000.0 | Cả hai đúng |
| Taker kéo bid lên | 10000.5 | 10000.0 | Chỉ wall_mid đúng |
| Taker đẩy ask xuống | 9999.5 | 10000.0 | Chỉ wall_mid đúng |

Với Resin, wall_mid **gần như luôn** trả về 10,000. Nhưng khi bạn chuyển sang KELP (giá thay đổi), wall_mid sẽ là **CÔNG CỤ DUY NHẤT** để biết giá trị hiện tại.

> **Tóm tắt:**
>
> `wall_mid` = nhìn vào 2 bức tường (lệnh lớn của market maker) để tìm trung tâm.
> Không bị ảnh hưởng bởi các bot taker nhỏ nhoi ở giữa.
> Với Resin: wall_mid ≈ 10,000 (luôn luôn).
> Với KELP: wall_mid = cách duy nhất để biết fair value.

---

## 8. Taking + Making — Chiến lược 2 pha

Đây là **sự khác biệt lớn nhất** giữa bot cơ bản và bot Frankfurt.

### Pha 1: TAKING (ăn lệnh có sẵn)

Giống như bot cơ bản, nhưng **tốt hơn**:
- Quét **TẤT CẢ** các mức giá (không chỉ best_ask/best_bid)
- Dùng `wall_mid` thay vì giá cố định 10,000
- Thêm logic xả hàng tồn kho

### Pha 2: MAKING (đặt lệnh chờ)

SAU KHI ăn hết lệnh tốt, đặt lệnh chờ ở vị trí tốt để **CHỜ** người khác đến ăn.

```
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   PHA 1: TAKING (ăn lệnh có lãi ngay lập tức)                 ║
║   ──────────────────────────────────────────                   ║
║   Quét sell_orders: giá < wall_mid - 1 → MUA ngay              ║
║   Quét buy_orders:  giá > wall_mid + 1 → BÁN ngay              ║
║                                                                ║
║   PHA 2: MAKING (đặt lệnh chờ để kiếm thêm)                   ║
║   ──────────────────────────────────────────                   ║
║   Đặt lệnh MUA ở bid_wall + 1 (overbid — chen lên trước)      ║
║   Đặt lệnh BÁN ở ask_wall - 1 (undercut — chen xuống trước)   ║
║   → Chờ các bot taker đến "ăn" lệnh của bạn                   ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

> **Tưởng tượng bạn ở chợ:**
>
> **Pha 1 (Taking):** Bạn đi quanh chợ, thấy ai bán cam rẻ thì mua, thấy ai trả đắt thì bán.
>
> **Pha 2 (Making):** Sau khi đi hết chợ, bạn đặt một cái bàn nhỏ và treo bảng:
> "MUA cam giá 49,000 đồng" (đắt hơn người mua khác 48,000 đồng → bạn được ưu tiên)
> "BÁN cam giá 51,000 đồng" (rẻ hơn người bán khác 52,000 đồng → bạn được ưu tiên)
> Rồi bạn NGỒI ĐỢI. Khi có người cần mua/bán gấp, họ đến bàn bạn TRƯỚC.

### Code đơn giản hóa từ Frankfurt:

```python
class Trader:
    def run(self, state: TradingState):
        result = {}

        for product in state.order_depths:
            order_depth = state.order_depths[product]
            orders = []

            if product == "RAINFOREST_RESIN":
                LIMIT = 50

                # Đọc vị thế
                position = state.position.get(product, 0)
                max_buy = LIMIT - position
                max_sell = LIMIT + position

                buy_orders = order_depth.buy_orders    # {giá: số_lượng_dương}
                sell_orders = order_depth.sell_orders   # {giá: số_lượng_âm}

                # --- Tính wall_mid ---
                bid_wall = min(buy_orders.keys())
                ask_wall = max(sell_orders.keys())
                wall_mid = (bid_wall + ask_wall) / 2

                # ============================================
                # PHA 1: TAKING — Ăn tất cả lệnh có lãi
                # ============================================

                # 1a. Quét TẤT CẢ lệnh bán (tìm cơ hội MUA)
                for price in sorted(sell_orders.keys()):
                    # sell_orders[price] là số âm, abs() để lấy số lượng
                    volume = abs(sell_orders[price])

                    if price <= wall_mid - 1:
                        # Giá rẻ hơn fair value ít nhất 1 đồng → MUA!
                        buy_qty = min(max_buy, volume)
                        if buy_qty > 0:
                            orders.append(Order(product, price, buy_qty))
                            max_buy -= buy_qty

                    elif price <= wall_mid and position < 0:
                        # Giá = fair value + đang short → mua để flatten
                        buy_qty = min(max_buy, volume, abs(position))
                        if buy_qty > 0:
                            orders.append(Order(product, price, buy_qty))
                            max_buy -= buy_qty
                            position += buy_qty

                # 1b. Quét TẤT CẢ lệnh mua (tìm cơ hội BÁN)
                for price in sorted(buy_orders.keys(), reverse=True):
                    volume = buy_orders[price]

                    if price >= wall_mid + 1:
                        # Giá đắt hơn fair value ít nhất 1 đồng → BÁN!
                        sell_qty = min(max_sell, volume)
                        if sell_qty > 0:
                            orders.append(Order(product, price, -sell_qty))
                            max_sell -= sell_qty

                    elif price >= wall_mid and position > 0:
                        # Giá = fair value + đang long → bán để flatten
                        sell_qty = min(max_sell, volume, position)
                        if sell_qty > 0:
                            orders.append(Order(product, price, -sell_qty))
                            max_sell -= sell_qty
                            position -= sell_qty

                # ============================================
                # PHA 2: MAKING — Đặt lệnh chờ để kiếm thêm
                # ============================================

                # Overbid: đặt lệnh MUA cao hơn bid_wall 1 bậc
                bid_price = bid_wall + 1
                # Undercut: đặt lệnh BÁN thấp hơn ask_wall 1 bậc
                ask_price = ask_wall - 1

                # An toàn: chỉ đặt lệnh nếu còn lãi
                if bid_price < wall_mid and max_buy > 0:
                    orders.append(Order(product, bid_price, max_buy))

                if ask_price > wall_mid and max_sell > 0:
                    orders.append(Order(product, ask_price, -max_sell))

            result[product] = orders

        return result, 1, ""
```

### Giải thích chi tiết từng phần:

**Pha 1a: Quét TẤT CẢ lệnh bán**

```python
for price in sorted(sell_orders.keys()):
```

Thay vì chỉ nhìn `best_ask` (giá bán thấp nhất), bot quét **TẤT CẢ** các mức giá bán, từ thấp đến cao.

> **Ví dụ:**
> ```
> sell_orders = {9995: -10, 9997: -30, 10001: -20}
> sorted keys = [9995, 9997, 10001]
>
> Giá 9995: 9995 <= 10000 - 1 = 9999? CÓ → MUA 10 đơn vị
> Giá 9997: 9997 <= 9999? CÓ → MUA 30 đơn vị
> Giá 10001: 10001 <= 9999? KHÔNG → Dừng quét
>
> Tổng: MUA 40 đơn vị (thay vì chỉ 30 nếu chỉ nhìn best_ask=9997)
> ```

**Logic flatten (xả hàng tồn kho):**

```python
elif price <= wall_mid and position < 0:
    buy_qty = min(max_buy, volume, abs(position))
```

Nếu bạn đang **short** (position < 0) và có lệnh bán ở đúng giá wall_mid → mua để trở về 0.

> **Ví dụ:** Position = -20, có lệnh bán ở giá 10000 (= wall_mid).
> → Mua 20 đơn vị ở 10000 để "xả" vị thế short.
> → Không lãi, không lỗ, nhưng **giải phóng sức chứa** để mua khi cơ hội tốt.

**Pha 2: Đặt lệnh chờ**

```python
bid_price = bid_wall + 1    # Overbid
ask_price = ask_wall - 1    # Undercut
```

Đặt lệnh MUA ở `bid_wall + 1` và lệnh BÁN ở `ask_wall - 1`. Đây là giá "chen" trước market maker.

> **Ví dụ:**
> ```
> bid_wall = 9997, ask_wall = 10003
>
> bid_price = 9997 + 1 = 9998   ← Đặt lệnh MUA ở 9998
> ask_price = 10003 - 1 = 10002  ← Đặt lệnh BÁN ở 10002
>
> wall_mid = (9997 + 10003) / 2 = 10000
>
> 9998 < 10000? CÓ → an toàn để đặt lệnh mua
> 10002 > 10000? CÓ → an toàn để đặt lệnh bán
> ```

### Bảng so sánh:

| Tính năng | Bot cơ bản (Lesson 1) | Bot Frankfurt |
|-----------|----------------------|---------------|
| Taking | Chỉ best_ask / best_bid | Quét TẤT CẢ mức giá có lãi |
| Making | Không có | Đặt lệnh chờ ở bid_wall+1 / ask_wall-1 |
| Fair value | Hardcoded 10,000 | wall_mid (linh hoạt) |
| Xử lý tồn kho | Không | Flatten ở wall_mid |
| Kết quả | ~15,000-20,000/round | ~39,000/round |

---

## 9. Overbidding & Undercutting — Giành quyền ưu tiên lệnh chờ

Khi đặt lệnh chờ (making), bạn muốn lệnh của mình được **THỰC HIỆN TRƯỚC** lệnh của người khác. Làm sao?

### Nguyên tắc ưu tiên lệnh

Trong Prosperity, khi có nhiều lệnh mua ở các giá khác nhau, lệnh có **GIÁ CAO NHẤT** được thực hiện trước. Tương tự, lệnh bán có **GIÁ THẤP NHẤT** được thực hiện trước.

```
Order Book hiện tại:
  Sell: 10003(-50), 10002(-5)     ← ask_wall = 10003
  Buy:  9997(50),   9998(5)       ← bid_wall = 9997

Lệnh của market maker:
  Mua @ 9997 (50 đơn vị)    ← "bức tường" mua
  Bán @ 10003 (50 đơn vị)   ← "bức tường" bán

Bot Frankfurt đặt lệnh "chen":
  Mua @ 9998 (overbid: +1 so với bid_wall)   ← "nhảy" lên trước bức tường mua
  Bán @ 10002 (undercut: -1 so với ask_wall)  ← "nhảy" xuống trước bức tường bán
```

Khi một bot taker đến:

```
Bot taker muốn BÁN Resin:
  → Tìm lệnh mua cao nhất
  → Thấy lệnh mua của bạn ở 9998 (cao hơn market maker ở 9997)
  → Bán cho BẠN trước! ← Bạn được "ăn" trước market maker!

Bot taker muốn MUA Resin:
  → Tìm lệnh bán thấp nhất
  → Thấy lệnh bán của bạn ở 10002 (thấp hơn market maker ở 10003)
  → Mua từ BẠN trước! ← Bạn được "ăn" trước market maker!
```

> **Tưởng tượng ở siêu thị:**
>
> Có 2 quầy bán cam:
> - Quầy A bán với giá 52,000 đồng (market maker)
> - Quầy B (của bạn) bán với giá 51,000 đồng (undercut)
>
> Khách hàng đến → thấy quầy B rẻ hơn → mua của bạn trước!
>
> Tương tự, có 2 người muốn mua cam:
> - Người A trả 48,000 đồng (market maker)
> - Bạn trả 49,000 đồng (overbid)
>
> Người bán cam đến → thấy bạn trả nhiều hơn → bán cho bạn trước!

### Kiểm tra an toàn

**QUAN TRỌNG:** Chỉ overbid/undercut nếu giá vẫn CÓ LÃI.

```python
# Chỉ overbid nếu giá mua MỚI vẫn DƯỚI wall_mid
overbid_price = bid_wall + 1
if overbid_price < wall_mid:      # Vẫn dưới giá trị thực → có lãi
    bid_price = overbid_price     # An toàn để đặt lệnh
else:
    bid_price = bid_wall          # Không overbid, giữ nguyên

# Chỉ undercut nếu giá bán MỚI vẫn TRÊN wall_mid
undercut_price = ask_wall - 1
if undercut_price > wall_mid:     # Vẫn trên giá trị thực → có lãi
    ask_price = undercut_price    # An toàn để đặt lệnh
else:
    ask_price = ask_wall          # Không undercut, giữ nguyên
```

> **Ví dụ an toàn:**
> ```
> bid_wall = 9997, ask_wall = 10003, wall_mid = 10000
>
> overbid_price = 9998
> 9998 < 10000? CÓ → An toàn, đặt lệnh mua ở 9998  (lãi 2 đồng/đơn vị)
>
> undercut_price = 10002
> 10002 > 10000? CÓ → An toàn, đặt lệnh bán ở 10002 (lãi 2 đồng/đơn vị)
> ```
>
> **Ví dụ KHÔNG an toàn:**
> ```
> bid_wall = 9999, ask_wall = 10001, wall_mid = 10000
>
> overbid_price = 10000
> 10000 < 10000? KHÔNG → Không overbid! (mua ở giá trị thực = không lãi)
>
> undercut_price = 10000
> 10000 > 10000? KHÔNG → Không undercut! (bán ở giá trị thực = không lãi)
> ```

---

## 10. Inventory Flattening — Xả hàng tồn kho

### Vấn đề: "Kẹt" vị thế

Hãy tưởng tượng bot của bạn mua liên tục và đạt vị thế +50 (tối đa). Lúc này:

```
Vị thế: +50

max_buy  = 50 - 50 = 0    ← KHÔNG MUA ĐƯỢC NỮA!
max_sell = 50 + 50 = 100

Cơ hội tuyệt vời xuất hiện: Resin bán ở giá 9990!
→ Nhưng max_buy = 0 → không mua được → BỎ LỠ!
```

Tương tự, nếu vị thế là -50:

```
Vị thế: -50

max_buy  = 50 + 50 = 100
max_sell = 50 - 50 = 0    ← KHÔNG BÁN ĐƯỢC NỮA!

Cơ hội tuyệt vời: Có người mua Resin ở giá 10010!
→ Nhưng max_sell = 0 → không bán được → BỎ LỠ!
```

### Giải pháp: Flatten ở giá trị thực

Khi vị thế quá lệch, bán mua/bán ở đúng giá `wall_mid` (giá trị thực) để **giải phóng sức chứa**.

```python
# Đang giữ nhiều (long) + có người mua ở wall_mid → BÁN để giảm vị thế
if price >= wall_mid and position > 0:
    sell_qty = min(max_sell, volume, position)
    orders.append(Order(product, price, -sell_qty))
    position -= sell_qty

# Đang thiếu (short) + có người bán ở wall_mid → MUA để tăng vị thế
if price <= wall_mid and position < 0:
    buy_qty = min(max_buy, volume, abs(position))
    orders.append(Order(product, price, buy_qty))
    position += buy_qty
```

> **Triết lý:** Flatten ở giá trị thực → **không lãi, không lỗ** → nhưng **GIẢI PHÓNG SỨC CHỨA** cho giao dịch có lãi tiếp theo.

### Ví dụ cụ thể:

```
Vị thế hiện tại: +45 (gần đầy!)
max_buy = 50 - 45 = 5     ← chỉ mua được 5 nữa
max_sell = 50 + 45 = 95

Có người mua ở 10000 (= wall_mid) với volume = 20

→ Flatten: BÁN 20 đơn vị ở 10000
  (chỉ bán tối đa = min(95, 20, 45) = 20)

Vị thế mới: +45 - 20 = +25
max_buy = 50 - 25 = 25    ← bây giờ mua được 25!
max_sell = 50 + 25 = 75

→ Sức chứa từ 5 tăng lên 25! Sẵn sàng cho cơ hội tiếp theo!
```

> **Tưởng tượng:**
>
> Bạn có 1 cái tủ lạnh chỉ chứa được 50 trái cam. Hiện tại chứa 45 trái.
> Có người nói "Tôi mua cam với giá 50,000 đồng" (giá đúng = giá trị).
> Bạn bán 20 trái với giá 50,000 → không lãi không lỗ.
> Nhưng bây giờ tủ lạnh còn chỗ 25 trái → nếu ngày mai có cam rẻ, bạn mua được nhiều hơn!

---

## 11. Cách hệ thống xử lý lệnh — Bí mật then chốt

Hiểu được **THỨ TỰ XỬ LÝ** lệnh là yếu tố quan trọng để hiểu tại sao Making (Pha 2) hoạt động.

### Thứ tự mỗi tick:

```
╔══════════════════════════════════════════════════════════════╗
║ Bước 1: Xóa TẤT CẢ lệnh cũ (lệnh chỉ tồn tại 1 tick)     ║
║                                                              ║
║ Bước 2: Market maker bots đặt lệnh → tạo "bức tường"        ║
║                                                              ║
║ Bước 3: Một số taker bots giao dịch                          ║
║                                                              ║
║ Bước 4: BOT CỦA BẠN đặt lệnh (taking + making)             ║
║         → Bạn thấy Order Book đã "ăn" bởi bước 3            ║
║         → Lệnh taking thực hiện ngay                         ║
║         → Lệnh making được đặt vào Order Book                ║
║                                                              ║
║ Bước 5: THÊM taker bots giao dịch                            ║
║         → Có thể ĂN lệnh making của bạn!                    ║
║                                                              ║
║ Bước 6: Tick kết thúc. Quay lại bước 1.                      ║
╚══════════════════════════════════════════════════════════════╝
```

### Tại sao điều này quan trọng?

**Lệnh making của bạn được đặt ở Bước 4, và taker bots ở Bước 5 có thể ĂN chúng.**

Nếu bạn không đặt lệnh making (như bot cơ bản), bạn BỎ LỠ toàn bộ cơ hội từ bước 5.

> **Ví dụ:**
> ```
> Bước 2: Market maker đặt lệnh mua @ 9997 (50 units)
> Bước 3: (không có gì xảy ra)
> Bước 4: Bot của bạn:
>   - Taking: mua 30 đơn vị @ 9997 (có người bán rẻ)
>   - Making: đặt lệnh mua @ 9998 (overbid market maker)
>            đặt lệnh bán @ 10002 (undercut market maker)
> Bước 5: Taker bot muốn bán Resin
>   → Thấy lệnh mua của bạn @ 9998 (cao hơn market maker @ 9997)
>   → BÁN cho bạn! ← Bạn kiếm được thêm lợi nhuận!
> ```

### Các điểm cần nhớ:

1. **Tốc độ không quan trọng** — Bạn luôn thấy toàn bộ Order Book trước khi quyết định. Không phải ai nhanh hơn thì thắng.

2. **Lệnh chỉ tồn tại 1 tick** — Không cần lo "hủy lệnh cũ". Mỗi tick bắt đầu từ trang giấy mới.

3. **Making có cơ hội thực sự** — Bot taker ở bước 5 có thể ăn lệnh making của bạn, tạo thêm lợi nhuận.

> **Đây là LÝ DO Frankfurt LUÔN đặt lệnh making (Pha 2)** — các bot taker ở bước 5 có thể ăn lệnh của họ, kiếm được lợi nhuận mà bot cơ bản (chỉ có Pha 1) bỏ lỡ hoàn toàn.

---

## 12. Tại sao Frankfurt Hedgehogs thắng?

Frankfurt chia sẻ 5 nguyên tắc cốt lõi trong writeup của họ:

### Nguyên tắc 1: Hiểu sâu trước khi code

> *"Placed enormous emphasis on deep structural understanding of each product."*
> — Frankfurt Hedgehogs

Họ không nhảy vào code ngay. Họ dành thời gian **hiểu** cách thị trường hoạt động:
- Các bot market maker đặt lệnh như thế nào?
- Các bot taker hành vi ra sao?
- Thứ tự xử lý lệnh là gì?
- Fair value được xác định thế nào?

**Bài học cho bạn:** Trước khi code, hãy đọc kỹ và hiểu. Đọc guide này là bước đúng đầu tiên!

### Nguyên tắc 2: Chiến lược đơn giản, ít tham số

> *"Focused on simple, robust strategies, minimizing parameters whenever possible."*

Chiến lược Resin của họ chỉ có:
- `wall_mid` (tự động tính từ Order Book)
- Overbid/undercut bằng 1 tick
- Flatten ở wall_mid

Không có Machine Learning. Không có công thức phức tạp. Không có 10 tham số cần tinh chỉnh.

**Bài học:** Đơn giản mà hiệu quả thì tốt hơn phức tạp mà không hiểu.

### Nguyên tắc 3: Không overfit

> *"If you can't explain why a strategy should work from first principles, any outperformance in historical data is probably noise."*

Nếu bạn không giải thích được **TẠI SAO** chiến lược hoạt động, kết quả backtest tốt chỉ là **may mắn**. Nó sẽ không hoạt động trên dữ liệu mới.

**Ví dụ:**
- TỐT: "Tôi mua dưới 10,000 vì Resin luôn có giá trị 10,000" → Giải thích được → Chiến lược tốt
- XẤU: "Tôi mua khi RSI < 30 vì backtest cho thấy lãi" → Không giải thích được tại sao RSI hoạt động → Có thể là may mắn

### Nguyên tắc 4: Công cụ tốt = phân tích nhanh

Frankfurt xây dashboard riêng để phân tích kết quả. Bạn có thể dùng:
- **Jmerle Backtester** (có sẵn trong project)
- **Visualizer** (file visualizer.py)
- Log file để debug

### Nguyên tắc 5: Học từ người đi trước

Frankfurt đọc writeup của những người thắng trước họ — và bây giờ bạn đang đọc writeup của Frankfurt. Vòng tròn tiếp nối!

### PnL của Frankfurt (tham khảo):

| Sản phẩm | PnL/round | Chiến lược |
|----------|-----------|------------|
| **Resin** | **~39,000** | **Market making (taking + making)** |
| Kelp | ~5,000 | Market making (wall_mid động) |
| Squid Ink | ~8,000 | Theo dõi trader Olivia |
| Baskets | ~50,000 | Arbitrage thống kê (ETF vs thành phần) |
| Options | ~100,000-150,000 | IV scalping |
| Macarons | ~80,000-100,000 | Arbitrage địa lý |

> **Chú ý:** Resin là ~39,000/round — không phải kiếm nhiều nhất, nhưng là **ỔN ĐỊNH NHẤT**. Chiến lược Resin của họ hầu như **không bao giờ thua lỗ**.

---

# PHẦN 4: BƯỚC TIẾP THEO

---

## 13. Tổng kết những gì đã học

Bạn đã đi từ 0 đến hiểu được chiến lược giao dịch Resin cấp cao:

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   LEVEL 1: Bot cơ bản (Lesson 1)                                ║
║   ─────────────────────────────                                  ║
║   • Mua dưới 10,000, bán trên 10,000                             ║
║   • Chỉ nhìn best_ask và best_bid                                ║
║   • Không đặt lệnh chờ (making)                                  ║
║   • Kết quả: ~15,000-20,000 XIRECs/round                        ║
║                                                                  ║
║   LEVEL 2: Bot Frankfurt                                         ║
║   ─────────────────────                                          ║
║   • Dùng wall_mid thay vì hardcoded 10,000                       ║
║   • Quét TẤT CẢ mức giá có lãi (không chỉ best price)           ║
║   • Đặt lệnh chờ (making) với overbid/undercut                   ║
║   • Flatten vị thế ở wall_mid để giải phóng sức chứa             ║
║   • Kết quả: ~39,000 XIRECs/round                               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

### Khái niệm đã học:

| # | Khái niệm | Ý nghĩa |
|---|-----------|---------|
| 1 | Fair Value cố định | Resin luôn = 10,000 XIRECs |
| 2 | Position Limit | Tối đa ±50, phải tính max_buy/max_sell |
| 3 | Aggressive Taking | Ăn lệnh có lãi từ Order Book |
| 4 | Wall Mid | Trung bình giá xa nhất 2 bên = fair value ổn định |
| 5 | Overbid/Undercut | Chen trước market maker +1/-1 để được ưu tiên |
| 6 | Making (Passive Orders) | Đặt lệnh chờ để taker bots ăn |
| 7 | Inventory Flattening | Xả vị thế ở fair value để giải phóng sức chứa |
| 8 | Thứ tự xử lý lệnh | Market maker → Taker → Bạn → Taker (ăn lệnh making của bạn) |

---

## 14. Bài tập thực hành

Hãy thử làm các bài tập sau để củng cố kiến thức:

### Bài tập 1: Chạy bot cơ bản
1. Mở file `Lesson1_Resin.py` (hoặc tạo mới từ code ở mục 4)
2. Chạy với backtester: `python backtester.py`
3. Xem kết quả PnL — nên đạt khoảng 15,000-20,000/round

### Bài tập 2: Thay đổi ngưỡng (threshold)
1. Thử đổi `FAIR_VALUE = 10000` thành `9999` hoặc `10001`
2. Chạy lại backtest — PnL tăng hay giảm?
3. **Suy nghĩ:** Tại sao 10,000 là tốt nhất?

### Bài tập 3: Thêm Making (Pha 2)
1. Lấy bot cơ bản từ bài tập 1
2. Thêm code đặt lệnh chờ sau phần taking:
   ```python
   # Sau khi taking xong, thêm:
   bid_price = best_bid_wall + 1  # (bạn cần tính bid_wall trước)
   ask_price = best_ask_wall - 1
   # Đặt lệnh...
   ```
3. Chạy backtest và so sánh PnL với bot chỉ có taking

### Bài tập 4: Implement wall_mid
1. Viết hàm `get_walls()` như ở mục 7
2. In ra wall_mid mỗi tick (dùng logger)
3. Xác nhận wall_mid gần như luôn = 10,000 cho Resin

### Bài tập 5: Thêm Inventory Flattening
1. Thêm logic flatten từ mục 10
2. Chạy backtest — vị thế có "ổn định" hơn không?
3. PnL có tăng không?

> **Mẹo:** Làm từng bài tập MỘT, kiểm tra kết quả, rồi mới làm bài tiếp. Không nên nhảy cả 5 bài cùng lúc!

---

## 15. Tiếp theo: KELP

Sau khi nắm vững Resin, sản phẩm tiếp theo là **KELP**.

### Điểm giống và khác:

| | Resin | KELP |
|--|-------|------|
| Fair value | **Cố định** = 10,000 | **Thay đổi** mỗi tick (random walk) |
| wall_mid | Luôn ≈ 10,000 (tùy chọn) | **BẮT BUỘC** để biết fair value |
| Chiến lược | Mua dưới 10K, bán trên 10K | Mua dưới wall_mid, bán trên wall_mid |
| Độ khó | Dễ | Trung bình |

### KELP khác gì?

Với Resin, bạn có thể "gian lận" bằng cách hardcode `FAIR_VALUE = 10000`. Với KELP, giá thay đổi liên tục — **bạn PHẢI tính wall_mid** mỗi tick.

```
KELP fair value theo thời gian:
  t=0:   2050
  t=100: 2055
  t=200: 2048
  t=300: 2060
  t=400: 2045
  ...

Không thể hardcode! Phải tính wall_mid mỗi tick!
```

Nhưng tin tốt là: **chiến lược Frankfurt cho KELP gần như giống Resin** — chỉ thay `FAIR_VALUE = 10000` bằng `wall_mid` tính từ Order Book. Tất cả logic khác (taking, making, overbid, undercut, flatten) giống hoàn toàn.

> **Tiếp theo:** Đọc guide Round1_Kelp khi có (sẽ được viết sau).

---

*Based on Lesson 1 + Frankfurt Hedgehogs strategy (Top 2, Prosperity 3). Updated for Prosperity 4.*
