import os, sys
import shutil
brief="output field types"

def execute(argv, argv0, engine):
    print("""
    table.big_increments('id')              Incrementing ID using a “big integer” equivalent
    table.big_integer('votes')              BIGINT equivalent to the table
    table.binary('data')                    BLOB equivalent to the table
    table.boolean('confirmed')              BOOLEAN equivalent to the table
    table.char('name', 4)                   CHAR equivalent with a length
    table.date('created_on')                DATE equivalent to the table
    table.datetime('created_at')            DATETIME equivalent to the table
    table.decimal('amount', 5, 2)           DECIMAL equivalent to the table with a precision and scale
    table.double('column', 15, 8)           DOUBLE equivalent to the table with precision, 15 digits in total and 8 after the decimal point
    table.enum('choices', ['foo', 'bar'])   ENUM equivalent to the table
    table.float('amount')                   FLOAT equivalent to the table
    table.increments('id')                  Incrementing ID to the table (primary key)
    table.integer('votes')                  INTEGER equivalent to the table
    table.json('options')                   JSON equivalent to the table
    table.long_text('description')          LONGTEXT equivalent to the table
    table.medium_integer('votes')           MEDIUMINT equivalent to the table
    table.medium_text('description')        MEDIUMTEXT equivalent to the table
    table.morphs('taggable')                Adds INTEGER taggable_id and STRING taggable_type
    table.nullable_timestamps()             Same as timestamps(), except allows NULLs
    table.small_integer('votes')            SMALLINT equivalent to the table
    table.soft_deletes()                    Adds deleted_at column for soft deletes
    table.string('email')                   VARCHAR equivalent column
    table.string('votes', 100)              VARCHAR equivalent with a length
    table.text('description')               TEXT equivalent to the table
    table.time('sunrise')                   TIME equivalent to the table
    table.timestamp('added_at')             TIMESTAMP equivalent to the table
    table.timestamps()                      Adds created_at and updated_at columns
    .nullable()                             Designate that the column allows NULL values
    .default(value)                         Declare a default value for a column
    .unsigned()                             Set INTEGER to UNSIGNED
    """)
