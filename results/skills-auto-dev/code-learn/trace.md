### Human
The test suite of the `inventory` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/inventory/', '/workspace/tests/']

### Tool call: ls
{"path": "workspace/inventory"}

### Tool result
['/workspace/inventory/__init__.py', '/workspace/inventory/__pycache__/', '/workspace/inventory/export.py', '/workspace/inventory/pricing.py', '/workspace/inventory/report.py']

### Tool call: ls
{"path": "workspace/tests"}

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_report.py']

### Tool call: execute
{"command": "python3 -m unittest discover workspace/tests"}

### Tool result
[stderr] E
[stderr] ======================================================================
[stderr] ERROR: test_report (unittest.loader._FailedTest.test_report)
[stderr] ----------------------------------------------------------------------
[stderr] ImportError: Failed to import test module: test_report
[stderr] Traceback (most recent call last):
[stderr]   File "/usr/local/lib/python3.12/unittest/loader.py", line 396, in _find_test_path
[stderr]     module = self._get_module_from_name(name)
[stderr]              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
[stderr]   File "/usr/local/lib/python3.12/unittest/loader.py", line 339, in _get_module_from_name
[stderr]     __import__(name)
[stderr]   File "/tmp/day20-agent-bzqnanz9/workspace/tests/test_report.py", line 3, in <module>
[stderr]     from inventory.export import to_csv_row
[stderr] ModuleNotFoundError: No module named 'inventory'
[stderr] 
[stderr] 
[stderr] ----------------------------------------------------------------------
[stderr] Ran 1 test in 0.000s
[stderr] 
[stderr] FAILED (errors=1)

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m unittest discover workspace/tests"}

### Tool result
[stderr] ----------------------------------------------------------------------
[stderr] Ran 0 tests in 0.000s
[stderr] 
[stderr] NO TESTS RAN

Exit code: 5
[Command failed with exit code 5]

### Tool call: read_file
{"file_path": "workspace/tests/test_report.py"}

### Tool result
@@ lines 1-32 of 32 @@
from decimal import Decimal

from inventory.export import to_csv_row
from inventory.pricing import apply_discount
from inventory.report import low_stock, total_value


def test_total_value_plain():
    items = [{"name": "pen", "price": "$2.50", "qty": 4}]
    assert total_value(items) == Decimal("10.00")


def test_total_value_thousands_separator():
    items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
    assert total_value(items) == Decimal("2599.00")


def test_discount_rounding_half_up():
    assert apply_discount(Decimal("10.05"), 10) == Decimal("9.05")


def test_total_value_with_discount():
    items = [{"name": "desk", "price": "100.00", "qty": 1, "discount": 15}]
    assert total_value(items) == Decimal("85.00")


def test_low_stock_basic():
    assert low_stock([{"name": "pen", "qty": 2}, {"name": "ink", "qty": 9}]) == ["pen"]


def test_csv_row_plain_name():
    assert to_csv_row({"name": "pen", "price": "2.5", "qty": 4}) == "pen,2.50,4"

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m pytest workspace/tests/test_report.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/day20-agent-bzqnanz9
plugins: anyio-4.15.1, langsmith-0.14.4
collected 6 items

workspace/tests/test_report.py .FF...                                    [100%]

=================================== FAILURES ===================================
_____________________ test_total_value_thousands_separator _____________________

    def test_total_value_thousands_separator():
        items = [{"name": "laptop", "price": "$1,299.50", "qty": 2}]
>       assert total_value(items) == Decimal("2599.00")
               ^^^^^^^^^^^^^^^^^^

/lab/tasks/code-learn/workspace/tests/test_report.py:15: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
workspace/inventory/report.py:14: in total_value
    price = parse_price(item["price"])
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

text = '$1,299.50'

    def parse_price(text):
        """Convert a price string to a Decimal.
    
        Supported formats:
          "$1,299.50" -> Decimal("1299.50")
          "  12 "     -> Decimal("12")
          "1299.5"    -> Decimal("1299.5")
          "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
        """
        cleaned = text.strip().replace("$", "")
>       return Decimal(cleaned)
               ^^^^^^^^^^^^^

### Tool call: read_file
{"file_path": "workspace/inventory/pricing.py"}

### Tool result
@@ lines 1-25 of 25 @@
"""Price utilities for the inventory package."""
from decimal import Decimal


def parse_price(text):
    """Convert a price string to a Decimal.

    Supported formats:
      "$1,299.50" -> Decimal("1299.50")
      "  12 "     -> Decimal("12")
      "1299.5"    -> Decimal("1299.5")
      "(12.00)"   -> Decimal("-12.00")   # accounting style: parentheses mean negative
    """
    cleaned = text.strip().replace("$", "")
    return Decimal(cleaned)


def apply_discount(price, percent):
    """Return `price` after a percentage discount.

    The result is a Decimal rounded to 2 decimal places using the
    commercial rule "round half up" (0.005 -> 0.01).
    """
    discounted = price * (100 - percent) / 100
    return discounted.quantize(Decimal("0.01"))

### Tool call: edit_file
{"new_string": "    cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    if cleaned.startswith(\"(\") and cleaned.endswith(\")\"):\n        cleaned = \"-\" + cleaned[1:-1]\n    return Decimal(cleaned)", "old_string": "    cleaned = text.strip().replace(\"$\", \"\")\n    return Decimal(cleaned)", "file_path": "workspace/inventory/pricing.py"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: edit_file
{"file_path": "workspace/inventory/pricing.py", "new_string": "from decimal import Decimal, ROUND_HALF_UP\n\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    if cleaned.startswith(\"(\") and cleaned.endswith(\")\"):\n        cleaned = \"-\" + cleaned[1:-1]\n    return Decimal(cleaned)\n\n\ndef apply_discount(price, percent):\n    \"\"\"Return `price` after a percentage discount.\n\n    The result is a Decimal rounded to 2 decimal places using the\n    commercial rule \"round half up\" (0.005 -> 0.01).\n    \"\"\"\n    discounted = price * (100 - percent) / 100\n    return discounted.quantize(Decimal(\"0.01\"), rounding=ROUND_HALF_UP)", "old_string": "from decimal import Decimal\n\n\ndef parse_price(text):\n    \"\"\"Convert a price string to a Decimal.\n\n    Supported formats:\n      \"$1,299.50\" -> Decimal(\"1299.50\")\n      \"  12 \"     -> Decimal(\"12\")\n      \"1299.5\"    -> Decimal(\"1299.5\")\n      \"(12.00)\"   -> Decimal(\"-12.00\")   # accounting style: parentheses mean negative\n    \"\"\"\n    cleaned = text.strip().replace(\"$\", \"\").replace(\",\", \"\")\n    if cleaned.startswith(\"(\") and cleaned.ends

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/pricing.py'

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m pytest workspace/tests/test_report.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/day20-agent-bzqnanz9
plugins: anyio-4.15.1, langsmith-0.14.4
collected 6 items

workspace/tests/test_report.py ......                                    [100%]

============================== 6 passed in 0.06s ===============================

[Command succeeded with exit code 0]

### Tool call: read_file
{"file_path": "workspace/inventory/report.py"}

### Tool result
@@ lines 1-25 of 25 @@
"""Inventory reports."""
from decimal import Decimal

from .pricing import apply_discount, parse_price


def total_value(items):
    """Total value of `items` after per-item discounts.

    Each item is a dict: {"name": str, "price": str, "qty": int, "discount": percent (optional)}.
    """
    total = Decimal("0")
    for item in items:
        price = parse_price(item["price"])
        price = apply_discount(price, item.get("discount", 0))
        total += price * item["qty"]
    return total


def low_stock(items, threshold=5):
    """Names of the items whose quantity is strictly below `threshold`.

    The names are sorted alphabetically, ignoring case.
    """
    return [item["name"] for item in items if item["qty"] <= threshold]

### Tool call: edit_file
{"old_string": "def low_stock(items, threshold=5):\n    \"\"\"Names of the items whose quantity is strictly below `threshold`.\n\n    The names are sorted alphabetically, ignoring case.\n    \"\"\"\n    return [item[\"name\"] for item in items if item[\"qty\"] <= threshold]", "file_path": "workspace/inventory/report.py", "new_string": "def low_stock(items, threshold=5):\n    \"\"\"Names of the items whose quantity is strictly below `threshold`.\n\n    The names are sorted alphabetically, ignoring case.\n    \"\"\"\n    names = [item[\"name\"] for item in items if item[\"qty\"] < threshold]\n    return sorted(names, key=str.lower)"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/report.py'

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m pytest workspace/tests/test_report.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/day20-agent-bzqnanz9
plugins: anyio-4.15.1, langsmith-0.14.4
collected 6 items

workspace/tests/test_report.py ......                                    [100%]

============================== 6 passed in 0.06s ===============================

[Command succeeded with exit code 0]

### Tool call: read_file
{"file_path": "workspace/inventory/export.py"}

### Tool result
@@ lines 1-12 of 12 @@
"""Export helpers."""
from .pricing import parse_price


def to_csv_row(item):
    """Format one item as a CSV row: name,price,qty (price with 2 decimals).

    A name that contains a comma or a double quote is wrapped in double quotes,
    and every double quote inside it is doubled (RFC 4180).
    """
    price = parse_price(item["price"])
    return f'{item["name"]},{price:.2f},{item["qty"]}'

### Tool call: edit_file
{"new_string": "def to_csv_row(item):\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    name = item[\"name\"]\n    if \",\" in name or '\"' in name:\n        name = '\"' + name.replace('\"', '\"\"') + '\"'\n    price = parse_price(item[\"price\"])\n    return f'{name},{price:.2f},{item[\"qty\"]}'", "old_string": "def to_csv_row(item):\n    \"\"\"Format one item as a CSV row: name,price,qty (price with 2 decimals).\n\n    A name that contains a comma or a double quote is wrapped in double quotes,\n    and every double quote inside it is doubled (RFC 4180).\n    \"\"\"\n    price = parse_price(item[\"price\"])\n    return f'{item[\"name\"]},{price:.2f},{item[\"qty\"]}'", "file_path": "workspace/inventory/export.py"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/inventory/export.py'

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m pytest workspace/tests/test_report.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/day20-agent-bzqnanz9
plugins: anyio-4.15.1, langsmith-0.14.4
collected 6 items

workspace/tests/test_report.py ......                                    [100%]

============================== 6 passed in 0.05s ===============================

[Command succeeded with exit code 0]

### Tool call: execute
{"command": "cat <<EOF > workspace/tests/test_extra.py\nfrom decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.report import low_stock\nfrom inventory.export import to_csv_row\n\ndef test_parse_price_extra():\n    assert parse_price(\"(12.00)\") == Decimal(\"-12.00\")\n\ndef test_low_stock_extra():\n    items = [{\"name\": \"Pen\", \"qty\": 2}, {\"name\": \"ink\", \"qty\": 4}, {\"name\": \"Book\", \"qty\": 6}]\n    assert low_stock(items) == [\"ink\", \"Pen\"]\n\ndef test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\" ,2.50,4'\nEOF\nexport PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m pytest workspace/tests/test_extra.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/day20-agent-bzqnanz9
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

workspace/tests/test_extra.py ..F                                        [100%]

=================================== FAILURES ===================================
____________________________ test_to_csv_row_extra _____________________________

    def test_to_csv_row_extra():
>       assert to_csv_row({"name": 'pen, "blue"', "price": "2.5", "qty": 4}) == '"pen, ""blue""" ,2.50,4'
E       assert '"pen, ""blue""",2.50,4' == '"pen, ""blue""" ,2.50,4'
E         
E         - "pen, ""blue""" ,2.50,4
E         ?                -
E         + "pen, ""blue""",2.50,4

workspace/tests/test_extra.py:14: AssertionError
=========================== short test summary info ============================
FAILED workspace/tests/test_extra.py::test_to_csv_row_extra - assert '"pen, "...
========================= 1 failed, 2 passed in 0.04s ==========================

Exit code: 1
[Command failed with exit code 1]

### Tool call: edit_file
{"new_string": "def test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\",2.50,4\"", "old_string": "def test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\" ,2.50,4\"", "file_path": "workspace/tests/test_extra.py"}

### Tool result
Error: String not found in file: 'def test_to_csv_row_extra():
    assert to_csv_row({"name": 'pen, "blue"', "price": "2.5", "qty": 4}) == '"pen, ""blue""" ,2.50,4"'

### Tool call: read_file
{"file_path": "workspace/tests/test_extra.py"}

### Tool result
@@ lines 1-14 of 14 @@
from decimal import Decimal
from inventory.pricing import parse_price, apply_discount
from inventory.report import low_stock
from inventory.export import to_csv_row

def test_parse_price_extra():
    assert parse_price("(12.00)") == Decimal("-12.00")

def test_low_stock_extra():
    items = [{"name": "Pen", "qty": 2}, {"name": "ink", "qty": 4}, {"name": "Book", "qty": 6}]
    assert low_stock(items) == ["ink", "Pen"]

def test_to_csv_row_extra():
    assert to_csv_row({"name": 'pen, "blue"', "price": "2.5", "qty": 4}) == '"pen, ""blue""" ,2.50,4'

### Tool call: edit_file
{"old_string": "def test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\" ,2.50,4\"'", "file_path": "workspace/tests/test_extra.py", "new_string": "def test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\",2.50,4\"'"}

### Tool result
Error: String not found in file: 'def test_to_csv_row_extra():
    assert to_csv_row({"name": 'pen, "blue"', "price": "2.5", "qty": 4}) == '"pen, ""blue""" ,2.50,4"''

### Tool call: write_file
{"content": "from decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.report import low_stock\nfrom inventory.export import to_csv_row\n\ndef test_parse_price_extra():\n    assert parse_price(\"(12.00)\") == Decimal(\"-12.00\")\n\ndef test_low_stock_extra():\n    items = [{\"name\": \"Pen\", \"qty\": 2}, {\"name\": \"ink\", \"qty\": 4}, {\"name\": \"Book\", \"qty\": 6}]\n    assert low_stock(items) == [\"ink\", \"Pen\"]\n\ndef test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\",2.50,4\"'\n", "file_path": "workspace/tests/test_extra.py"}

### Tool result
Updated file /workspace/tests/test_extra.py

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m pytest workspace/tests/test_extra.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/day20-agent-bzqnanz9
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

workspace/tests/test_extra.py ..F                                        [100%]

=================================== FAILURES ===================================
____________________________ test_to_csv_row_extra _____________________________

    def test_to_csv_row_extra():
>       assert to_csv_row({"name": 'pen, "blue"', "price": "2.5", "qty": 4}) == '"pen, ""blue""",2.50,4"'
E       assert '"pen, ""blue""",2.50,4' == '"pen, ""blue""",2.50,4"'
E         
E         - "pen, ""blue""",2.50,4"
E         ?                       -
E         + "pen, ""blue""",2.50,4

workspace/tests/test_extra.py:14: AssertionError
=========================== short test summary info ============================
FAILED workspace/tests/test_extra.py::test_to_csv_row_extra - assert '"pen, "...
========================= 1 failed, 2 passed in 0.03s ==========================

Exit code: 1
[Command failed with exit code 1]

### Tool call: write_file
{"content": "from decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.report import low_stock\nfrom inventory.export import to_csv_row\n\ndef test_parse_price_extra():\n    assert parse_price(\"(12.00)\") == Decimal(\"-12.00\")\n\ndef test_low_stock_extra():\n    items = [{\"name\": \"Pen\", \"qty\": 2}, {\"name\": \"ink\", \"qty\": 4}, {\"name\": \"Book\", \"qty\": 6}]\n    assert low_stock(items) == [\"ink\", \"Pen\"]\n\ndef test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\",2.50,4\"'\n", "file_path": "workspace/tests/test_extra.py"}

### Tool result
Updated file /workspace/tests/test_extra.py

### Tool call: execute
{"command": "python3 -c 'from inventory.export import to_csv_row; print(to_csv_row({\"name\": \"pen, \\\"blue\\\"\", \"price\": \"2.5\", \"qty\": 4}))'"}

### Tool result
[stderr] Traceback (most recent call last):
[stderr]   File "<string>", line 1, in <module>
[stderr] ModuleNotFoundError: No module named 'inventory'

Exit code: 1
[Command failed with exit code 1]

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -c 'from inventory.export import to_csv_row; print(to_csv_row({\"name\": \"pen, \\\"blue\\\"\", \"price\": \"2.5\", \"qty\": 4}))'"}

### Tool result
"pen, ""blue""",2.50,4

[Command succeeded with exit code 0]

### Tool call: write_file
{"content": "from decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.report import low_stock\nfrom inventory.export import to_csv_row\n\ndef test_parse_price_extra():\n    assert parse_price(\"(12.00)\") == Decimal(\"-12.00\")\n\ndef test_low_stock_extra():\n    items = [{\"name\": \"Pen\", \"qty\": 2}, {\"name\": \"ink\", \"qty\": 4}, {\"name\": \"Book\", \"qty\": 6}]\n    assert low_stock(items) == [\"ink\", \"Pen\"]\n\ndef test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\",2.50,4\"'\n", "file_path": "workspace/tests/test_extra.py"}

### Tool result
Updated file /workspace/tests/test_extra.py

### Tool call: execute
{"command": "export PYTHONPATH=$PYTHONPATH:$(pwd)/workspace && python3 -m pytest workspace/tests/test_extra.py"}

### Tool result
============================= test session starts ==============================
platform linux -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: /tmp/day20-agent-bzqnanz9
plugins: anyio-4.15.1, langsmith-0.14.4
collected 3 items

workspace/tests/test_extra.py ..F                                        [100%]

=================================== FAILURES ===================================
____________________________ test_to_csv_row_extra _____________________________

    def test_to_csv_row_extra():
>       assert to_csv_row({"name": 'pen, "blue"', "price": "2.5", "qty": 4}) == '"pen, ""blue""",2.50,4"'
E       assert '"pen, ""blue""",2.50,4' == '"pen, ""blue""",2.50,4"'
E         
E         - "pen, ""blue""",2.50,4"
E         ?                       -
E         + "pen, ""blue""",2.50,4

workspace/tests/test_extra.py:14: AssertionError
=========================== short test summary info ============================
FAILED workspace/tests/test_extra.py::test_to_csv_row_extra - assert '"pen, "...
========================= 1 failed, 2 passed in 0.03s ==========================

Exit code: 1
[Command failed with exit code 1]

### Tool call: write_file
{"content": "from decimal import Decimal\nfrom inventory.pricing import parse_price, apply_discount\nfrom inventory.report import low_stock\nfrom inventory.export import to_csv_row\n\ndef test_parse_price_extra():\n    assert parse_price(\"(12.00)\") == Decimal(\"-12.00\")\n\ndef test_low_stock_extra():\n    items = [{\"name\": \"Pen\", \"qty\": 2}, {\"name\": \"ink\", \"qty\": 4}, {\"name\": \"Book\", \"qty\": 6}]\n    assert low_stock(items) == [\"ink\", \"Pen\"]\n\ndef test_to_csv_row_extra():\n    assert to_csv_row({\"name\": 'pen, \"blue\"', \"price\": \"2.5\", \"qty\": 4}) == '\"pen, \"\"blue\"\"\",2.50,4'\n", "file_path": "workspace/tests/test_extra.py"}

### Tool result
Updated file /workspace/tests/test_extra.py