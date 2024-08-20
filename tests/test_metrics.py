import unittest
from prometheus_client import CollectorRegistry
from prometheus_client.exposition import generate_latest
from metrics import rows_processed, rows_cleaned, data_quality_issues, start_metrics_server

class TestMetrics(unittest.TestCase):

    def setUp(self):
        self.registry = CollectorRegistry()
        rows_processed.remove(self.registry)
        rows_cleaned.remove(self.registry)
        data_quality_issues.remove(self.registry)

    def test_metrics_initial(self):
        # Start metrics server in test mode
        start_metrics_server(port=8000)

        # Set some metrics
        rows_processed.set(100)
        rows_cleaned.set(90)
        data_quality_issues.set(1)

        # Generate and check metrics
        metrics = generate_latest(self.registry)
        self.assertIn(b'rows_processed 100', metrics)
        self.assertIn(b'rows_cleaned 90', metrics)
        self.assertIn(b'data_quality_issues 1', metrics)

if __name__ == '__main__':
    unittest.main()
