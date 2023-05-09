import unittest

from daktari.result_printer import progress_bar


class TestResultPrinter(unittest.TestCase):
    def test_progress_bar(self):
        self.assertEqual(progress_bar(0, 50), "Progress: [>                        ] 0%  (0/50)")
        self.assertEqual(progress_bar(5, 50), "Progress: [->                       ] 10%  (5/50)")
        self.assertEqual(progress_bar(10, 40), "Progress: [----->                   ] 25%  (10/40)")
        self.assertEqual(progress_bar(20, 40), "Progress: [----------->             ] 50%  (20/40)")
        self.assertEqual(progress_bar(20, 37), "Progress: [------------>            ] 54%  (20/37)")
        self.assertEqual(progress_bar(30, 40), "Progress: [----------------->       ] 75%  (30/40)")
        self.assertEqual(progress_bar(40, 40), "Progress: [------------------------>] 100%  (40/40)")
