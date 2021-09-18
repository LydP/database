# Database

## Introduction 

This is a simple Python class that creates a DB file from a UTF-16 CSV file for use with my SRS project. The class assumes the
CSV has headers with columns in the order popularity,front,back. (Column header names are not important).

- Popularity: how common the word is (e.g. a word with a popularity of 1 means this is the most common word)
- Front: front of the card
- Back: back of the card

## Database File

The database file is initialized with the following two commands:

```
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
```

```
CREATE TABLE IF NOT EXISTS statistics (
                popularity INTEGER,
                sintvl INTEGER,
                iintvl INTEGER,
                nrev INTEGER DEFAULT 0,
                time TEXT,
                rdr INTEGER,
                vtime INTEGER,
                sess_count INTEGER,
                card_sess_count INTEGER DEFAULT 0,
                riar INTEGER DEFAULT 0);
```

The columns in the statistics table are:

- popularity - cards.popularity; used to identify the card.
- sintvl - scheduled interval: the duration from now to when the card is to be reviewed (in days; 0 if card is to be
  shown again in same session, e.g. when user selects wrong button or card is new and on second viewing)
- iintvl - inter-interval: time from when user last saw the card in seconds; NULL if first time viewing card
- nrev - number of review: the number of times a particular card has been seen as of the current review
- time - date and time of the review
- rdr - 1 (remembered) or 0 (didn't remember)
- vtime - viewing time: the amount of time the user spends looking at the card (in seconds)
- sess_count - the session number at which this review occurred
- card_sess_count - the number of sessions in which a card has appeared, i.e. card_sess_count = 1 means the card has
  appeared in 1 session
- riar - remembered in a row: the number of times in a row the user has remembered a card

The columns in the cards table are: 

- popularity - frequency of occurrence of this word, e.g. 1 means this is the most common word
- front - front of card
- back - back of card
- age - time when the user first saw the card, formatted as MM:dd:yyyy:HH:mm:ss, e.g. 03:01:2021:18:07:13; if NULL, card
  hasn't been seen yet
- csintvl - current scheduled interval; the most recent value of statistics.sintvl-current day; when it reaches 0, card
  is selected for review
- ciintvl - current inter-interval; the most recent value of statistics.iintvl
- cnrev - number of reviews; the most recent value of statistics.nrev
- ctime - data and time of the review; most recent value of statistics.time
- csess_count - session number; most recent value of statistics.sess_count
- cvtime - viewing time; the most recent value of statistics.vtime
- crdr - 1 (remembered) or 0 (didn't remember); the most recent value of statistics.rdr
- ccard_sess_count - the most recent value of statistics.card_sess_count
- criar - remembered in a row; most recent value of statistics.riar
- fin_sess - 0 for when a card's most recent review wasn't completed before user closed program, 1 otherwise
- deck - NULL when fin_sess is 1, 0 or 1 otherwise; shows deck card is in when user closed program

### A Note About Sessions

A session is the reviewing/learning of a deck of cards. ```fin_sess``` and ```deck``` are used in the program to
determine if a user has completed a session when the program is closed. If the user has not completed a session when the
program is closed, that session is resumed when the user reruns the program. Multiple sessions can also occur in a
single run if a new session is scheduled at the same time the user is completing a prior session, such as when rerunning
the program the day after closing it mid-session.

## CSV Formatting

The CSV file must be encoded with UTF-16 and formatted with the columns popularity,front,back (column header names don't matter, as mentioned
before). Separate definitions on the back of the cards must be separated by something other than a comma (e.g.
semicolon). Any desired newlines must be indicated with \n. For example:

|Popularity|Front|Back|
|:--------:|:---:|:---:|
|⋮|⋮|⋮|
|9|仕事|しごと\n\nwork; job|
|⋮|⋮|⋮|
|25|国|くに\n\ncountry|
|⋮|⋮|⋮|

## Creating images
To convert the front text to an image, set ```create_images=True``` in the ```populate_database()``` method. This will
result in the creation of the card_fronts folder in the current working directory and every item in the Front column of
the CSV file will be converted into a JPG image and placed in that folder with the name imageN.jpg, where N is the 
corresponding popularity value minus one. (File names are zero indexed, popularity values are not). If there are 1000
entries in the CSV file, there will be 1000 images.

All images will have the same size, determined by the largest item in the Front column. For example, if your CSV 
consists of the words "back" and "forward", the two images produced will appear as below: 

![Alt text](./examples/image0.jpg?raw=true "Title")  
![Alt text](./examples/image1.jpg?raw=true "Title")
