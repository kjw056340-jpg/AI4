"""실행: python -m unittest -v"""

import unittest
from fastapi.testclient import TestClient
from main import app


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def values(self, first, second):
        response = self.client.get("/calculate", params={"first": first, "second": second})
        self.assertEqual(response.status_code, 200)
        import re
        return re.findall(r"<dd>(.*?)</dd>", response.text)

    def test_home_and_stylesheet(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn('lang="ko"', response.text)
        self.assertEqual(self.client.get("/static/style.css").status_code, 200)

    def test_four_operations(self):
        self.assertEqual(self.values("12", "4"), ["16", "8", "48", "3"])

    def test_decimal_precision(self):
        self.assertEqual(self.values("0.1", "0.2"), ["0.3", "-0.1", "0.02", "0.5"])

    def test_negatives(self):
        self.assertEqual(self.values("-3", "2"), ["-1", "-5", "-6", "-1.5"])

    def test_zero_divisor_preserves_other_results(self):
        for zero in ("0", "-0", "0.00"):
            with self.subTest(zero=zero):
                self.assertEqual(self.values("5", zero), ["5", "5", "0", "0으로 나눌 수 없습니다."])

    def test_recurring_decimal(self):
        self.assertEqual(self.values("1", "3")[-1], "0." + "3" * 64)

    def test_whitespace(self):
        self.assertEqual(self.values(" 2 ", " .5 "), ["2.5", "1.5", "1", "4"])

    def test_invalid_inputs(self):
        for invalid in ("", " ", "abc", "NaN", "Infinity", "1e5", "1,000", "1" * 31, "1.2.3"):
            for field in ("first", "second"):
                with self.subTest(invalid=invalid, field=field):
                    params = {"first": "1", "second": "2", field: invalid}
                    response = self.client.get("/calculate", params=params)
                    self.assertEqual(response.status_code, 400)
                    self.assertIn('role="alert"', response.text)
                    self.assertNotIn("<dd>", response.text)

    def test_missing_inputs(self):
        self.assertEqual(self.client.get("/calculate").status_code, 400)

    def test_html_is_escaped(self):
        response = self.client.get("/calculate", params={"first": '<script>alert(1)</script>', "second": "2"})
        self.assertEqual(response.status_code, 400)
        self.assertNotIn("<script>", response.text)
        self.assertIn("&lt;script&gt;", response.text)

    def test_largest_inputs(self):
        number = "9" * 30
        self.assertEqual(self.values(number, number), [str(int(number) * 2), "0", str(int(number) ** 2), "1"])


if __name__ == "__main__":
    unittest.main()
