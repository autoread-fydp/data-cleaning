# data-cleaning

The main dataset we'll use to start off with is [The Adventures of Tom Sawyer](https://librivox.org/tom-sawyer-by-mark-twain/) read by [John Greeman](https://librivox.org/reader/107).

Aeneas is the forced alignment software used. Follow setup instructions [here](https://github.com/readbeyond/aeneas/blob/master/wiki/INSTALL.md). Their linux install script was useful for installing some requirements that were not mentioned, so check that out if the pip install fails.

I (Emily) decided to use Aeneas's mplain format for easy word level time detail. See the documentation [here](https://www.readbeyond.it/aeneas/docs/textfile.html#aeneas.textfile.TextFileFormat.MPLAIN).

`to_mplain.py` can be used to convert the [plain text](http://www.gutenberg.org/files/74/74-0.txt) of Tom Sawyer to the proper format. Python's `nltk` library will be required for this to work (for sentence tokenization)

Some notes with the plain text data:
- There's weird areas with double spaces - those were removed manually through search and replace
- some parts in the beginning and end are not included (eg. release date, etc.), those were manually removed
- There's an additional intro section in the reading that I've added below:
  ```
  This is a librivox recording. All librivox recordings are in the public domain. For more information or to volunteer, please visit librivox.org.

  The Adventures of Tom Sawyer, by Mark Twain

  To my wife, this book is affectionately dedicated.
  ```
