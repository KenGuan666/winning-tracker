# Technical Design: Winning Tracker

Version: 0.0.0, Nov 21 2021

This project has a database module, a backend API set, and an interface.

## Database

Can use Python3's built-in sqlite3 or JSON dict.

`database/xx_database.py` provides db-related low level functions.

```
db.create_table(name: str, columns: Dict[str, Dict])

db.get_table_schema(name: str)
   # returns Dict[str, Dict[str, str]]

db.get_all_table_names()

db.insert_row(tableName: str, values: Dict[str, Any], _id=None)
   # Returns uuid

db.delete_row(tableName: str, _id: uuid)

db.get_all_rows(tableName: str)

db.get_rows_with_conditions(tableName: str, conditions: List[VisualizeFilters])
   # Acts like db.get_all_rows if conditions=None
```

## Backend API

The Backend provides an interface to the database.

Object Definitions
```
# Defines a Field to a Game
class FieldDefinition:
   fieldName: str
   fieldType: type

# Defines a collection of Fields and their corresponding Values
class Session:
   game: Game
   fieldValues: Dict[str, Any] # fieldName -> value

class Game:
   gameName: str
   fields: List[FieldDefinition] # auto-populate default fields if not provided

class FilterCondition:
   operator: enum[Greater, Less, Equal, Contains]
   operandType: type
   operand: operandType
   negate: bool

# Defines which fields to filter Session results
class VisualizeFilters:
   filters: Dict[str, List[FilterCondition]]
```

Game API
```
func add_game(name str, customFields List[FieldDefinition])
   # Creates a Game object
   # Creates a Table named ${name} with UUID and columns for each default and custom Field
   # Calls db.create_table
   ### TODO: Design an interface to modify the Fields

func get_all_games()
   # Calls db.get_all_table_names
```

Session API
```
func add_session(session Session, _id=None)
   # Creates a row in Table ${gameName}
   # Calls db.insert_row
   # Returns uuid

func get_session_by_id(gameName str, sessionId uuid)
   # Finds session by uuid, or None if not exists

func edit_session(gameName str, sessionId uuid, newSession Session)
   # Modifies the row in Table
   # Calls db.insert_row with previous _id
   # Returns True if successful

func delete_session(gameName str, sessionId uuid)
   # Deletes the row in Table
   # Calls db.delete_row

func get_sessions(gameName str, filters List[VisualizeFilters])
   # Each VisualizeFilters represents an AND
   # Different VisualizeFilters are linked with OR
   # Calls db.get_rows_with_conditions
   # Returns a dict of { uuid: Session }
```

Visualization API
```
### TODO: Design the visualization interface
### How to visualize NET_EARN vs. date?
### Should we provide interface for custom sort function?
### Should we provide interface for other stats?

func visualize_sessions(sessions List[Session])

```


## Interface
First implement a CLI

Once finished, use Python's native GUI as Proof of Concept
