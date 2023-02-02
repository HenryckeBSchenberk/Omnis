from src.nodes.serial.gcode import GCODE, PARSER, package
import unittest

class TestGCODE(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gcode = GCODE
        
    def test_gcode_G0(self):
        """[GCODE] Criando comando G0"""
        self.assertEqual(self.gcode.G0(('X',0), ('Y',2), ('Z', 0.1), ('E', -2)).data, 'G0 X0.0 Y2.0 Z0.1 E-2.0 ')

    def test_gcode_G1(self):
        """[GCODE] Criando comando G1"""
        self.assertEqual(self.gcode.G1(('X',0), ('Y',2), ('Z', 0.1), ('E', -2)).data, 'G1 X0.0 Y2.0 Z0.1 E-2.0 ')
    
    def test_gcode_M42(self):
        """[GCODE] Criando comando M42"""
        self.assertEqual(self.gcode.M42(1, 1).data, 'M42 P1 S1')
    
    def test_gcode_M114(self):
        """[GCODE] Criando comando M114"""
        self.assertEqual(self.gcode.M114().data, 'M114 ')

    def test_gcode_M114_R(self):
        """[GCODE] Criando comando M114 R"""
        self.assertEqual(self.gcode.M114('R').data, 'M114 R')
    
    def test_gcode_M119(self):
        """[GCODE] Criando comando M119"""
        self.assertEqual(self.gcode.M119().data, 'M119')
    
    def test_gcode_G28(self):
        """[GCODE] Criando comando G28"""
        self.assertEqual(self.gcode.G28('X','Y').data, 'G28 X Y')

class TestGcodeParser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.parser = PARSER
    
    def test_gcode_parser_M114(self):
        """[GCODE_PARSER] Formatando retorno de pacote M114"""
        self.assertEqual(self.parser.M114(package(['X:0.00 Y:0.00 Z:0.00 E:0.00 Count X:420 Y:400 Z:20', 'ok'])), {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'E': 0.0})

    def test_gcode_parser_M119(self):
        """[GCODE_PARSER] Formatando retorno de pacote M119"""
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
