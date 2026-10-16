class BaristaBot:
    #생성자
    def __init__(self, bot_name: str, bean_grams: int):
        self.bot_name = bot_name
        self.bean_grams = bean_grams
        self.total_cups = 0
    def brew_espresso(self, cups: int = 1) -> str:
        required_beans = cups * 18
        if self.bean_grams < required_beans:
            return f"[{self.bot_name}] 원두부족! (필요: {required_beans}g, 현재: {self.bean_grams}g)"
        self.bean_grams -= required_beans
        self.total_cups += cups
        return f"[{self.bot_name}] 에스프레소 {cups}잔 추출 완료! (남은 원두: {self.bean_grams}g, 누적: {self.total_cups}잔)"

bot = BaristaBot("코덱스바리스타-1호", 50)
print(bot.brew_espresso(2))
print(bot.brew_espresso(2))

bot2= BaristaBot('알바생',100)
print(bot2.brew_espresso(3))
print(bot2.brew_espresso(2))
print(bot2.brew_espresso(10))
print(bot2.brew_espresso(5))
