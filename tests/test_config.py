import os
import unittest
from unittest.mock import patch

import config


class LeituraConfiguracaoTests(unittest.TestCase):
    def test_lista_remove_espacos(self):
        with patch.dict(os.environ, {'TESTE_CODIGOS': '1005, 1923,1056'}):
            self.assertEqual(
                config._ler_lista_codigos('TESTE_CODIGOS', ''),
                ('1005', '1923', '1056'),
            )

    def test_lista_rejeita_codigo_vazio(self):
        with patch.dict(os.environ, {'TESTE_CODIGOS': '1005,,1056'}):
            with self.assertRaises(ValueError):
                config._ler_lista_codigos('TESTE_CODIGOS', '')

    def test_lista_rejeita_duplicidade(self):
        with patch.dict(os.environ, {'TESTE_CODIGOS': '1005,1005'}):
            with self.assertRaises(ValueError):
                config._ler_lista_codigos('TESTE_CODIGOS', '')

    def test_booleanos_validos(self):
        for valor in ('true', '1', 'sim', 'on'):
            with self.subTest(valor=valor):
                with patch.dict(os.environ, {'TESTE_BOOL': valor}):
                    self.assertTrue(config._ler_booleano('TESTE_BOOL', False))

        for valor in ('false', '0', 'nao', 'off'):
            with self.subTest(valor=valor):
                with patch.dict(os.environ, {'TESTE_BOOL': valor}):
                    self.assertFalse(config._ler_booleano('TESTE_BOOL', True))

    def test_booleano_invalido_falha_explicitamente(self):
        with patch.dict(os.environ, {'TESTE_BOOL': 'talvez'}):
            with self.assertRaises(ValueError):
                config._ler_booleano('TESTE_BOOL', False)


if __name__ == '__main__':
    unittest.main()
