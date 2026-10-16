from enum import IntEnum


class CustomerType(IntEnum):
    # 수정: 실제 등급 이름은 정해져 있지 않으므로 할인율로 의미를 표현합니다.
    REGULAR = 0
    DISCOUNT_5 = 1
    DISCOUNT_10 = 2
    DISCOUNT_20 = 3


# 수정: 할인 정책을 한곳에 모으고, float 대신 정수 백분율을 사용합니다.
DISCOUNT_PERCENT = {
    CustomerType.REGULAR: 0,
    CustomerType.DISCOUNT_5: 5,
    CustomerType.DISCOUNT_10: 10,
    CustomerType.DISCOUNT_20: 20,
}
COUPON_AMOUNT = 3000


def calc_order(u_type: int, price: int, qty: int, coupon: bool | str) -> int:
    """등급 할인 후 쿠폰을 차감한 최종 금액을 원 단위 정수로 반환합니다.

    u_type: 0(일반), 1(5%), 2(10%), 3(20%) 또는 CustomerType 값.
    price: 0 이상의 정수 단가(원). qty: 1 이상의 정수 수량.
    coupon: True/False 또는 YES/NO 문자열(대소문자와 앞뒤 공백 무시).
    최종 금액은 최소 0원이며, 원 미만 금액은 기존 정책대로 버립니다.
    잘못된 자료형은 TypeError, 허용 범위 밖의 값은 ValueError를 냅니다.
    """
    # 수정: bool은 int의 하위 타입이므로 별도로 제외해야 합니다.
    if isinstance(u_type, bool) or not isinstance(u_type, int):
        raise TypeError("u_type은 정수 등급이어야 합니다.")
    if u_type not in DISCOUNT_PERCENT:
        raise ValueError("u_type은 0, 1, 2, 3 중 하나여야 합니다.")

    # 수정: 잘못된 입력을 0원으로 덮지 않고, 계산 전에 원인을 알립니다.
    for name, value in (("price", price), ("qty", qty)):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name}는 정수여야 합니다.")
    if price < 0:
        raise ValueError("price는 0 이상이어야 합니다.")
    if qty <= 0:
        raise ValueError("qty는 1 이상이어야 합니다.")

    # 수정: 기존 YES/NO 호출을 지원하면서 'Yes', ' yes '도 처리합니다.
    # 오타를 쿠폰 미사용으로 간주하지 않도록 허용값을 검증합니다.
    if isinstance(coupon, bool):
        use_coupon = coupon
    elif isinstance(coupon, str):
        normalized_coupon = coupon.strip().upper()
        if normalized_coupon not in ("YES", "NO"):
            raise ValueError("coupon 문자열은 YES 또는 NO여야 합니다.")
        use_coupon = normalized_coupon == "YES"
    else:
        raise TypeError("coupon은 bool 또는 YES/NO 문자열이어야 합니다.")

    # 수정: 금액을 1/100원 단위의 정수로 유지해 큰 금액도 정확히 계산합니다.
    # 원래 순서(등급 할인 → 쿠폰 차감 → 최저 0원 → 버림)를 유지합니다.
    total_hundredths = price * qty * (100 - DISCOUNT_PERCENT[u_type])
    if use_coupon:
        total_hundredths -= COUPON_AMOUNT * 100
    return max(0, total_hundredths) // 100


# 수정: 직접 실행할 때만 예제를 실행하고 반환값을 화면에 표시합니다.
if __name__ == "__main__":
    result = calc_order(CustomerType.DISCOUNT_5, 100, 20, "Yes")
    print(f"최종 결제 금액: {result:,}원")
