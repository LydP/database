"""database.py: create an SRS database file using SQLite from a CSV file. Database can
contain images or text for front of cards."""

import sqlite3
import os
import pathlib
import csv


class DatabaseManager:
    """
    A class for creating and initializing a DB file with values from a CSV file
    """
    def __init__(self, db_name):
        """
        Init DatabaseManager
        :param db_name: full name of the database file you wish to create, e.g. "database.db"
        """
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)

    def create_database(self, create_images=True):
        """
        Create a .db file in cwd. Only creates tables and columns; does not populate the database with data
        :param create_images: true to prepare table for images (blob), false to prepare table for unicode (text)
        :return: None
        """
        path = pathlib.Path(os.getcwd()) / self.db_name
        with self.connection:
            cursor = self.connection.cursor()

            # Recording card data; leading c's mean "current"
            # front - front of card
            # back - back of card
            # age - time when the user first saw the card, formatted as MM:dd:yyyy:HH:mm:ss, e.g. 03:01:2021:18:07:13;
            #   if NULL, card hasn't been seen yet
            # csintvl - current scheduled interval: the most recent value of statistics.sintvl - current day; when it
            #   reaches 0, card is selected for review
            # ciintvl - current inter-interval: the most recent value of statistics.iintvl
            # popularity - frequency of occurrence of this word, e.g. 1 means this is the most common word
            # cnrev - number of reviews: the most recent value of statistics.nrev
            # ctime - data and time of the review; most recent value of statistics.time
            # csess_count - session number; most recent value of statistics.sess_count
            # cvtime - viewing time; the most recent value of statistics.vtime
            # crdr - 1 (remembered) or 0 (didn't remember); the most recent value of statistics.rdr
            # ccard_sess_count - the most recent value of statistics.card_sess_count
            # criar - remembered in a row; most recent value of statistics.riar
            # fin_sess - 0 for when a card's most recent review wasn't completed before user closed program, 1 otherwise
            # deck - NULL when fin_sess is 1, 0 or 1 otherwise; shows deck card is in when user closed program
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cards (
                popularity INTEGER,
                front TEXT,
                back TEXT,
                age TEXT,
                csintvl INTEGER,
                ciintvl INTEGER,
                cnrev INTEGER DEFAULT 0,
                ctime TEXT,
                csess_count INTEGER,
                cvtime INTEGER,
                crdr INTEGER,
                ccard_sess_count INTEGER DEFAULT 0,
                criar INTEGER DEFAULT 0,
                fin_sess INTEGER,
                deck INTEGER);
                """
            )

            # Recording review data for each review
            # iintvl - inter-interval: time from when user last saw the card in seconds; NULL if first time viewing card
            # rdr - 1 (remembered) or 0 (didn't remember)
            # vtime - viewing time: the amount of time the user spends looking at the card (in seconds)
            # sintvl - scheduled interval: the duration from now to when the card is to be reviewed (in days; 0 if card
            #   is to be shown again in same session, e.g. when user selects wrong button or card is new and on second
            #   viewing)
            # time - date and time of the review
            # nrev - number of review: the number of times a particular card has been seen as of the current review
            # popularity - cards.popularity. Used to identify the card.
            # sess_count -  the session number at which this review occurred
            # card_sess_count - the number of sessions in which a card has appeared, i.e. card_sess_count = 1 means the
            #   card has appeared in 1 session
            # riar - remembered in a row: the number of times the user has remembered a card in a row
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS statistics (
                popularity INTEGER,
                sintvl INTEGER,
                iintvl INTEGER,
                nrev INTEGER DEFAULT 0,
                time TEXT,
                rdr INTEGER,
                vtime INTEGER,
                sess_count INTEGER,
                card_sess_count INTEGER DEFAULT 0 ,
                riar INTEGER DEFAULT 0);
                """
            )

        print("'{}' created".format(self.db_name))
        print('Path to DB file: {}'.format(path))

    def populate_database(self, csvfile: str, create_images=True):
        """
        Populates .db file with data from provided CSV file. Used for initializing the empty database created with the
        create_database() method.

        CSV must be formatted with popularity,front,back. Separate definitions on back of cards must be separated by
        something other than a comma (e.g. semicolon). Any desired newlines must be indicated with \n.
        :param csvfile: Path (or just filename if in the cwd) to the CSV file from which to grab database
        information, e.g. 'database.csv'.
        :param create_images: true to convert the front of the card to an image, false to keep it as unicode
        :return: None
        """
        with open(csvfile, 'r', encoding='utf-16') as file:
            csvreader = csv.reader(file)
            next(csvreader)

            with self.connection:
                cursor = self.connection.cursor()

                insert_string = 'INSERT INTO cards (popularity, front, back) VALUES (?, ?, ?)'

                if create_images:
                    self._image_from_text(csvfile)
                    for (i, row) in enumerate(csvreader):
                        path = pathlib.Path('card_fronts') / 'image{}.jpg'.format(i + 1)
                        cursor.execute(insert_string, (int(row[0]), str(path), row[2]))
                else:
                    for row in csvreader:
                        cursor.execute(insert_string, (int(row[0]), row[1], row[2]))

                # SQLite doesn't support \n, so use SQLite char() function to replace newlines
                update_string = 'UPDATE cards SET back = REPLACE(back, "\\n\\n", char(13, 13))'
                cursor.execute(update_string)

        print("'{}' populated".format(self.db_name))

    def _image_from_text(self, csvfile: str, font_size=30, font_file='ARIALUNI.TTF'):
        """
        Creates images with black text and white backgrounds from csvfile. Prints directory where images are created
        :param csvfile: The csvfile from which to read. Must have column headers and be formatted as index,front,back
        :param font_size: Desired font size for the images. Defaults to 30
        :param font_file: Font file to use to determine font in images. Defaults to included ARIALUNI.TTF file
        :return: None
        """
        from PIL import Image, ImageDraw, ImageFont

        font = ImageFont.truetype(font=font_file, size=font_size)

        with open(csvfile, 'r', encoding='utf-16') as file:
            csvreader = csv.reader(file)
            next(csvreader)

            image_width = 100
            image_height = 100

            max_width = 0
            max_height = 0

            # find dimensions of longest and tallest element in font
            # these will be used for image dimensions
            for row in csvreader:
                image = Image.new(mode='RGB', size=(image_width, image_height), color='white')
                im = ImageDraw.Draw(image)
                width, height = im.textsize(row[1], font=font)
                if width > max_width:
                    max_width = width
                if height > max_height:
                    max_height = height

            image_width = max_width
            image_height = max_height

        with open(csvfile, 'r', encoding='utf-16') as file:
            csvreader = csv.reader(file)
            next(csvreader)

            try:
                os.mkdir('card_fronts')
            except FileExistsError:
                print('card_fronts already exists in current working directory')

            # create the images
            for (i, row) in enumerate(csvreader):
                image = Image.new(mode='RGB', size=(image_width, image_height), color='white')
                im = ImageDraw.Draw(image)
                width, height = im.textsize(row[1], font=font)
                # center text in image
                x = (image_width - width) / 2
                y = (image_height - height) / 2
                im.text((x, y), row[1], fill=(0, 0, 0), font=font)
                try:
                    image.save(r'card_fronts\image{}.jpg'.format(i))
                except FileNotFoundError:
                    print("card_fronts directory doesn't exist.")
                    exit()

        print('Images are here: {}'.format(pathlib.Path(os.getcwd()) / 'card_fronts'))
