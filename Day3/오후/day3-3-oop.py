from dataclasses import dataclass
from enum import IntEnum


class CustomerType(IntEnum):
    """숫자로 전달하던 고객 등급에 의미 있는 이름을 부여합니다."""

    REGULAR = 0
    DISCOUNT_5 = 1
    DISCOUNT_10 = 2
    DISCOUNT_20 = 3


# 할인 정책은 기존 수정본과 동일하게 유지합니다.
DISCOUNT_PERCENT = {
    CustomerType.REGULAR: 0,
    CustomerType.DISCOUNT_5: 5,
    CustomerType.DISCOUNT_10: 10,
    CustomerType.DISCOUNT_20: 20,
}
COUPON_AMOUNT = 3000


@dataclass(frozen=True)
class Order:
    """주문 정보와 검증, 금액 계산을 함께 관리하는 클래스.

    단가는 0 이상의 정수(원), 수량은 1 이상의 정수입니다.
    등급은 0~3 또는 CustomerType, 쿠폰은 bool 또는 YES/NO를 받습니다.
    잘못된 자료형은 TypeError, 범위나 문자열 값 오류는 ValueError입니다.
    """

    # 변경: 함수 인수였던 값을 주문 객체의 속성으로 보관합니다.
    # dataclass가 이 속성들을 받는 __init__을 자동으로 만들어 줍니다.
    u_type: CustomerType | int
    price: int
    qty: int
    coupon: bool | str = False

    def __post_init__(self) -> None:
        """자동 생성된 __init__ 직후 실행되어 입력을 검증합니다."""
        # 변경: 주문 생성 시 검증하므로 잘못된 주문으로 계산할 수 없습니다.
        self._validate_inputs()

        # 변경: 다양한 입력 표현을 등급 Enum과 bool로 통일합니다.
        # frozen 객체의 초기화 단계에서만 object.__setattr__을 사용합니다.
        # 생성 후에는 속성 변경을 막아 검증된 상태를 유지합니다.
        object.__setattr__(self, "u_type", CustomerType(self.u_type))
        object.__setattr__(self, "coupon", self._normalize_coupon(self.coupon))

    def _validate_inputs(self) -> None:
        """이 주문의 등급, 단가, 수량을 검사하는 내부 메서드입니다."""
        # bool은 int의 하위 타입이므로 숫자 검사에서 명시적으로 제외합니다.
        if isinstance(self.u_type, bool) or not isinstance(self.u_type, int):
            raise TypeError("u_type은 정수 등급이어야 합니다.")
        if self.u_type not in DISCOUNT_PERCENT:
            raise ValueError("u_type은 0, 1, 2, 3 중 하나여야 합니다.")

        for name, value in (("price", self.price), ("qty", self.qty)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name}는 정수여야 합니다.")
        if self.price < 0:
            raise ValueError("price는 0 이상이어야 합니다.")
        if self.qty <= 0:
            raise ValueError("qty는 1 이상이어야 합니다.")

    @staticmethod
    def _normalize_coupon(coupon: bool | str) -> bool:
        """객체 속성을 사용하지 않는 변환 로직이므로 정적 메서드로 둡니다."""
        if isinstance(coupon, bool):
            return coupon
        if isinstance(coupon, str):
            normalized = coupon.strip().upper()
            if normalized not in ("YES", "NO"):
                raise ValueError("coupon 문자열은 YES 또는 NO여야 합니다.")
            return normalized == "YES"
        raise TypeError("coupon은 bool 또는 YES/NO 문자열이어야 합니다.")

    def calculate_total(self) -> int:
        """등급 할인 → 쿠폰 차감 → 최저 0원 → 원 미만 버림 순서로 계산합니다."""
        # 변경: 인수를 다시 받지 않고 self에 저장된 주문 정보를 사용합니다.
        # 1/100원 단위의 정수로 계산해 float의 정밀도 문제를 피합니다.
        total_hundredths = (
            self.price * self.qty * (100 - DISCOUNT_PERCENT[self.u_type])
        )
        if self.coupon:
            total_hundredths -= COUPON_AMOUNT * 100
        # 계산 과정에서 객체 속성을 바꾸지 않으므로 반복 호출 결과도 같습니다.
        return max(0, total_hundredths) // 100


if __name__ == "__main__":
    # 기존: calc_order(1, 100, 20, "Yes")
    # 변경: 주문 객체를 생성한 다음 그 객체의 계산 메서드를 호출합니다.
    order = Order(
        u_type=CustomerType.DISCOUNT_5,
        price=100,
        qty=20,
        coupon="Yes",
    )
    print(f"최종 결제 금액: {order.calculate_total():,}원")
