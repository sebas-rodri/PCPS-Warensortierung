import sqlite3
import logging


class DatabaseManager:
    """Manages SQLite database operations."""

    def __init__(self, db_name):
        """
        Initializes the DatabaseManager instance with a SQLite database connection.
        @param db_name: The name of the SQLite database file.
        @type db_name: str
        """
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            logging.info(f"Connected to SQLite database '{db_name}'")

            self.createTables()
        except sqlite3.Error as e:
            logging.exception(f"Error connecting to database: {e}")
            self.conn = None
            self.cursor = None

    def createTables(self):
        """
        Creates the following tables:
        packets: packets that are currently in a box, before emptying
        archive: history of all packets being sorted since system setup
        """
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight INTEGER NOT NULL,
                box_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            logging.debug("Table 'packets' created or already exists")

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight INTEGER NOT NULL,
                box_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            logging.debug("Table 'archive' created or already exists")
            self.conn.commit()
        except sqlite3.Error as e:
            logging.exception(f"Error creating tables: {e}")

    def set(self, weight, box_id):
        """
        Inserts data into the 'packets' table and the 'archive' table.
        @param weight: The weight value to insert.
        @type weight: int
        @param box_id: The box ID to associate with the weight.
        @type box_id: int
        """
        if self.cursor:
            try:
                # Insert into packets table
                self.cursor.execute('''
                INSERT INTO packets (weight, box_id) VALUES (?, ?)
                ''', (weight, box_id))
                self.conn.commit()

                # Insert into archive table
                self.cursor.execute('''
                INSERT INTO archive (weight, box_id) VALUES (?, ?)
                ''', (weight, box_id))
                self.conn.commit()

                logging.info(f"Inserted data into 'packets' and 'archive' tables: weight={weight}, box_id={box_id}")
            except sqlite3.Error as e:
                logging.exception(f"Error inserting data: {e}")

    def getById(self, packet_id):
        """
        Fetches one packet by ID.
        @param packet_id: The packet ID to fetch.
        @type packet_id: int
        @return: Row in table 'packets'
        @rtype: int
        """
        if self.cursor:
            try:
                self.cursor.execute('SELECT * FROM packets WHERE id = ?', (packet_id,))
                row = self.cursor.fetchone()
                logging.info(f"Data retrieved from 'packets' table for id={packet_id}: {row}")
                print(row)
                return row
            except sqlite3.Error as e:
                logging.exception(f"Error retrieving data: {e}")

    def getAll(self, table_name):
        """
        Fetches and prints all data from the specified table.
        @param table_name: The name of the table from which to fetch data.
        @type table_name: str
        """
        if self.cursor:
            try:
                self.cursor.execute(f'SELECT * FROM {table_name}')
                rows = self.cursor.fetchall()
                logging.info(f"Data retrieved from '{table_name}' table:")
                for row in rows:
                    print(row)
            except sqlite3.Error as e:
                logging.exception(f"Error retrieving data from '{table_name}': {e}")

    def getPacketsInBox(self, box_id):
        """
        Fetches and prints all packets currently in a specific box.
        @param box_id: The ID of the box.
        @type box_id: int
        """
        if self.cursor:
            try:
                self.cursor.execute('SELECT * FROM packets WHERE box_id = ?', (box_id,))
                rows = self.cursor.fetchall()
                logging.info(f"Packets in box {box_id}:")
                for row in rows:
                    print(row)
            except sqlite3.Error as e:
                logging.exception(f"Error retrieving data: {e}")

    def getPacketsInBoxCount(self, box_id):
        """
        Fetches the count of packets currently in a specific box.
        @param box_id: The ID of the box.
        @type box_id: int
        @return: The count of packets currently in the box.
        @rtype: int
        """
        if self.cursor:
            try:
                self.cursor.execute('SELECT COUNT(*) FROM packets WHERE box_id = ?', (box_id,))
                count = self.cursor.fetchone()[0]
                logging.info(f"Packet count in box {box_id}: {count}")
                return count
            except sqlite3.Error as e:
                logging.exception(f"Error retrieving packet count for box {box_id}: {e}")
                return 0

    def emptyBox(self, box_id):
        """
        Deletes all packets from a specific box in the 'packets' table.
        @param box_id: The ID of the box to empty.
        @type box_id: int
        """
        if self.cursor:
            try:
                self.cursor.execute('DELETE FROM packets WHERE box_id = ?', (box_id,))
                self.conn.commit()
                logging.info(f"Emptied box {box_id} by deleting its packets from 'packets' table")
            except sqlite3.Error as e:
                logging.exception(f"Error emptying box {box_id}: {e}")

    def close(self):
        """
        Closes the database connection.
        """
        if self.conn:
            self.cursor.close()
            self.conn.close()
            logging.info("Connection to SQLite database closed")

    def emptyAndClose(self):
        """
        Empties all boxes and closes the database connection.
        """
        if self.cursor:
            try:
                for box_id in range(1, 3):
                    self.emptyBox(box_id)
                logging.debug("Emptied all boxes and closed the database connection")
            except sqlite3.Error as e:
                logging.exception(f"Error emptying all boxes: {e}")
        self.close()


# for testing purposes
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db_manager = DatabaseManager('raspi-webserver/src/db/database.db')

    # Insert random data
    additional_data = [
        (100, 1),
        (200, 1),
        (510, 2)
    ]
    for data in additional_data:
        db_manager.set(data[0], data[1])

    db_manager.getAll('packets')

    db_manager.getById(1)

    db_manager.getPacketsInBoxCount(1)
    db_manager.getPacketsInBoxCount(2)

    #db_manager.emptyBox(2)

    db_manager.getPacketsInBox(1)
    db_manager.getPacketsInBox(2)

    db_manager.getAll('archive')

    db_manager.close()
