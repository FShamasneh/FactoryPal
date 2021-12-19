import unittest
import analyzer
import numpy as np
import sys
sys.path.append('../')

class TestAnalyzer(unittest.TestCase):

    def test_normalizer(self):
        self.assertRaises(ValueError, analyzer.normalizer, [1, 1, 1, 1, 1])
        input = [123, 32, 1, 23, 45, 6]
        result = analyzer.normalizer(input)
        self.assertEqual(round(np.mean(result)), 0)
        self.assertEqual(round(np.std(result)), 1)

    def test_get_dicts_out_of_data(self):
        sample_input = '{"product":{"0":[1,2],"1":[32,12]}}' \
                       '{"id":{"19":[123,321],"31":[12,32]}}'
        # expected_out = ({'product': {'0': [1, 2], '1': [32, 12]}}, {'id': {'19': [123, 321], '31': [12, 32]}})
        result = analyzer.get_dicts_out_of_data(sample_input)
        self.assertEqual(result[0]['product']['0'][0], 1)
        self.assertEqual(result[0]['product']['0'][1], 2)
        self.assertEqual(result[1]['id']['19'][0], 123)

    def test_get_values_per_stream(self):
        sample_input = [(12, 32), (123, 32), (65, 7), (95, 43)]
        expected_out = [32, 32, 7, 43]
        result = analyzer.get_values_per_stream(sample_input)
        cnt = 0
        while cnt < len(expected_out):
            self.assertEqual(result[cnt], expected_out[cnt])
            cnt += 1

    def test_get_time_per_stream(self):
        sample_input = [(12, 32), (123, 32), (65, 7), (95, 43)]
        expected_out = [12, 123, 65, 95]
        result = analyzer.get_time_per_stream(sample_input)
        cnt = 0
        while cnt < len(expected_out):
            self.assertEqual(result[cnt], expected_out[cnt])
            cnt += 1

    def test_get_top_n(self):
        sorted_input = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = analyzer.get_top_n(sorted_input)
        cnt = 0
        input_len = len(sorted_input) - 1
        while cnt < len(result):
            self.assertEqual(result[cnt], sorted_input[ input_len - cnt])
            cnt += 1

    def test_sort_list_of_correlations(self):
        unsorted_input = [(21, 2), (32, 1), (42, 4), (1, 3), (42, 5)]
        test_expected_out = [1, 2, 3, 4, 5]
        result = analyzer.sort_list_tuples_of_correlations(unsorted_input)
        cnt = 0
        while cnt < len(unsorted_input):
            self.assertEqual(result[cnt][1], test_expected_out[cnt])
            cnt += 1

if __name__ == 'main':
    unittest.main()
