from abc import ABC, abstractmethod
from dataclasses import dataclass
@dataclass
class PaymentReceipt:
    method: str
    buyer: str
    amount: int
    fee: int
    status: str
    @property
    def net_amount(self) -> int:
        return self.amount - self.fee

obj = PaymentReceipt('card','홍길동',100,5,'normal')
print(obj.net_amount)