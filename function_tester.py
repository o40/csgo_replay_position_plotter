import unittest
import posplotter


class TestPosPlotterFunctions(unittest.TestCase):

    def test_calculate_zoom_parameters(self):
        extent = [0, 1000, 0, 1000]
        zoom_arg = '10,20,10'

        expected_area = [100, 200, 200, 300]
        calculated_area = posplotter.calculate_zoom_parameters(zoom_arg, extent)
        self.assertEqual(calculated_area, expected_area)


if __name__ == '__main__':
    unittest.main()
