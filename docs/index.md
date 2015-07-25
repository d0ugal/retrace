# Retrace Usage


## Retrying, on all exceptions


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


## Retrying specific exceptions only

```python
import retrace

@retrace.retry(on_exeption=IOError)
def unstable():
    # ...
```


## Delaying between retries

If you want to delay between retries you can pass in an int or interval object.
Interval objects are given information and then return the sleep in seconds. If
an int is passed that will be used instead.

```
from retrace import intervals
import retrace

@retrace.retry(interval=5)
def unstable():
    # ...


@retrace.retry(interval=intervals.sleep(5))
def unstable():
    # ...
```


## Limit the number of attempts

```
from retrace import limits
import retrace

@retrace.retry(limit=5)
def unstable():
    # ...

@retrace.retry(limit=limits.count(5))
def unstable():
    # ...
```
