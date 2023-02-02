import unittest
from src.nodes.matrix.matrix_obj import Blister
from src.manager.matrix_manager import MatrixManager as Manager
from bson import ObjectId
import numpy as np
import itertools
from src.test import users

class TestMatrix(unittest.TestCase):
    def setUp(self):
        self._id = ObjectId()
        self.descritor = {
            "_id": self._id,
            "name": "Teste",
            "slots": {
                "qtd": {
                    "x": 3,
                    "y": 3
                },
                "margin": {
                    "x": 0.28,
                    "y": 3.35
                },
                "size": {
                    "x": 5.137,
                    "y": 2.324
                }
            },
            "subdivisions": {
                "qtd": {
                    "x": 1,
                    "y": 1
                },
                "margin": {
                    "x": 0,
                    "y": 0
                }
            },
            "description": "Teste",
            "origin": {
                "x": 5,
                "y": 5
            },
            "order": "TLR",
            "part_number": "Teste",
        }
        self.Matrix = Blister(self.descritor)
        Manager.create(
            _id=self._id,
            input=self.descritor,
            user=users['dev']
        )
    def tearDown(self):
        Manager.delete(_id=self._id, user=users['dev'])
    
    def test_matrix_pattern(self):
        """[Matrix] Testando o padrão de criação da matriz"""
        self.assertIsInstance(self.Matrix, Blister)
        self.assertIsInstance(self.Matrix._id, ObjectId)
        self.assertIsInstance(self.Matrix.name, str)

    def test_matrix_slots_centers(self):
        """[Matrix] Testando os centros dos slots"""
        correct=np.array([
            [[7.5685,  6.162 ],[12.9855, 6.162 ],[18.4025, 6.162 ]],
            [[ 7.5685, 11.836],[12.9855, 11.836],[18.4025, 11.836]],
            [[ 7.5685, 17.51 ],[12.9855, 17.51 ],[18.4025, 17.51 ]],
        ])

        for x, y in itertools.product(range(3), repeat=2):
            self.assertIsNone(np.testing.assert_allclose(self.Matrix(x,y).center, correct[x, y]))
    
    def matrix_order_test(self, order, expected_order):
        self.Matrix.data = self.Matrix.re_order(self.Matrix.generate_data(self.Matrix.shape, **self.Matrix.slot_config), order)
        for x, y in itertools.product(range(3), repeat=2):
            self.assertEqual(self.Matrix(x,y).position.tolist(), expected_order[x, y].tolist())

    def test_matrix_order_TLR(self):
        """[Matrix] Testando a ordem TLR - Top Left Right"""
        TLR = np.array([
            [[0, 0], [0, 1], [0, 2]],
            [[1, 0], [1, 1], [1, 2]],
            [[2, 0], [2, 1], [2, 2]],
        ])
        self.matrix_order_test("TLR", TLR)
    
    def test_matrix_order_TRB(self):
        """[Matrix] Testando a ordem TRB - Top Right Bottom"""
        TRB = np.array([
            [[0, 2], [1, 2], [2, 2]],
            [[0, 1], [1, 1], [2, 1]],
            [[0, 0], [1, 0], [2, 0]]
        ])
        self.matrix_order_test("TRB", TRB)

    def test_matrix_order_BLU(self):
        """[Matrix] Testando a ordem BLU - Bottom Left Up"""
        BLU = np.array([
            [[2, 0], [1, 0], [0, 0]],
            [[2, 1], [1, 1], [0, 1]],
            [[2, 2], [1, 2], [0, 2]]
        ])
        self.matrix_order_test("BLU", BLU)

    def test_matrix_order_TRL(self):
        """[Matrix] Testando a ordem TRL - Top Right Left"""
        TRL = np.array([
            [[0, 2], [0, 1], [0, 0]],
            [[1, 2], [1, 1], [1, 0]],
            [[2, 2], [2, 1], [2, 0]]
        ])
        self.matrix_order_test("TRL", TRL)

    def test_matrix_order_TLB(self):
        """[Matrix] Testando a ordem TLB - Top Left Bottom"""
        TLB = np.array([
            [[0, 0], [1, 0], [2, 0]],
            [[0, 1], [1, 1], [2, 1]],
            [[0, 2], [1, 2], [2, 2]]
        ])
        self.matrix_order_test("TLB", TLB)

    def test_matrix_order_BRU(self):
        """[Matrix] Testando a ordem BRU - Bottom Right Up"""
        BRU = np.array([
            [[2, 2], [1, 2], [0, 2]],
            [[2, 1], [1, 1], [0, 1]],
            [[2, 0], [1, 0], [0, 0]]
        ])
        self.matrix_order_test("BRU", BRU)

    def test_matrix_order_BLR(self):
        """[Matrix] Testando a ordem BLR - Bottom Left Right"""
        BLR = np.array([
            [[2, 0], [2, 1], [2, 2]],
            [[1, 0], [1, 1], [1, 2]],
            [[0, 0], [0, 1], [0, 2]]
        ])
        self.matrix_order_test("BLR", BLR)

    def test_matrix_order_BRL(self):
        """[Matrix] Testando a ordem BRL - Bottom Right Left"""
        BRL = np.array([
            [[2, 2], [2, 1], [2, 0]],
            [[1, 2], [1, 1], [1, 0]],
            [[0, 2], [0, 1], [0, 0]]
        ])
        self.matrix_order_test("BRL", BRL)

    def test_matrix_manager_create(self):
        """[MATRIX_MANAGER] Criando uma matrix"""
        _oid = ObjectId()
        _id = Manager.create(
            _id=_oid,
            input=self.descritor,
            user=users['dev']
        )
        self.assertEqual(_id, _oid)
        
        descritor = Manager.get_item(
            _id=_oid,
            user=users['dev']
        )
        self.assertEqual(descritor['name'], self.descritor['name'])
        Manager.delete(_id=_oid, user=users['dev'])

    def test_matrix_manager_read(self):
        """[MATRIX_MANAGER] Procurando uma matrix"""
        descritor = Manager.get_item(
            _id=self._id,
            user=users['dev']
        )
        self.assertEqual(descritor['name'], self.descritor['name'])
        self.assertEqual(Blister(descritor).name, Blister(self.descritor).name)

    def test_matrix_manager_update(self):
        """[MATRIX_MANAGER] Atualizando uma matrix"""
        u_id = Manager.update(
            _id=self._id,
            input={'name':'CRUD_MATRIX_TEST'},
            user=users['dev']
        )
        self.assertEqual(u_id, self._id)

        u_descrit = Manager.get_item(
            _id=self._id,
            user=users['dev']
        )
        self.assertEqual(u_descrit['name'], 'CRUD_MATRIX_TEST')
        self.assertNotEqual(Blister(u_descrit).name, Blister(self.descritor).name)

    def test_matrix_manager_delete(self):
        """[MATRIX_MANAGER] Remove uma matrix"""
        Manager.delete(_id=self._id, user=users['dev'])

        with self.assertRaises(KeyError):
            Manager.get_item(_id=self._id, user=users['dev'])