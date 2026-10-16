class BaseAIModel:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    def predict(self, input_data: str) -> str:
        return f"[{self.name} v{self.version}] 기본 추론: {input_data}"
class VisionClassifier(BaseAIModel):
    def __init__(self, name: str, version: str, resolution: str):
        super().__init__(name, version)  # 부모 초기화 코드 재사용        
        self.resolution = resolution
    def predict(self, input_data: str) -> str:  # 다형성 오버라이딩        
       return f"[Vision {self.name} ({self.resolution})] 이미지 '{input_data}' 분석 결과 -> '고양이 (확률 98.4%)'"
class TextSummarizerLLM(BaseAIModel):
    def __init__(self, name: str, version: str, max_tokens: int):
        super().__init__(name, version)
        self.max_tokens = max_tokens
    def predict(self, input_data: str) -> str:  # 다형성 오버라이딩        
        summary = input_data[:18] + "..." if len(input_data) > 18 else input_data
        return f"[LLM {self.name} (max={self.max_tokens})] 텍스트 요약 결과 -> '{summary}'"

pipeline=[BaseAIModel('base','1.0'),VisionClassifier('vision','1.0','1024'),TextSummarizerLLM('textsumarizer','1.0',10000000)]
for obj in pipeline:
    print(obj.predict("테스트"))
