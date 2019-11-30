import csv
import os

import yahoofinancials
import prettytable

import database as db
import models.allocation


def main():
    action = None
    while action != 4:
        action = options()

        if action == 1:
            show_allocation()
        elif action == 2:
            rebalance()
        elif action == 3:
            sheet = get_csv()
            import_assets(sheet)


def rebalance():
    contribution_amount = input('How much are you contributing? ')

    allocations = db.session.query(models.allocation.Allocation).all()
    assets = []
    for alloc in allocations:
        for asset in alloc.assets:
            assets.append(asset)

    fin = yahoofinancials.YahooFinancials([asset.id for asset in assets])
    current_price_map = fin.get_current_price()
    current_price_map['SPAXX**'] = 1

    asset_map = {}
    protfolio_value = 0.0

    for asset in assets:
        asset_map[asset.id] = {
            'shares': asset.shares,
            'current_price': current_price_map[asset.id],
            'current_value': asset.shares * current_price_map[asset.id],
            'target_allocation': 0
        }

        protfolio_value += asset_map[asset.id]['current_value']

    table = prettytable.PrettyTable()
    table.field_names = ['TICKER', 'BUY AMOUNT', 'CURRENT_ALLOCATION', 'TARGET_ALLOCATION']
    rows = []
    for alloc in allocations:
        target_value = (protfolio_value + float(contribution_amount)) * (alloc.target / 100)

        active_asset = None
        current_value = 0.0
        for asset in alloc.assets:
            current_value += asset_map[asset.id]['current_value']
            if asset.is_active:
                active_asset = asset

        current_allocation = round((current_value / protfolio_value) * 100, 2)
        buy_amount = round(target_value - current_value, 2)

        rows.append([active_asset.id, buy_amount, current_allocation, alloc.target])

    rows.sort(key=lambda x: x[0])
    for row in rows:
        table.add_row(row)

    print(table)
    print('\n')


def add_or_update_asset(ticker, shares, name):
    asset = db.session.query(models.allocation.Asset).get(ticker)

    if asset:
        if shares and asset.shares != shares:
            asset.shares = shares
        if name and asset.name != name:
            asset.name = name
        print(f'Fund {ticker} was updated')
    else:
        asset = models.allocation.Asset(id=ticker, shares=shares, name=name)
        db.session.add(asset)
        print(f'Fund with the ticker {ticker} added')

    db.session.flush()

    set_allocation(asset)

    trues = ['y', 'Y', 'yes', 'Yes', 'YES']
    _input = input('Is this an actively purchased asset y/n: ')
    asset.is_active = _input in trues

    db.session.flush()


def set_allocation(asset):
    current_allocations = db.session.query(models.allocation.Allocation). \
        order_by(models.allocation.Allocation.name).all()

    if not asset.allocation:
        table = prettytable.PrettyTable()
        table.field_names = ['ID', 'NAME', 'TARGET_ALLOCATION']

        for alloc in current_allocations:
            table.add_row([alloc.id, alloc.name, alloc.target])

        print(f'No current allocation for {asset.id} {asset.name}\n\n\n')
        print('Current available allocation groups')
        print(table)
        print('\n')

        _input = input('Enter ID of alloaction group to add current asset to or desired Name,target for new.\n')

        try:
            allocation_id = int(_input)
        except ValueError:
            name, target = _input.split(',')

            allocation_obj = models.allocation.Allocation(name=name, target=target)
            db.session.add(allocation_obj)
            db.session.flush()
            allocation_id = allocation_obj.id

        allocation_relationship = models.allocation.AssetAllocationRelationship(
            asset_id=asset.id, allocation_id=allocation_id)

        db.session.add(allocation_relationship)
        db.session.flush()
    else:
        print(f'Current target allocation group {asset.allocation.name} with target {asset.allocation.target}')

    db.session.commit()


def import_assets(sheet):
    column_map = {}
    with open(sheet, newline='') as csv_file:
        reader = csv.reader(csv_file)
        column_names = next(reader)

        for idx, name in enumerate(column_names):
            if name == 'Symbol':
                column_map['ticker'] = idx
            elif name == 'Description':
                column_map['name'] = idx
            elif name == 'Quantity':
                column_map['shares'] = idx
        for asset in reader:
            if column_map['ticker'] >= len(asset):
                break

            add_or_update_asset(asset[column_map['ticker']], asset[column_map['shares']], asset[column_map['name']])


def get_csv():
    path = './upload'
    file_name = os.listdir('./upload')[0]

    return path + '/' + file_name


def show_allocation():
    # TODO replace with orm
    # funds = db_cursor.execute('SELECT ticker, shares, target_allocation FROM funds').fetchall()

    funds = db.session.query(models.allocation.Asset).all()
    tickers = [fund.id for fund in funds]

    fin = yahoofinancials.YahooFinancials(tickers)
    current_price_map = fin.get_current_price()
    current_price_map['SPAXX**'] = 1

    fund_dict = {}
    protfolio_value = 0.0
    for fund in funds:
        fund_dict[fund.id] = {
            'shares': fund.shares,
            'current_price': current_price_map[fund.id],
            'current_value': fund.shares * current_price_map[fund.id]
        }

        protfolio_value += fund_dict[fund.id]['current_value']

    allocations = db.session.query(models.allocation.Allocation).all()

    table = prettytable.PrettyTable()
    table.field_names = ['NAME', 'CURRENT_ALLOCATION', 'TARGET_ALLOCATION', 'ACTIVE FUND']
    for alloc in allocations:
        current_allocation = 0.0
        active_asset = None
        for asset in alloc.assets:
            current_allocation += round((fund_dict[asset.id]['current_value'] / protfolio_value) * 100, 2)
            if asset.is_active:
                active_asset = asset

        table.add_row([alloc.name, current_allocation, alloc.target, active_asset.name])

    print(table)
    print('\n')


def options():
    valid_options = list(range(1, 5))

    def print_options():
        print('What would you like to do?')
        print('1 Show current funds')
        print('2 Calcuate purches amounts for current allocation model')
        print('3 Upload')
        print('4 Exit\n')

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
