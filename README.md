# retrace - configurable retrying of functions

Retrace allows you to wrap functions with decorators and handle how they are
retried on exceptions.


## Retrying, on all exceptions

```python
import retrace

@retrace.retry
def unstable():
    # ...
```


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
