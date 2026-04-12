from datamodel import OrderDepth, TradingState, Order
from typing import List, Optional
import math


# Position limit của tutorial round
POSITION_LIMITS = {
    "EMERALDS": 80,
    "TOMATOES": 80,
}

# EMERALDS giống Resin:
# fair value cố định ở 10000
EMERALDS_FAIR_VALUE = 10000


class Trader:
    def run(self, state: TradingState):
        # result là dict chứa toàn bộ lệnh của từng sản phẩm
        # print("State timestamp:", state.timestamp)
        result = {}

        # EMERALDS được trade như Resin:
        # fair value cố định, take giá tốt trước, sau đó đặt maker quotes
        result["EMERALDS"] = self.trade_emeralds(state)

        # TOMATOES được trade như Kelp:
        # fair value không cố định, ta ước lượng bằng wall mid
        # # result["TOMATOES"] = self.trade_tomatoes(state)

        # Bot nay khong can nho du lieu giua cac timestep
        traderData = ""

        # Không dùng conversion trong bài này
        conversions = 0

        return result, conversions, traderData

    def trade_emeralds(self, state: TradingState) -> List[Order]:
        product = "EMERALDS"

        # Nếu timestep này không có EMERALDS trong order book thì không làm gì
        if product not in state.order_depths:
            return []

        order_depth = state.order_depths[product]
        initial_position = state.position.get(product, 0)
        current_position = initial_position
        limit = POSITION_LIMITS[product]
        orders: List[Order] = []

        # ============================================================
        # ĐỐI VỚI EMERALDS, FAIR VALUE LUÔN LÀ 10000!
        # ============================================================
        if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
            return []
            
        bid_wall = max(order_depth.buy_orders.keys())
        ask_wall = min(order_depth.sell_orders.keys())
        
        wall_mid = EMERALDS_FAIR_VALUE

        # Sắp xếp nâng cao:
        # sell_orders: để tra giá ask từ thấp tới cao
        sell_orders = sorted(order_depth.sell_orders.items())
        # buy_orders: để tra giá bid từ cao tới thấp
        buy_orders = sorted(order_depth.buy_orders.items(), reverse=True)


        # ============================================================
        # PHASE 1: TAKING (KHỚP LỆNH CHỦ ĐỘNG - HỐT HÀNG NGAY)
        # ============================================================

        # 1A. QUÉT CHIỀU BÁN (Tìm người bán rẻ) để MUA vào
        for ask_price, ask_volume in sell_orders:
            ask_vol_abs = abs(ask_volume)
            
            # Trường hợp 1: Bán quá rẻ (rẻ hơn wall_mid >= 1 giá) -> Mua kiếm lời ngay tức khắc
            if ask_price <= wall_mid - 1:
                buy_qty = min(limit - current_position, ask_vol_abs)
                if buy_qty > 0:
                    orders.append(Order(product, ask_price, buy_qty))
                    current_position += buy_qty
            
            # Trường hợp 2: Xả kho (Inventory risk neutralization)
            # Giá không hề rẻ (bằng đúng wall_mid), nhưng vì chúng ta đang bán khống (ôm âm hàng: position < 0)
            # chúng ta phải MUA LẠI ngay lập tức để tránh rủi ro lệch vị thế. Mua huề vốn!
            pass


        # 1B. QUÉT CHIỀU MUA (Tìm người mua đắt) để BÁN ra
        for bid_price, bid_volume in buy_orders:
            # Trường hợp 1: Mua quá đắt (đắt hơn wall_mid >= 1 giá) -> Bán ngay chốt lời
            if bid_price >= wall_mid + 1:
                sell_qty = min(limit + current_position, bid_volume)
                if sell_qty > 0:
                    orders.append(Order(product, bid_price, -sell_qty))
                    current_position -= sell_qty
            
            # Trường hợp 2: Xả kho
            # Giá này không có lời nhiều (bằng wall_mid), nhưng vì ta đang ôm nhiều hàng (position > 0)
            # ta phải BÁN XẢ NGAY (xả hàng huề vốn) để clear kho.
            pass


        # ============================================================
        # PHASE 2: MAKING (TRANH GIÁ TREO LỆNH - PENNYING GIỐNG FRANKFURT)
        # ============================================================
        
        # Đặt base case là biên độ rẻ nhất có lời (bắt buộc phải cách wall_mid ít nhất 1 đồng)
        # (Nếu ta mua rẻ 1 đồng, và bán đắt 1 đồng thì edge = 1 x 2 chiều = 2 đồng)
        bid_price_make = min(bid_wall + 1, wall_mid - 1) 
        ask_price_make = max(ask_wall - 1, wall_mid + 1)

        # 2A. TRANH MUA (Overbidding) chen lệnh 1 đồng phía trước đối thủ
        for bp, bv in buy_orders:
            if bv > 10 and (bp + 1) < wall_mid:
                bid_price_make = max(bid_price_make, bp + 1)
                break
            elif bp < wall_mid:
                bid_price_make = max(bid_price_make, bp)
                break

        # 2B. TRANH BÁN (Underbidding) chen lệnh phía trước người bán khác
        for sp, sv in sell_orders:
            sv_abs = abs(sv)
            if sv_abs > 10 and (sp - 1) > wall_mid:
                ask_price_make = min(ask_price_make, sp - 1)
                break
            elif sp > wall_mid:
                ask_price_make = min(ask_price_make, sp)
                break

        # Tính toán room (capacity) sau khi Taking
        buy_room = limit - current_position
        sell_room = limit + current_position

        # Cuối cùng, quăng bộ sổ lệnh bán/mua vào OrderBook thôi!
        if buy_room > 0:
            orders.append(Order(product, bid_price_make, buy_room))
        
        if sell_room > 0:
            orders.append(Order(product, ask_price_make, -sell_room))

        return orders

    def trade_tomatoes(self, state: TradingState) -> List[Order]:
        product = "TOMATOES"

        # Nếu timestep này không có TOMATOES trong order book thì không làm gì
        if product not in state.order_depths:
            return []

        order_depth = state.order_depths[product]
        initial_position = state.position.get(product, 0)
        limit = POSITION_LIMITS[product]
        orders: List[Order] = []

        if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
            return []

        # bid wall = giá mua TỐT NHẤT, ask wall = giá bán TỐT NHẤT
        bid_wall = max(order_depth.buy_orders.keys())
        ask_wall = min(order_depth.sell_orders.keys())
        wall_mid = (bid_wall + ask_wall) / 2

        # ============================================================
        # THUẬT TOÁN ĐỘNG (DYNAMIC TRADER) CỦA FRANKFURT HEDGEHOGS
        # - Họ không làm thao tác Taking (Tự đi dò lệnh rẻ/đắt)
        # - Cứ bám sát hai đầu sổ lệnh (bid_wall và ask_wall) mà Make !!
        # ============================================================

        # ------------------------------------------------------------
        # 1. ĐẶT LỆNH MUA (BID)
        # ------------------------------------------------------------
        # Mặc định luôn chen ngay 1 đồng vào cuối hàng mua
        bid_price = bid_wall + 1
        bid_volume = limit - initial_position

        # Điều chỉnh giá chặn rủi ro (Giả lập thông tin / Informed trading của Frankfurt):
        # Nếu khoảng lời quá mỏng (chưa đến 1 đồng lời từ wall_mid)
        # Và ta đang ôm vị thế ngắn (bán khống) nhưng chênh lệch chưa chạm đáy -40.
        # Frankfurt sẽ dời lệnh Mua xuống thẳng Đáy Sổ (bid_wall) để chờ sung rụng chứ không thèm tranh chen ngang nữa.
        # (Ở đây ta áp dụng logic an toàn chung: Nếu edge < 1, tụt giá mua xuống bằng đáy!)
        if wall_mid - bid_price < 1:
            bid_price = bid_wall

        if bid_volume > 0:
            orders.append(Order(product, bid_price, bid_volume))


        # ------------------------------------------------------------
        # 2. ĐẶT LỆNH BÁN (ASK)
        # ------------------------------------------------------------
        # Mặc định chen ngay 1 đồng vào cuối hàng bán
        ask_price = ask_wall - 1
        ask_volume = limit + initial_position  # Chú ý: Cần gắn dấu trừ khi thả vào Order()

        # Quản trị rủi ro bên phán Bán:
        # Tương tự mua, nếu bán ra mà chẳng lời nổi quá 1 đồng so với wall_mid
        # Frankfurt lập tức dạt giá bán về sát Đỉnh của Sổ lệnh (ask_wall) để núp lùm.
        if ask_price - wall_mid < 1:
            ask_price = ask_wall

        if ask_volume > 0:
            orders.append(Order(product, ask_price, -ask_volume))

        return orders
