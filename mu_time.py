import time

month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# Daylight Savings Time is calculated by finding the last Sunday of a month in spring and the last Sunday of a month in fall. The exact months vary between countries.
# Set the summertime month by assigning a new integer value to summertime_month
summertime_month = 3
# Set the wintertime month by assigning a new integer value to wintertime_month
wintertime_month = 10
# Set the timezone offset by assigning a new integer valut to timezone_offset
timezone_offset = 1

def find_weekday(year: int, month: int, day: int):
    # Convert month and year to Zeller's numbering system
    if month < 3:
        month += 12
        year -= 1
    k = year % 100
    j = year // 100

    # Calculate weekday using Zeller's Congruence Algorithm
    #   h = (q + ((13 * (m + 1)) // 5 + K + (K // 4) + (J // 4) - 2 * J)) % 7
    # where:
    #   h = day of week as integer (0 = Saturday, 6 = Friday)
    #   q = day of the month
    #   m = month as integer (3 = March, 4 = April, 5 = May [...] 14 = February) **
    #   K = year of the century (year % 100)
    #   J = 0-indexed century (year // 100)
    h = (day + ((13 * (month + 1)) // 5) + k  + (k // 4) + (j // 4) - 2 * j) % 7

    # Convert back so that 0 = Monday, 6 = Sunday
    return (h + 5) % 7


def is_leapyear(year: int):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def last_sunday(year: int, month: int):

    if is_leapyear(year):
        month_lengths[1] = 29

    month_idx = month - 1
    last_days = []
    for i in range(month_lengths[month_idx] - 6, month_lengths[month_idx] + 1):
        last_days.append(i)

    for day in last_days:
        if find_weekday(year, month, day) == 6:
            return day

def find_yearday(year: int, month: int, day: int):

    if is_leapyear(year):
        month_lengths[1] = 29

    return sum(month_lengths[:month - 1]) + day


def is_summertime():
    year = time.localtime().tm_year
    yearday = time.localtime().tm_yday
    summertime_start = find_yearday(year, summertime_month, last_sunday(year, summertime_month))
    winter_time_start = find_yearday(year, wintertime_month, last_sunday(year, wintertime_month))
    return summertime_start <= yearday and yearday < winter_time_start


def now():
    hour = time.localtime().tm_hour
    minute = time.localtime().tm_min
    hour += timezone_offset
    if is_summertime():
        hour += 1

    shr = f'{hour}'
    smin = f'{minute}'
    if hour >= 24:
        hour = hour % 24
    elif hour < 10:
        shr = '0' + shr    
    if minute < 10:
        smin = '0' + smin
    
    return f'{shr}:{smin}'
