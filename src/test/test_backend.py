import unittest
import os

from backend import Backend
from definitions import FieldDefinition, Game, GameName, Session, DefaultFieldNames


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
        game = self.backend.add_game(GameName.TEXAS_HOLDEM, [])
        self.assertEqual(game.get_name(), GameName.TEXAS_HOLDEM)

        # Check Game and schema in backend.db
        expectedAllGames = [GameName.TEXAS_HOLDEM]
        self.assertCountEqual(self.backend.db.get_all_table_names(), expectedAllGames)

        expectedGameSchema = [f.as_dict() for f in Game.DefaultFields]
        self.assertCountEqual(
            [f.as_dict() for f in self.backend.db.get_table_schema(GameName.TEXAS_HOLDEM)],
            expectedGameSchema
        )

        # backend.add_game fails if Game is already present in db
        self.assertFalse(self.backend.add_game(GameName.TEXAS_HOLDEM, []))

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

    def setUp(self):
        self.backend.db.reset_database()
        self.game = self.backend.add_game(GameName.TEXAS_HOLDEM, [])
        self.uuid1 = self.backend.add_session(Session(self.game, { DefaultFieldNames.NET_EARN: 10 }))
        self.uuid2 = self.backend.add_session(Session(self.game, { DefaultFieldNames.NET_EARN: -10 }))
        self.uuid3 = self.backend.add_session(Session(self.game, { DefaultFieldNames.NET_EARN: 0 }))

    # Test Case: backend.add_session
    def test_add_session(self):

        # Check Session in backend.db
        expectedAllRows = {
            self.uuid1: { DefaultFieldNames.NET_EARN: 10 },
            self.uuid2: { DefaultFieldNames.NET_EARN: -10 },
            self.uuid3: { DefaultFieldNames.NET_EARN: 0 },
        }
        self.assertDictEqual(self.backend.db.get_all_rows(self.game.get_name()), expectedAllRows)

    # Test Case: backend.get_sessions without filter conditions
    # Should return all sessions
    def test_get_sessions_without_filters(self):

        expectedSessions = {
            self.uuid1: Session(self.game, { DefaultFieldNames.NET_EARN: 10 }),
            self.uuid2: Session(self.game, { DefaultFieldNames.NET_EARN: -10 }),
            self.uuid3: Session(self.game, { DefaultFieldNames.NET_EARN: 0 }),
        }
        for _id, actualSession in self.backend.get_sessions(self.game.get_name(), filter=None).items():
            self.assertTrue(actualSession.equals(expectedSessions[_id]))

    # Test Case: backend.get_sessions with filter conditions
    def test_get_sessions_with_filters(self):
        pass

    # Test Case: backend.get_session_by_id
    def test_get_session_by_id(self):

        # Should find existing session by id
        self.assertTrue(self.backend.get_session_by_id(self.game.get_name(), self.uuid1).equals(
            Session(self.game, { DefaultFieldNames.NET_EARN: 10 })
        ))

        # Should return False value if session is not present
        self.assertFalse(self.backend.get_session_by_id(self.game.get_name(), 'bad id'))

    # Test Case: backend.edit_session
    def test_edit_session(self):

        # Should update existing Session with new fieldValues
        self.backend.edit_session(self.game.get_name(), self.uuid1, {
            DefaultFieldNames.LENGTH: 1,
        })
        self.assertTrue(self.backend.get_session_by_id(self.game.get_name(), self.uuid1) \
            .equals(Session(self.game, {
                DefaultFieldNames.NET_EARN: 10,
                DefaultFieldNames.LENGTH: 1,
            })))

        # Should overwrite values in existing Session if new value specified
        self.backend.edit_session(self.game.get_name(), self.uuid2, {
            DefaultFieldNames.NET_EARN: -1,
            DefaultFieldNames.LENGTH: 1,
        })
        self.assertTrue(self.backend.get_session_by_id(self.game.get_name(), self.uuid2) \
            .equals(Session(self.game, {
                DefaultFieldNames.NET_EARN: -1,
                DefaultFieldNames.LENGTH: 1,
            })))

        # Should reject updates that would violate type checks
        self.assertRaises(TypeError, self.backend.edit_session, \
            self.game.get_name(), self.uuid3, {
            DefaultFieldNames.LENGTH: 'text',
        })
        self.assertTrue(self.backend.get_session_by_id(self.game.get_name(), self.uuid3) \
            .equals(Session(self.game, {
                DefaultFieldNames.NET_EARN: 0,
            })))

        # Should reject udpates if session is not present
        self.assertFalse(self.backend.edit_session(self.game.get_name(), 'bad id', {
            DefaultFieldNames.NET_EARN: -1,
        }))

    # Test Case: backend.delete_session
    def test_delete_session(self):

        # Should delete an existing session
        self.assertTrue(self.backend.delete_session(self.game.get_name(), self.uuid1))
        expectedSessions = {
            self.uuid2: Session(self.game, { DefaultFieldNames.NET_EARN: -10 }),
            self.uuid3: Session(self.game, { DefaultFieldNames.NET_EARN: 0 }),
        }
        for _id, actualSession in self.backend.get_sessions(self.game.get_name(), filter=None).items():
            self.assertTrue(actualSession.equals(expectedSessions[_id]))

        # Should return False if session is not present
        self.assertFalse(self.backend.delete_session(self.game.get_name(), 'bad id'))
