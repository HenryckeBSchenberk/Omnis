from src.nodes.serial.gcode import GCODE, PARSER, package
import unittest

class GCODE_UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gcode = GCODE
        
    def test_GOCDE_G0(self):
        self.assertEqual(self.gcode.G0(('X',0), ('Y',2), ('Z', 0.1), ('E', -2)).data, 'G0 X0.0 Y2.0 Z0.1 E-2.0 ')

    def test_GOCDE_G1(self):
        self.assertEqual(self.gcode.G1(('X',0), ('Y',2), ('Z', 0.1), ('E', -2)).data, 'G1 X0.0 Y2.0 Z0.1 E-2.0 ')
    
    def test_GOCDE_M42(self):
        self.assertEqual(self.gcode.M42(1, 1).data, 'M42 P1 S1')
    
    def test_GOCDE_M114(self):
        self.assertEqual(self.gcode.M114().data, 'M114 ')

    def test_GOCDE_M114_R(self):
        self.assertEqual(self.gcode.M114('R').data, 'M114 R')
    
    def test_GOCDE_M119(self):
        self.assertEqual(self.gcode.M119().data, 'M119')
    
    def test_GOCDE_G28(self):
        self.assertEqual(self.gcode.G28('X','Y').data, 'G28 X Y')

class PARSER_UnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.parser = PARSER
    
    def test_PARSER_M114(self):
        self.assertEqual(self.parser.M114(package(['X:0.00 Y:0.00 Z:0.00 E:0.00 Count X:420 Y:400 Z:20', 'ok'])), {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'E': 0.0})

    def test_PARSER_M119(self):
        self.assertTrue(
            self.parser.M119(
                package(
                    [
                        'Reporting endstop status',
                        'x_min: open',
                        'x2_min: open',
                        'y_min: open',
                        'z_min: open',
                        'ok'
                    ]
                ),
                {'x_min': 'open', 'x2_min': 'open', 'y_min': 'open', 'z_min': 'open'},
                True
            )
        )

        self.assertFalse(
            self.parser.M119(
                package(
                    [
                        'Reporting endstop status',
                        'x_min: open',
                        'x2_min: open',
                        'y_min: open',
                        'z_min: open',
                        'ok'
                    ]
                ),
                {'x_min': 'open', 'x2_min': 'open', 'y_min': 'open', 'z_min': 'triggered'},
                True
            )
        )
