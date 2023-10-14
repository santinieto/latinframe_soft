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

if __name__ == '__main__':
    unittest.main()