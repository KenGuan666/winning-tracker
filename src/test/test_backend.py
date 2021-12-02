import unittest
import os

from backend import Backend
from definitions import FieldDefinition, Game, GameName


test_filename = 'test_filename.json'

class BackendTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.backend = Backend()
        cls.backend.db.DEFAULT_DB_FILENAME = test_filename
        cls.backend.db.reset_database()

    @classmethod
    def tearDownClass(cls):
        os.remove(test_filename)


class TestGameAPI(BackendTests):

    def test_add_game(self):
        game = self.backend.add_game(GameName.TEXAS_HOLDEM,[])
        self.assertEqual(game.name, GameName.TEXAS_HOLDEM)

        expectedAllGames = [GameName.TEXAS_HOLDEM]
        self.assertCountEqual(self.backend.db.get_all_table_names(), expectedAllGames)

        expectedGameSchema = [f.as_dict() for f in Game.DefaultFields]
        self.assertCountEqual(
            [f.as_dict() for f in self.backend.db.get_table_schema(GameName.TEXAS_HOLDEM)],
            expectedGameSchema
        )

    def test_get_all_games(self):
        self.backend.add_game(GameName.TEXAS_HOLDEM, [])
        self.backend.add_game(GameName.PLO, [])
        self.backend.add_game(GameName.AOE4, [])

        self.assertCountEqual(
            self.backend.get_all_games(),
            [GameName.TEXAS_HOLDEM, GameName.PLO, GameName.AOE4]
        )
