# Usage Examples

This page provides examples of how to use py-cashier in various scenarios.

## Basic Usage

### Caching a Synchronous Function

```python
from py_cashier import cache

@cache()
def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# First call computes the value
result1 = fibonacci(10)  # Performs many recursive calculations
print(result1)  # Output: 55

# Second call uses cached result
result2 = fibonacci(10)  # Instant result from cache
print(result2)  # Output: 55
```

### Caching an Asynchronous Function

```python
import asyncio
from py_cashier import cache

@cache()
async def fetch_data(user_id: int) -> dict:
    """Simulate fetching user data from a database."""
    print(f"Fetching data for user {user_id}...")
    # Simulate network delay
    await asyncio.sleep(1)
    return {"id": user_id, "name": f"User {user_id}"}

async def main():
    # First call performs the fetch
    user = await fetch_data(123)
    print(user)  # Output: {'id': 123, 'name': 'User 123'}

    # Second call uses cached result (no delay)
    user_again = await fetch_data(123)
    print(user_again)  # Output: {'id': 123, 'name': 'User 123'}

asyncio.run(main())
```

## Advanced Usage

### Custom TTL (Time-To-Live)

```python
from datetime import timedelta
from py_cashier import cache
from py_cashier._storages import TTLMapStorage
import time

@cache(storage=lambda: TTLMapStorage(ttl=timedelta(seconds=5)))
def get_timestamp() -> float:
    """Return the current timestamp."""
    return time.time()

# First call
ts1 = get_timestamp()
print(f"Timestamp 1: {ts1}")

# Second call (within TTL) - returns cached value
ts2 = get_timestamp()
print(f"Timestamp 2: {ts2}")
print(f"Same timestamp: {ts1 == ts2}")  # Output: True

# Wait for TTL to expire
time.sleep(6)

# Third call (after TTL expired) - returns new value
ts3 = get_timestamp()
print(f"Timestamp 3: {ts3}")
print(f"Different timestamp: {ts1 != ts3}")  # Output: True
```

### Custom Cache Size

```python
from py_cashier import cache
from py_cashier._storages import TTLMapStorage

@cache(storage=lambda: TTLMapStorage(max_size=2))  # Only store the 2 most recently used results
def process_data(data_id: int) -> str:
    print(f"Processing data {data_id}...")
    return f"Processed {data_id}"

# Fill the cache
process_data(1)  # Output: Processing data 1...
process_data(2)  # Output: Processing data 2...

# Both results are cached
process_data(1)  # No output (cached)
process_data(2)  # No output (cached)

# Add a third item, which will evict the least recently used item (1)
process_data(3)  # Output: Processing data 3...

# Item 1 is no longer in cache
process_data(1)  # Output: Processing data 1... (recalculated)
# Item 2 is still in cache
process_data(2)  # No output (cached)
```

### Custom Key Builders

```python
from py_cashier import cache, DefaultKeyBuilder

# Only consider the first argument for caching
key_builder = DefaultKeyBuilder(
    func=lambda x, *args, **kwargs: x,
    prefix="first_arg_only"
)

@cache(key_builder=key_builder)
def add_numbers(a: int, b: int) -> int:
    print(f"Adding {a} + {b}")
    return a + b

# First call
result1 = add_numbers(5, 10)  # Output: Adding 5 + 10
print(result1)  # Output: 15

# Second call with same first argument but different second argument
# Uses cached result because our key builder only considers the first argument
result2 = add_numbers(5, 20)  # No output (cached)
print(result2)  # Output: 15 (not 25!)

# Call with different first argument
result3 = add_numbers(7, 10)  # Output: Adding 7 + 10
print(result3)  # Output: 17
```

### Different Serializers

```python
from py_cashier import cache, DefaultKeyBuilder, Md5Serializer

# Use MD5 serializer for consistent hashing across processes
key_builder = DefaultKeyBuilder(
    func=lambda x, y: x + y,
    key_serializer=Md5Serializer
)


@cache(key_builder=key_builder)
def compute_value(x: int, y: int) -> int:
    print(f"Computing {x} * {y}")
    return x * y


# First call
result = compute_value(5, 10)  # Output: Computing 5 * 10
print(result)  # Output: 50

# Second call uses cached result
result_again = compute_value(5, 10)  # No output (cached)
print(result_again)  # Output: 50
```

## Practical Examples

### Caching Database Queries

```python
from py_cashier import cache
from py_cashier._storages import TTLMapStorage
from datetime import timedelta
import sqlite3

# Create a connection to a database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create a table and insert some data
cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)')
cursor.execute('INSERT INTO users VALUES (1, "Alice")')
cursor.execute('INSERT INTO users VALUES (2, "Bob")')
conn.commit()

@cache(storage=lambda: TTLMapStorage(ttl=timedelta(minutes=5)))
def get_user(user_id: int) -> dict:
    """Get a user from the database by ID."""
    print(f"Fetching user {user_id} from database...")
    cursor.execute('SELECT id, name FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    if row:
        return {"id": row[0], "name": row[1]}
    return None

# First query hits the database
user1 = get_user(1)  # Output: Fetching user 1 from database...
print(user1)  # Output: {'id': 1, 'name': 'Alice'}

# Second query uses cache
user1_again = get_user(1)  # No output (cached)
print(user1_again)  # Output: {'id': 1, 'name': 'Alice'}

# Different user ID hits the database again
user2 = get_user(2)  # Output: Fetching user 2 from database...
print(user2)  # Output: {'id': 2, 'name': 'Bob'}
```

### Caching API Requests

```python
import asyncio
import random
from datetime import timedelta
from py_cashier import cache
from py_cashier._storages import TTLMapStorage

@cache(storage=lambda: TTLMapStorage(ttl=timedelta(minutes=5)))
async def fetch_weather(city: str) -> dict:
    """Simulate fetching weather data from an API."""
    print(f"Fetching weather data for {city}...")
    # Simulate API request delay
    await asyncio.sleep(1)
    # Return simulated weather data
    return {
        "city": city,
        "temperature": random.randint(0, 30),
        "conditions": random.choice(["Sunny", "Cloudy", "Rainy"])
    }

async def main():
    # First call to the API
    weather1 = await fetch_weather("New York")
    print(f"Weather in New York: {weather1}")

    # Second call uses cached data
    weather2 = await fetch_weather("New York")
    print(f"Weather in New York (cached): {weather2}")

    # Different city makes a new API call
    weather3 = await fetch_weather("London")
    print(f"Weather in London: {weather3}")

asyncio.run(main())
```
