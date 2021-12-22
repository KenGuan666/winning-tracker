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

    # Test Case: backend.add_game
    def test_add_game(self):

        # backend.add_game
        game = self.backend.add_game(GameName.TEXAS_HOLDEM,[])
        self.assertEqual(game.name, GameName.TEXAS_HOLDEM)

        # Check Game and schema in backend.db
        expectedAllGames = [GameName.TEXAS_HOLDEM]
        self.assertCountEqual(self.backend.db.get_all_table_names(), expectedAllGames)

        expectedGameSchema = [f.as_dict() for f in Game.DefaultFields]
        self.assertCountEqual(
            [f.as_dict() for f in self.backend.db.get_table_schema(GameName.TEXAS_HOLDEM)],
            expectedGameSchema
        )

    # Test Case: backend.get_all_games
    def test_get_all_games(self):

        # Set up state with db.add_game
        self.backend.add_game(GameName.TEXAS_HOLDEM, [])
        self.backend.add_game(GameName.PLO, [])
        self.backend.add_game(GameName.AOE4, [])

        # Check backend.get_all_games against expected state
        self.assertCountEqual(
            self.backend.get_all_games(),
            [GameName.TEXAS_HOLDEM, GameName.PLO, GameName.AOE4]
        )


class TestSessionAPI(BackendTests):

    # Test Case: backend.add_session
    def test_add_session(self):
        pass

    # Test Case: backend.edit_session
    def test_edit_session(self):
        pass

    # Test Case: backend.delete_session
    def test_delete_session(self):
        pass

    # Test Case: backend.get_sessions
    def test_get_sessions(self):
        pass
