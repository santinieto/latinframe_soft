import unittest
from src.db import Database

class TestDatabase(unittest.TestCase):

    def test_select_query(self):
        with Database() as db:
            query = 'SELECT VIDEO_ID FROM VIDEO WHERE CHANNEL_ID = ?'
            params = ('UCqNmJfc7RgMU6hTxOOuCYHQ',)
            results = db.select(query, params)
            results = [item[0] for item in results]
            print(results)

    def test_insert_product_record(self):
        with Database() as db:
            db.insert_product_record()

if __name__ == '__main__':
    unittest.main()