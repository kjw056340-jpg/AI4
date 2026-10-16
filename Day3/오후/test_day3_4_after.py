"""실행: python test_day3_4_after.py. 기능 검증 후 동일 데이터의 전후 지표를 출력합니다."""

import copy
import importlib.util
import json
import sys
import unittest
import warnings
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


after = load_module("day3_4_after", "day3-4-after.py")
legacy = load_module("day3_4_legacy", "day3-4.py").preprocess_legacy
fixed = load_module("day3_4_fixed", "day3-4-fixed.py").preprocess_legacy

VALID = [{"score": 0}, {"score": "85.5"}, {"score": 100}, {"score": " 50 "}]
EXPECTED = [0.0, 0.855, 1.0, 0.5]
INVALID = [
    ({}, "missing_score", KeyError),
    ({"score": "N/A"}, "conversion", ValueError),
    ({"score": None}, "conversion", TypeError),
    (None, "row_type", None),
    ({"score": -10}, "out_of_range", None),
    ({"score": 120}, "out_of_range", None),
    ({"score": "nan"}, "non_finite", None),
    ({"score": "inf"}, "non_finite", None),
    ({"score": "-inf"}, "non_finite", None),
    ({"score": "1e309"}, "non_finite", None),
    ({"score": True}, "boolean", None),
    ({"score": False}, "boolean", None),
    ({"score": 10**400}, "conversion", OverflowError),
    ({"score": ""}, "conversion", ValueError),
    ({"score": []}, "conversion", TypeError),
    ({"score": {}}, "conversion", TypeError),
]
MIXED = VALID + [row for row, _, _ in INVALID]


class PreprocessTests(unittest.TestCase):
    def test_normal_results_match_both_previous_versions(self):
        self.assertEqual(list(after.preprocess(VALID).values), EXPECTED)
        self.assertEqual(legacy(VALID), EXPECTED)
        self.assertEqual(fixed(VALID), EXPECTED)

    def test_validator_codes_and_exception_chains(self):
        for row, code, cause_type in INVALID:
            with self.subTest(code=code, row_type=type(row).__name__):
                with self.assertRaises(after.ScoreValidationError) as caught:
                    after.validate_score(row)
                self.assertEqual(caught.exception.code, code)
                if cause_type is None:
                    self.assertIsNone(caught.exception.__cause__)
                else:
                    self.assertIsInstance(caught.exception.__cause__, cause_type)
                    self.assertTrue(caught.exception.__suppress_context__)

    def test_mixed_report_counts_positions_and_statistics(self):
        report = after.preprocess(MIXED)
        self.assertEqual(report.total, 20)
        self.assertEqual(report.accepted, 4)
        self.assertEqual(report.rejected, 16)
        self.assertEqual(report.acceptance_rate, 0.2)
        self.assertEqual([issue.row_number for issue in report.issues], list(range(5, 21)))
        data = report.to_dict()
        self.assertAlmostEqual(data['mean'], 0.58875)
        self.assertEqual((data['min'], data['max']), (0.0, 1.0))
        self.assertEqual(data['rejected_by_code'], {
            'missing_score': 1, 'conversion': 6, 'row_type': 1,
            'out_of_range': 2, 'non_finite': 4, 'boolean': 2,
        })

    def test_empty_and_all_invalid_statistics(self):
        for rows in ([], [row for row, _, _ in INVALID]):
            with self.subTest(size=len(rows)):
                report = after.preprocess(rows)
                data = report.to_dict()
                self.assertEqual(data['values'], [])
                for key in ('mean', 'min', 'max'):
                    self.assertIsNone(data[key])
                self.assertEqual(report.acceptance_rate, 0.0 if rows else None)

    def test_bad_container_and_cause(self):
        for data in (None, 3, '85', b'85', bytearray(b'85'), {'score': 85}):
            with self.subTest(data_type=type(data).__name__):
                with self.assertRaises(after.InputValidationError) as caught:
                    after.preprocess(data)
                if data is None or data == 3:
                    self.assertIsInstance(caught.exception.__cause__, TypeError)

    def test_generator_continues_after_invalid_row(self):
        report = after.preprocess(iter([{'score': 80}, {}, {'score': 90}]))
        self.assertEqual(report.values, (0.8, 0.9))
        self.assertEqual(report.issues[0].row_number, 2)

    def test_broken_iterator_has_chained_error(self):
        def broken():
            yield {'score': 80}
            raise RuntimeError('source failed')
        with self.assertRaises(after.InputValidationError) as caught:
            after.preprocess(broken())
        self.assertIsInstance(caught.exception.__cause__, RuntimeError)
        self.assertIn('1개 행', str(caught.exception))

    def test_input_is_not_mutated(self):
        original = copy.deepcopy(MIXED)
        after.preprocess(MIXED)
        self.assertEqual(MIXED, original)

    def test_report_is_json_serializable_without_nonfinite_numbers(self):
        encoded = json.dumps(after.preprocess(MIXED).to_dict(), allow_nan=False)
        self.assertEqual(json.loads(encoded)['rejected'], 16)

    def test_rounding_policy_is_preserved(self):
        rows = [{'score': 0.004}, {'score': 99.999}]
        self.assertEqual(list(after.preprocess(rows).values), legacy(rows))

    def test_warning_as_error_does_not_interrupt_after(self):
        with warnings.catch_warnings():
            warnings.simplefilter('error')
            with self.assertRaises(UserWarning):
                fixed([{}, {'score': 80}])
            self.assertEqual(after.preprocess([{}, {'score': 80}]).values, (0.8,))

    def test_unexpected_validator_bug_is_not_silently_skipped(self):
        class BrokenRow(dict):
            def __getitem__(self, key):
                raise RuntimeError('unexpected mapping failure')
        with self.assertRaises(RuntimeError):
            after.preprocess([BrokenRow(score=80)])


def compare_quality():
    """시간 측정이 아닌, 고정된 20행에 대한 정확성/진단 가능성 지표입니다."""
    metrics = {}
    for name, function in [('legacy', legacy), ('fixed', fixed), ('after', after.preprocess)]:
        rejected = 0
        for row, _, _ in INVALID:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    output = function([row])
                values = output.values if isinstance(output, after.After) else output
                rejected += len(values) == 0
            except (KeyError, TypeError, ValueError, OverflowError):
                rejected += 1

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            try:
                output = function(MIXED)
                completed = True
                returned = len(output.values if isinstance(output, after.After) else output)
            except (KeyError, TypeError, ValueError, OverflowError):
                output, completed, returned = None, False, 0
        metrics[name] = {
            'invalid_rows_rejected_individually': f'{rejected}/16',
            'mixed_batch_completed': completed,
            'valid_results_returned': f'{returned}/4',
            'warnings_in_mixed_batch': len(caught),
            'structured_issues': len(output.issues) if isinstance(output, after.After) else 0,
            'preserved_causes': (
                sum(issue.error.__cause__ is not None for issue in output.issues)
                if isinstance(output, after.After) else None
            ),
        }
    assert metrics['legacy']['invalid_rows_rejected_individually'] == '8/16'
    assert metrics['fixed']['invalid_rows_rejected_individually'] == '16/16'
    assert metrics['after']['invalid_rows_rejected_individually'] == '16/16'
    assert metrics['after']['preserved_causes'] == 7
    return metrics


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(PreprocessTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        sys.exit(1)
    print(json.dumps(compare_quality(), ensure_ascii=False, indent=2))
