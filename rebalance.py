import sqlite3

import yahoofinancials
import prettytable


conn = sqlite3.connect('finances.db')
db_cursor = conn.cursor()


def main():
    action = None
    while action != 6:
        action = options()

        if action == 1:
            ticker = get_ticker()
            add_fund(ticker)
            update_shares(ticker)
            set_target_allocation(ticker)
        if action == 2:
            ticker = get_ticker()
            update_shares(ticker)
        if action == 3:
            ticker = get_ticker()
            set_target_allocation(ticker)
        if action == 4:
            rebalance()
        if action == 5:
            show_allocation()

        conn.commit()


def rebalance():
    contribution_amount = input('How much are you contributing? ')

    funds = db_cursor.execute('SELECT ticker, shares, target_allocation FROM funds').fetchall()

    tickers = [fund[0] for fund in funds]

    fin = yahoofinancials.YahooFinancials(tickers)
    current_price_map = fin.get_current_price()
    current_price_map['CASHX'] = 1

    fund_dict = {}
    protfolio_value = 0.0

    for fund in funds:
        fund_dict[fund[0]] = {
            'shares': fund[1],
            'current_price': current_price_map[fund[0]],
            'current_value': fund[1] * current_price_map[fund[0]],
            'target_allocation': fund[2]
        }

        protfolio_value += fund_dict[fund[0]]['current_value']

    table = prettytable.PrettyTable()
    table.field_names = ['TICKER', 'SHARES', 'CURRENT_ALLOCATION', 'TARGET_ALLOCATION', 'BUY_AMOUNT']

    for ticker, fund_data in fund_dict.items():
        target_value = (protfolio_value + float(contribution_amount)) * (fund_data['target_allocation'] / 100)
        buy_amount = round(target_value - fund_data['current_value'], 2)

        current_allocation = round((fund_data['current_value'] / protfolio_value) * 100, 2)

        table.add_row([ticker, fund_data['shares'], current_allocation, fund_data['target_allocation'], buy_amount])

    print(table)
    print('\n')


def get_ticker():
    return input('Fund ticker: ')


def add_fund(ticker):
    db_cursor.execute('INSERT INTO funds (ticker, shares) VALUES (?, 0);', (ticker, ))
    print('Fund with the ticker {} added'.format(ticker))


def update_shares(ticker):
    shares = input('Number of shares for fund {}: '.format(ticker))
    if shares:
        db_cursor.execute('UPDATE funds SET shares=? WHERE ticker=?', (shares, ticker))


def set_target_allocation(ticker):
    target_allocation = input('Desired allocation of fund {}: '.format(ticker))
    if target_allocation:
        db_cursor.execute('UPDATE funds SET target_allocation=? WHERE ticker=?', (float(target_allocation), ticker))


def show_allocation():
    funds = db_cursor.execute('SELECT ticker, shares, target_allocation FROM funds').fetchall()

    tickers = [fund[0] for fund in funds]

    fin = yahoofinancials.YahooFinancials(tickers)
    current_price_map = fin.get_current_price()
    current_price_map['CASHX'] = 1

    fund_dict = {}
    protfolio_value = 0.0
    for fund in funds:
        fund_dict[fund[0]] = {
            'shares': fund[1],
            'current_price': current_price_map[fund[0]],
            'current_value': fund[1] * current_price_map[fund[0]]
        }

        protfolio_value += fund_dict[fund[0]]['current_value']

    table = prettytable.PrettyTable()
    table.field_names = ['TICKER', 'SHARES', 'CURRENT_ALLOCATION', 'TARGET_ALLOCATION']
    for fund in funds:
        ticker = fund[0]
        shares = fund[1]

        current_allocation = round((fund_dict[ticker]['current_value'] / protfolio_value) * 100, 2)
        table.add_row([ticker, shares, current_allocation, fund[2]])

    print(table)
    print('\n')


def options():
    valid_options = list(range(1, 7))

    def print_options():
        print('What would you like to do?')
        print('1 Add Fund')
        print('2 Update fund shares')
        print('3 Set target allocation for fund')
        print('4 Calcuate purches amounts for current allocation model')
        print('5 Show current funds')
        print('6 Exit\n')

    no_selection = True
    while no_selection:
        print_options()
        action = input('Selection: ')
        print('\n')

        try:
            action = int(action)
        except ValueError:
            print('Please enter a number for the corresponding action!\n')
            continue

        if action in valid_options:
            return action
        else:
            print('Please enter a number for the corresponding action!\n')

    return action


if __name__ == '__main__':
    main()
