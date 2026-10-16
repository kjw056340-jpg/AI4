import math
import warnings
from collections.abc import Iterable, Mapping


def preprocess_legacy(data: Iterable[Mapping]) -> list[float]:
    """0~100점인 유효한 행만 정규화하여 입력 순서대로 반환합니다.

    score는 float로 변환 가능한 값이며, bool은 허용하지 않습니다.
    잘못된 행은 건너뛰고 1부터 시작하는 행 번호와 원인을 경고합니다.
    건너뛴 행은 결과에 포함되지 않으므로 입력과 결과의 길이는 다를 수 있습니다.
    data 자체가 행들의 반복 가능한 묶음이 아니면 TypeError를 발생시킵니다.
    이터레이터는 처리 중 소비되며, 입력 리스트와 행은 직접 수정하지 않습니다.
    """
    # 수정: 문자열이나 단일 딕셔너리를 행들의 묶음으로 오인하지 않습니다.
    if isinstance(data, (str, bytes, bytearray, Mapping)):
        raise TypeError("data에는 단일 값 대신 행들의 리스트 또는 이터레이터를 전달하세요.")
    try:
        rows = iter(data)
    except TypeError as exc:
        raise TypeError("data는 행들의 반복 가능한 묶음이어야 합니다.") from exc

    result = []
    for row_number, row in enumerate(rows, start=1):
        reason = None

        # 수정: 행의 구조, 필수 키, bool 여부를 숫자 변환 전에 확인합니다.
        if not isinstance(row, Mapping):
            reason = "행은 딕셔너리 형태여야 합니다."
        elif "score" not in row:
            reason = "score 키가 없습니다."
        elif isinstance(row["score"], bool):
            reason = "bool은 점수로 사용할 수 없습니다."
        else:
            try:
                score = float(row["score"])
            except (TypeError, ValueError, OverflowError):
                # 수정: N/A, None, 지나치게 큰 정수 등으로 전체 처리가 중단되지 않습니다.
                reason = "score를 실수로 변환할 수 없습니다."
            else:
                # 수정: NaN과 무한대는 범위 검사와 별개로 명시적으로 거부합니다.
                if not math.isfinite(score):
                    reason = "score는 NaN이나 무한대가 아닌 유한한 숫자여야 합니다."
                elif not 0 <= score <= 100:
                    reason = "score는 0 이상 100 이하여야 합니다."

        # 수정: 오류가 있는 행만 제외하고, 행 번호와 사유를 호출자에게 알립니다.
        if reason is not None:
            warnings.warn(f"{row_number}번째 행 제외: {reason}", UserWarning, stacklevel=2)
            continue

        # 기존 호환성 유지: 소수점 넷째 자리까지 반올림합니다.
        # 이 정밀도에서는 0.004점 → 0.0, 99.999점 → 1.0이 될 수 있습니다.
        result.append(round(score / 100.0, 4))

    return result


# 수정: 직접 실행할 때만 정상 입력과 잘못된 입력이 섞인 예제를 확인합니다.
if __name__ == "__main__":
    sample = [
        {"score": 0},
        {"score": "85.5"},
        {},
        {"score": "N/A"},
        {"score": 120},
        {"score": "nan"},
        {"score": True},
        {"score": 100},
    ]
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        normalized = preprocess_legacy(sample)
    print("정규화 결과:", normalized)
    print("제외된 행 수:", len(caught))
    for warning in caught:
        print(warning.message)
