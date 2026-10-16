from abc import abstractmethod

class PaymentGateway:
    @abstractmethod
    def process_payment(self, item:str, amount:int) -> str:
        pass

class CreditCardGateway(PaymentGateway):
    def process_payment(self, item:str,amount:int) -> str:
            return f'구매품목2 : {item} 수량2 : {amount}'

class BankGateway(PaymentGateway):
    pass

for obj in [CreditCardGateway(), BankGateway()]:
    print(obj.process_payment('식료품',100))