import sqlite3


conn = sqlite3.connect('finances.db')
db_cursor = conn.cursor()


def main():
    print('What would you like to do?')
    print('1 Add Fund')
    print('2 Update fund shares')
    print('3 Calcuate purches amounts for current allocation model')

    action = input('Selection: ')
    if action == '1':
        ticker = input('Fund ticker to add: ')
        add_fund(ticker)
        update_shares(ticker)

    conn.commit()


def rebalance():
    # current_value_map = {}

    # for ticker in TICKERS:
    #     shares = get_ticker_shares()
    #     current_value = share_amount * current_nav
    pass


def add_fund(ticker):
    db_cursor.execute('INSERT INTO funds (ticker, shares) VALUES (?, 0);', (ticker, ))
    print('Fund with the ticker {} added'.format(ticker))


def update_shares(ticker):
    shares = input('Number of shares for fund {}: '.format(ticker))
    if shares:
        db_cursor.execute('UPDATE funds SET shares=? WHERE ticker=?', (shares, ticker))


if __name__ == '__main__':
    main()
