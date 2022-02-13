import datetime

def get_time_info(today_date):
    #today_date = datetime.datetime.today()
    first_day_of_week = today_date - datetime.timedelta(days=today_date.weekday())
    last_day_of_week = today_date - datetime.timedelta(days=today_date.weekday()) + datetime.timedelta(days=6)
    first_day_of_month = today_date.replace(day=1)
    last_day_of_month = first_day_of_month.replace(day=28) + datetime.timedelta(days=4)  - datetime.timedelta(days=first_day_of_month.day)
    first_day_of_year = today_date.replace(month=1, day=1)
    last_day_of_year = today_date.replace(month=12, day=31)

    # first_day_of_week = datetime.datetime.combine(first_day_of_week, datetime.datetime.min.time())
    # last_day_of_week = datetime.datetime.combine(last_day_of_week, datetime.datetime.min.time())
    # first_day_of_month = datetime.datetime.combine(first_day_of_month, datetime.datetime.min.time())
    # last_day_of_month = datetime.datetime.combine(last_day_of_month, datetime.datetime.min.time())
    # first_day_of_year = datetime.datetime.combine(first_day_of_year, datetime.datetime.min.time())
    # last_day_of_year = datetime.datetime.combine(last_day_of_year, datetime.datetime.min.time())

    d = {}
    d['current_timestamp'] = today_date.timestamp()
    d['first_day_of_week'] = datetime.datetime.combine(first_day_of_week, datetime.datetime.min.time()).timestamp()
    d['last_day_of_week'] = datetime.datetime.combine(last_day_of_week, datetime.datetime.min.time()).timestamp()
    d['first_day_of_month'] = datetime.datetime.combine(first_day_of_month, datetime.datetime.min.time()).timestamp()
    d['last_day_of_month'] = datetime.datetime.combine(last_day_of_month, datetime.datetime.min.time()).timestamp()
    d['first_day_of_year'] = datetime.datetime.combine(first_day_of_year, datetime.datetime.min.time()).timestamp()
    d['last_day_of_year'] = datetime.datetime.combine(last_day_of_year, datetime.datetime.min.time()).timestamp()

    return(d) 


def main():
    d = get_time_info(datetime.datetime.today())

    #print(d)

    current_date = datetime.datetime.fromtimestamp(d['current_timestamp'])
    first_day_of_week = datetime.datetime.fromtimestamp(d['first_day_of_week'])
    last_day_of_week = datetime.datetime.fromtimestamp(d['last_day_of_week'])
    first_day_of_month = datetime.datetime.fromtimestamp(d['first_day_of_month'])
    last_day_of_month = datetime.datetime.fromtimestamp(d['last_day_of_month'])
    first_day_of_year = datetime.datetime.fromtimestamp(d['first_day_of_year'])
    last_day_of_year = datetime.datetime.fromtimestamp(d['last_day_of_year'])

    print(f'The current epoch is: {current_date.timestamp()}')
    print(f'The current timestamp is: {current_date}')
    print(f'The current date is: {current_date.date()}') # needs an integer
    print(f'The first day of the week is: {first_day_of_week.date()}')
    print(f'The last day of the week is: {last_day_of_week.date()}')
    print(f'The first day of the month is: {first_day_of_month.date()}')
    print(f'The last day of the month is: {last_day_of_month.date()}')
    print(f'The first day of the year is: {first_day_of_year.date()}')
    print(f'The last day of the year is: {last_day_of_year.date()}')

if __name__ == '__main__':
    main()