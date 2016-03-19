from __future__ import print_function

import logging
import sys
import time

import retrace

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


count = [0, 0]


def limit(attempt_number):
    print("Current attempt: {}".format(attempt_number))
    print("Limiter, I will stop this if we go over 5 attempts.")
    if attempt_number > 5:
        raise retrace.LimitReached()


def interval(attempt_number):
    print("Adding a delay between attempts, increasing by one second.")
    time.sleep(attempt_number * 0.1)


@retrace.retry(limit=limit, interval=interval)
def unstable(pass_at):

    count[0] += 1

    if count[0] < pass_at:
        print("FAILING")
        time.sleep(1)
        raise Exception("FAIL")

    return "PASSING"


print("Calling unstable. Example 1")
print(unstable(5))

count[0] = 0

print("\n\n\n")
print("Calling unstable. Example 2")

try:
    print(unstable(10))
except retrace.LimitReached:
    print("Limit reached.\n\n")


def validator(result):
    return result == 3


@retrace.retry(validator=validator)
def wrong():
    count[1] += 1
    return count[1]

print(wrong())
