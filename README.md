# Datheon Python Programming Internship

This project covers all four internship tasks. Each script runs in a terminal with Python 3.10 or newer and uses only the standard library. Run the commands below from the repository root. On Windows, use `py` in place of `python` if needed.

## Task 1 · Hangman

`python task1/hangman.py`

Guess the word one letter at a time. You can make six incorrect guesses. The display reveals every occurrence of a correct letter and shows a new gallows stage for each mistake. Invalid entries and repeated guesses leave the remaining mistakes unchanged.

## Task 2 · Stock Portfolio Performance Tracker

`python task2/portfolio.py`

Enter a ticker, its buy price in USD, and the number of shares. Press Enter at the ticker prompt to finish. Repeated entries for a ticker combine into one holding with a weighted average buy price. The report shows invested capital, market value, and gain or loss for each holding and the portfolio. Gain or loss percentage is calculated as (market value − invested capital) ÷ invested capital × 100.

The included prices are illustrative. To use a different price snapshot, supply a UTF-8 CSV with `ticker,price_usd` columns:

`python task2/portfolio.py --prices my_prices.csv --output portfolio_summary.csv`

Each successful run writes the latest report to `portfolio_summary.csv` by default. The committed `task2/portfolio_summary.csv` is a generated example based on buying 2 AAPL shares at $150, 1 AAPL share at $180, and 1 MSFT share at $450.

## Task 3 · Automated File Organizer

Preview the files that would move:

`python task3/organizer.py "path/to/folder"`

Apply the changes:

`python task3/organizer.py "path/to/folder" --apply`

Add `--recursive` to organize nested directories, each into its own category folders. The organizer creates Documents, Images, Videos, Archives, and Code folders as needed. It keeps unknown file types in place, skips links and junctions, and adds numeric suffixes to avoid overwriting existing files. Each run logs its actions and prints a summary. Destination or permission errors are reported while processing continues. On POSIX, the destination filesystem must support hard links for moves.

## Task 4 · Rule-Based Support Chatbot

`python task4/chatbot.py`

The bot answers questions about a fictional shop's hours, shipping, returns, backpack, and warranty. Try “When are you open and how long does shipping take?” for a multi-topic response, then “Tell me more” for details about both topics. The bot offers supported topics when it cannot match a question. Type `bye`, `exit`, or `quit` to end the session.
