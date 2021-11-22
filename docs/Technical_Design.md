# Technical Design: Winning Tracker

Version: 0.0.0, Nov 21 2021

This project has a database module, a backend API set, and an interface.

## Database

Can use Python3's built-in sqlite3 or JSON dict.

`database/xx_database.py` provides db-related low level functions.

```
db.create_table(name str, columns List[str])

db.get_all_table_names()

db.insert_row(tableName str, values Dict[str] fieldType)
   # Returns uuid

db.delete_row(tableName str, id uuid)

db.get_rows_with_conditions(tableName str, conditions List[VisualizeFilters])
```

## Backend API

The Backend provides an interface to the database.

Object Definitions
```
# Defines a Field to a Game
class FieldDefinition:
   fieldName str
   fieldType type

# Defines a collection of Fields and their corresponding Values
class FieldValueCollection:
   values Dict[fieldName str] fieldType

class Game:
   gameName str
   fields List[FieldDefinition]

class Session:
   id uuid
   game Game
   fieldValues FieldValueCollection

class FilterCondition:
   operator enum[Greater, Less, Equal, Contains]
   operandType type
   operand operandType
   negate bool

# Defines which fields to filter Session results
class VisualizeFilters
   filters Dict[fieldName str] List[FilterCondition]
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
func add_session(gameName str, fieldValues FieldValueCollection)
   # Creates Session object
   # Creates a row in Table ${gameName}
   # Calls db.insert_row

func edit_session(gameName str, sessionId uuid, newFieldValues FieldValueCollection)
   # Modifies the row in Table
   # Returns new Session object
   # Calls db.delete_row & db.insert_row

func delete_session(gameName str, sessionId uuid)
   # Deletes the row in Table
   # Calls db.delete_row

func get_sessions(gameName str)
   # Calls db.get_rows_with_conditions
   ### TODO: Support Pagination
```

Visualization API
```
func get_sessions(gameName str, filters List[VisualizeFilters])
   # Each VisualizeFilters represents an AND
   # Different VisualizeFilters are linked with OR
   # Calls db.get_rows_with_conditions

### TODO: Design the summary stats visualization
```


## Interface
First implement a CLI

Once finished, use Python's native GUI as Proof of Concept
