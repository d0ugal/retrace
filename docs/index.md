# Retrace

Dealing with some unstable code? Be it a bad connection or system that often
fall over retrace is here to help. Simple, easy and configurable method
retrying with a nice clean API.

Don't manually fudge around with exception retrying again!

## Installation

### Install from pip

Installation from pip is simple, just use

    pip install retrace

### Vendoring

If you don't want to add a new dependency for such a small tool, you are in
luck! Retrace is designed to be easily vendor-able! Simply head to the
[GitHub repo](https://github.com/d0ugal/retrace), grab the `retrace.py` file
and include it in your project tree. Then, for example, say you add it under
`myproject.utils.retrace` then you just need to use that import path in the
examples below.


## Usage Examples

### Retrying, on all exceptions


If you want to retry a function call on any exception you can use the decorator
with no arguments.


```python
import retrace

@retrace.retry
def unstable():
    # ...
```

!!! note

    By default this will catch all subclasses of Exception, meaning it wont
    catch a anything that subclasses BaseException directly like
    KeyboardInterupt. **By default, it will retry 5 times.**


### Retrying specific exceptions only

```python
import retrace

@retrace.retry(on_exeption=IOError)
def unstable():
    # ...
```


### Delaying between retries

If you want to delay between retries you can pass in an int or interval object.
Interval objects are given information and then return the sleep in seconds. If
an int is passed that will be used instead.

```
import retrace

@retrace.retry(interval=5)
def unstable():
    # ...
```


### Limit the number of attempts

```
import retrace

@retrace.retry(limit=5)
def unstable():
    # ...
```


## Custom Retry Handling

Customising the behaviour is a breeze, if you have some specific logic you
want to implement.

For example, here is a exponential backoff. It will increase the delay between
each attempt. To do this, a method needs to be passed that accepts one
argument. The argument is the the current attempt integer.

```
import time
import retrace

def exponential_backoff(attempt_number):
    time.sleep(attempt_number * 2)

@retrace.retry(sleep=exponential_backoff)
def unstable():
    # ...
```

Similarly, the same behaviour can be used to control the retrying behaviour.
In this artificial example, the retry limit is 10 in the afternoon, but only 5
in them orning.

```
import datetime
import retrace

def try_more_in_the_afternoon(attempt_number):

    now = datetime.datetime.now()
    if now.hour < 12 and attempt_number > 5:
        raise retrace.LimitException()
    elif attempt_number > 10:
        raise retrace.LimitException()

@retrace.retry(limit=try_more_in_the_afternoon)
def unstable():
    # ...
```
