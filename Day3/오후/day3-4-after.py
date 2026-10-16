"""방어적 검증과 구조화된 전처리 보고서. 기존 두 버전은 비교용으로 보존합니다."""

import math
from collections import Counter
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from statistics import fmean


class InputValidationError(TypeError):
    """입력 묶음이 잘못되었거나 순회를 끝내지 못한 경우입니다."""


class ScoreValidationError(ValueError):
    """행 검증 실패. code는 통계 집계와 프로그램의 분기 처리에 사용합니다."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class RowIssue:
    row_number: int
    error: ScoreValidationError


@dataclass(frozen=True)
class After:
    """전처리 결과와 통계. values와 issues는 원본 입력 순서를 따릅니다.

    직렬화된 보고서에는 원본 행을 포함하지 않습니다.
    오류의 __cause__로 변환 실패 원인을 조사할 수 있습니다.
    반올림 정책은 기존과 같은 소수점 넷째 자리입니다.
    """

    values: tuple[float, ...]
    issues: tuple[RowIssue, ...]

    @property
    def accepted(self) -> int:
        return len(self.values)

    @property
    def rejected(self) -> int:
        return len(self.issues)

    @property
    def total(self) -> int:
        # 수정: 개수를 중복 저장하지 않아 total = accepted + rejected가 항상 성립합니다.
        return self.accepted + self.rejected

    @property
    def acceptance_rate(self) -> float | None:
        # 수정: 빈 입력의 비율은 계산할 수 없으므로 0% 대신 None으로 표현합니다.
        return self.accepted / self.total if self.total else None

    def to_dict(self) -> dict:
        """JSON으로 저장 가능한 보고서. 평균/최솟값/최댓값은 정규화된 결과 기준입니다."""
        return {
            "values": list(self.values),
            "total": self.total,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "acceptance_rate": self.acceptance_rate,
            "mean": fmean(self.values) if self.values else None,
            "min": min(self.values) if self.values else None,
            "max": max(self.values) if self.values else None,
            "rejected_by_code": dict(Counter(issue.error.code for issue in self.issues)),
            "issues": [
                {
                    "row_number": issue.row_number,
                    "code": issue.error.code,
                    "message": str(issue.error),
                    "cause_type": (
                        type(issue.error.__cause__).__name__
                        if issue.error.__cause__ is not None else None
                    ),
                }
                for issue in self.issues
            ],
        }


def validate_score(row: object) -> float:
    """방어적 검증기: 유효한 0~100점만 반환하고 정규화는 수행하지 않습니다."""
    if not isinstance(row, Mapping):
        raise ScoreValidationError("row_type", "행은 딕셔너리 형태여야 합니다.")

    # 수정: 누락 키의 원래 KeyError를 예외 체인에 보존합니다.
    try:
        raw_score = row["score"]
    except KeyError as exc:
        raise ScoreValidationError("missing_score", "score 키가 없습니다.") from exc

    if isinstance(raw_score, bool):
        raise ScoreValidationError("boolean", "bool은 점수로 사용할 수 없습니다.")
    try:
        score = float(raw_score)
    except (TypeError, ValueError, OverflowError) as exc:
        # 수정: 사용자용 설명과 디버깅에 필요한 원래 예외를 함께 보존합니다.
        raise ScoreValidationError("conversion", "score를 실수로 변환할 수 없습니다.") from exc

    if not math.isfinite(score):
        raise ScoreValidationError("non_finite", "score는 유한한 숫자여야 합니다.")
    if not 0 <= score <= 100:
        raise ScoreValidationError("out_of_range", "score는 0 이상 100 이하여야 합니다.")
    return score


def validate_data(data: object) -> Iterator:
    """단일 딕셔너리/문자열과 반복 불가능한 값을 입력 경계에서 거부합니다."""
    if isinstance(data, (str, bytes, bytearray, Mapping)):
        raise InputValidationError("data에는 행들의 리스트 또는 이터레이터를 전달하세요.")
    try:
        return iter(data)
    except TypeError as exc:
        raise InputValidationError("data는 반복 가능한 묶음이어야 합니다.") from exc


def preprocess(data: object) -> After:
    """잘못된 행은 보고서에 기록하고, 유효한 행은 계속 처리합니다.

    입력 이터레이터 자체가 고장 나면 불완전한 보고서를 반환하지 않고 예외를 냅니다.
    이터레이터는 소비됩니다. 원본 리스트/딕셔너리는 직접 수정하지 않습니다.
    """
    rows = validate_data(data)
    values = []
    issues = []
    row_number = 0
    while True:
        try:
            row = next(rows)
        except StopIteration:
            break
        except Exception as exc:
            # 수정: 순회 실패는 잘못된 점수와 구분하고, 원인과 실패 위치를 보존합니다.
            raise InputValidationError(
                f"{row_number}개 행을 읽은 뒤 다음 행을 읽지 못했습니다."
            ) from exc

        row_number += 1
        try:
            score = validate_score(row)
        except ScoreValidationError as exc:
            # 수정: 전역 경고 설정에 의존하지 않고 오류를 명시적인 결과로 반환합니다.
            issues.append(RowIssue(row_number, exc))
        else:
            # 기존 정책 유지: 0.004점 → 0.0, 99.999점 → 1.0이 될 수 있습니다.
            values.append(round(score / 100.0, 4))

    return After(tuple(values), tuple(issues))


if __name__ == "__main__":
    import json

    sample = [{"score": 0}, {"score": "85.5"}, {}, {"score": "N/A"},
              {"score": 120}, {"score": "nan"}, {"score": True}, {"score": 100}]
    print(json.dumps(preprocess(sample).to_dict(), ensure_ascii=False, indent=2, allow_nan=False))
