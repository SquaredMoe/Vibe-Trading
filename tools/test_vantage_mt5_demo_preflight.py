"""Offline contract tests for the read-only Vantage MT5 demo preflight."""

import unittest

from tools.vantage_mt5_demo_preflight import assess_readiness


class VantageDemoPreflightTests(unittest.TestCase):
    def setUp(self):
        self.status = {
            "status": "ok",
            "config": {"profile": "paper", "password": "***redacted***"},
            "account": {
                "login": 12345678,
                "trade_mode": 0,
                "is_demo": True,
                "server": "Vantage-Demo",
            },
        }
        self.quote = {
            "status": "ok",
            "resolved_symbol": "EURUSD",
            "quote": {"bid": 1.082, "ask": 1.083},
        }
        self.history = {"status": "ok", "bars": [{"close": 1.082}]}

    def check(self, expected_server=""):
        return assess_readiness(
            self.status,
            self.quote,
            self.history,
            expected_server=expected_server,
        )

    def test_valid_vantage_demo_is_ready(self):
        result = self.check()
        self.assertTrue(result["ready_for_demo_testing"])
        self.assertEqual(result["symbol"], "EURUSD")
        self.assertFalse(result["execution_enabled_by_this_script"])
        self.assertNotIn("login", result)
        self.assertNotIn("password", result)

    def test_real_account_never_passes(self):
        self.status["account"]["trade_mode"] = 2
        self.status["account"]["is_demo"] = False
        self.assertFalse(self.check()["ready_for_demo_testing"])

    def test_live_profile_never_passes_even_on_demo(self):
        self.status["config"]["profile"] = "live"
        self.assertFalse(self.check()["ready_for_demo_testing"])

    def test_failed_login_guard_never_passes(self):
        self.status["status"] = "error"
        self.assertFalse(self.check()["ready_for_demo_testing"])

    def test_wrong_broker_server_does_not_pass(self):
        self.status["account"]["server"] = "AnotherBroker-Demo"
        self.assertFalse(self.check()["ready_for_demo_testing"])

    def test_exact_server_pin(self):
        self.assertTrue(self.check("vantage-demo")["ready_for_demo_testing"])
        self.assertFalse(self.check("Vantage-OtherDemo")["ready_for_demo_testing"])

    def test_invalid_quote_does_not_pass(self):
        self.quote["quote"]["ask"] = float("nan")
        self.assertFalse(self.check()["ready_for_demo_testing"])

    def test_no_history_does_not_pass(self):
        self.history["bars"] = []
        self.assertFalse(self.check()["ready_for_demo_testing"])


if __name__ == "__main__":
    unittest.main()
