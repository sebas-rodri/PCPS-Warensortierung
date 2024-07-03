import sqlite3
import logging

class DatabaseManager:
    """Manages SQLite database operations."""

    def __init__(self, db_name):
        """
        Initializes the DatabaseManager instance with a SQLite database connection.

        Args:
            db_name (str): The name of the SQLite database file.
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
        Creates tables.
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

        Args:
            weight (int): The weight value to insert.
            box_id (int): The box ID to associate with the weight.
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
        Fetches one packet by id.

        Args:
            packet_id (int): The ID of the packet to fetch.
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

        Args:
            table_name (str): The name of the table from which to fetch data.
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

        Args:
            box_id (int): The ID of the box.
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

        Args:
            box_id (int): The ID of the box.
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

        Args:
            box_id (int): The ID of the box to empty.
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
                for box_id in range(1,3):
                    self.emptyBox(box_id)              
                logging.debug("Emptied all boxes and closed the database connection")
            except sqlite3.Error as e:
                logging.exception(f"Error emptying all boxes: {e}")
        self.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db_manager = DatabaseManager('raspi-frontend/src/db/database.db')

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
