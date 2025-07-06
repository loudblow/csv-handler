import pytest

from main import (
    OPERATORS,
    AGGREGATION_FUNCS,
    SORT_FUNCS,
    Aggregator,
    Sorter,
    Handler,
    Table,
    Filter,
    handle_table,
    load_csv_file,
    validate_float,
    get_parser,
)


@pytest.fixture(autouse=True)
def table():
    yield [
        {'name': 'iphone 15 pro', 'brand': 'apple', 'price': '999', 'rating': '4.9'},
        {'name': 'galaxy s23 ultra', 'brand': 'samsung', 'price': '1199', 'rating': '4.8'},
        {'name': 'redmi note 12', 'brand': 'xiaomi', 'price': '199', 'rating': '4.6'},
        {'name': 'iphone 14', 'brand': 'apple', 'price': '799', 'rating': '4.7'},
        {'name': 'galaxy a54', 'brand': 'samsung', 'price': '349', 'rating': '4.2'},
        {'name': 'poco x5 pro', 'brand': 'xiaomi', 'price': '299', 'rating': '4.4'},
        {'name': 'iphone se', 'brand': 'apple', 'price': '429', 'rating': '4.1'},
        {'name': 'galaxy z flip 5', 'brand': 'samsung', 'price': '999', 'rating': '4.6'},
        {'name': 'redmi 10c', 'brand': 'xiaomi', 'price': '149', 'rating': '4.1'},
        {'name': 'iphone 13 mini', 'brand': 'apple', 'price': '599', 'rating': '4.5'},
    ]


@pytest.fixture(autouse=True)
def columns():
    yield ['name', 'brand', 'price', 'rating']


@pytest.mark.parametrize(
    'string, expected',
    [
        ('1', 1.0),
        ('0', 0.0),
        ('-1', -1.0),
        ('3.6e2', 360),
        ('jjjj', 'jjjj')
    ],
)
def test_validate_float(string, expected):
    assert validate_float(string) == expected


@pytest.mark.parametrize(
    'operator, a, b, expected',
    [
        ('>', 2, 1.0, True),
        ('>', 1, 1.0, False),
        ('>', 1, 2.0, False),

        ('<', 2, 1.0, False),
        ('<', 1, 2.0, True),
        ('<', 1, 1.0, False),

        ('=', 2, 1.0, False),
        ('=', 1, 2.0, False),
        ('=', 1, 1.0, True),
    ]
)
def test_operators(operator, a, b, expected):
    func = OPERATORS.get(operator)
    assert func != None
    assert func(a, b) == expected


@pytest.mark.parametrize(
    'mode,iterable,expected',
    [
        ('avg', [0, 1, 2, 3, 4], 2),
        ('avg', [0, 1, 2, 3, 4, 4, 4, 4], 2.75),

        ('med', [0, 1, 2, 3, 4], 2),
        ('med', [0, 1, 2, 3, 4, 4, 4, 4], 3.5),

        ('min', [0, 1, 2, 3, 4], 0),
        ('min', [0, 1, 2, 3, 4, 4, 4, 4], 0),

        ('max', [0, 1, 2, 3, 4], 4),
        ('max', [0, 1, 2, 3, 4, 4, 4, 4], 4),
    ]
)
def test_aggregation_funcs(mode, iterable, expected):
    func = AGGREGATION_FUNCS.get(mode)
    assert func != None
    assert func(iterable) == expected


@pytest.mark.parametrize(
    'mode,key,iterable,expected',
    [
        (
            'asc', 
            'a', 
            [{'a': 2}, {'a': 0}, {'a': 1}, {'a': 3}, {'a': 4}], 
            [{'a': 0}, {'a': 1}, {'a': 2}, {'a': 3}, {'a': 4}],
        ),

        (
            'desc', 
            'a', 
            [{'a': 2}, {'a': 0}, {'a': 1}, {'a': 3}, {'a': 4}],
            [{'a': 4}, {'a': 3}, {'a': 2}, {'a': 1}, {'a': 0}],
        ),
    ]
)
def test_sort_funcs(mode, key, iterable, expected):
    func = SORT_FUNCS.get(mode)
    assert func != None
    assert func(iterable, key=lambda row: row[key]) == expected


class MockHandler(Handler):
    def __call__(self, table: Table) -> Table:
        return []


class TestMockHandler:
    def test_init(self):
        handler = MockHandler(
            column='a', 
            operator=lambda a, b: a == b,
            value='123',
        )
        assert handler.column == 'a'
        assert handler.operator(1, 1) == True
        assert handler.value == '123'
    
    def test_from_condition(self) -> None:
        handler = MockHandler.from_condition('a=123')
        assert handler.column == 'a'
        assert handler.operator(1, 1) == True
        assert handler.value == 123

        with pytest.raises(ValueError) as e_info:
            handler = MockHandler.from_condition('a=')
        
        with pytest.raises(ValueError) as e_info:
            handler = MockHandler.from_condition('a+1')
        
        with pytest.raises(ValueError) as e_info:
            handler = MockHandler.from_condition('a>=1')
    
    def test_call(self) -> None:
        handler = MockHandler.from_condition('a=123')
        assert handler([{'a': 1}]) == []


@pytest.mark.parametrize(
    'condition,expected',
    [
        (
            'brand=apple', 
            [
                {'name': 'iphone 15 pro', 'brand': 'apple', 'price': '999', 'rating': '4.9'},
                {'name': 'iphone 14', 'brand': 'apple', 'price': '799', 'rating': '4.7'},
                {'name': 'iphone se', 'brand': 'apple', 'price': '429', 'rating': '4.1'},
                {'name': 'iphone 13 mini', 'brand': 'apple', 'price': '599', 'rating': '4.5'},
            ]
        ),
        (
            'price<350', 
            [
                {'name': 'redmi note 12', 'brand': 'xiaomi', 'price': '199', 'rating': '4.6'},
                {'name': 'galaxy a54', 'brand': 'samsung', 'price': '349', 'rating': '4.2'},
                {'name': 'poco x5 pro', 'brand': 'xiaomi', 'price': '299', 'rating': '4.4'},
                {'name': 'redmi 10c', 'brand': 'xiaomi', 'price': '149', 'rating': '4.1'},
            ]
        ),
        (
            'rating>4.5', 
            [
                {'name': 'iphone 15 pro', 'brand': 'apple', 'price': '999', 'rating': '4.9'},
                {'name': 'galaxy s23 ultra', 'brand': 'samsung', 'price': '1199', 'rating': '4.8'},
                {'name': 'redmi note 12', 'brand': 'xiaomi', 'price': '199', 'rating': '4.6'},
                {'name': 'iphone 14', 'brand': 'apple', 'price': '799', 'rating': '4.7'},
                {'name': 'galaxy z flip 5', 'brand': 'samsung', 'price': '999', 'rating': '4.6'},
            ]
        ),
        (
            'price=1199', 
            [{'name': 'galaxy s23 ultra', 'brand': 'samsung', 'price': '1199', 'rating': '4.8'}]
        ),
    ]
)
def test_filter(condition, expected, table):
    handler = Filter.from_condition(condition)
    result = handler(table)

    for item in result:
        assert item in expected

    for item in expected:
        assert item in result


@pytest.mark.parametrize(
    'condition,expected',
    [
        ('price=med', [{'med': 514}]),
        ('price=avg', [{'avg': 602}]),
        ('price=min', [{'min': 149}]),
        ('price=max', [{'max': 1199}]),
    ]
)
def test_aggregator(condition, expected, table):
    handler = Aggregator.from_condition(condition)
    result = handler(table)

    assert result == expected


@pytest.mark.parametrize(
    'condition,expected',
    [
        (
            'price=asc', 
            [
                {'name': 'redmi 10c', 'brand': 'xiaomi', 'price': '149', 'rating': '4.1'},
                {'name': 'redmi note 12', 'brand': 'xiaomi', 'price': '199', 'rating': '4.6'},
                {'name': 'poco x5 pro', 'brand': 'xiaomi', 'price': '299', 'rating': '4.4'},
                {'name': 'galaxy a54', 'brand': 'samsung', 'price': '349', 'rating': '4.2'},
                {'name': 'iphone se', 'brand': 'apple', 'price': '429', 'rating': '4.1'},
                {'name': 'iphone 13 mini', 'brand': 'apple', 'price': '599', 'rating': '4.5'},
                {'name': 'iphone 14', 'brand': 'apple', 'price': '799', 'rating': '4.7'},
                {'name': 'iphone 15 pro', 'brand': 'apple', 'price': '999', 'rating': '4.9'},
                {'name': 'galaxy z flip 5', 'brand': 'samsung', 'price': '999', 'rating': '4.6'},
                {'name': 'galaxy s23 ultra', 'brand': 'samsung', 'price': '1199', 'rating': '4.8'},
            ]
        ),
        (
            'price=desc', 
            [
                {'name': 'galaxy s23 ultra', 'brand': 'samsung', 'price': '1199', 'rating': '4.8'},
                {'name': 'iphone 15 pro', 'brand': 'apple', 'price': '999', 'rating': '4.9'},
                {'name': 'galaxy z flip 5', 'brand': 'samsung', 'price': '999', 'rating': '4.6'},
                {'name': 'iphone 14', 'brand': 'apple', 'price': '799', 'rating': '4.7'},
                {'name': 'iphone 13 mini', 'brand': 'apple', 'price': '599', 'rating': '4.5'},
                {'name': 'iphone se', 'brand': 'apple', 'price': '429', 'rating': '4.1'},
                {'name': 'galaxy a54', 'brand': 'samsung', 'price': '349', 'rating': '4.2'},
                {'name': 'poco x5 pro', 'brand': 'xiaomi', 'price': '299', 'rating': '4.4'},
                {'name': 'redmi note 12', 'brand': 'xiaomi', 'price': '199', 'rating': '4.6'},
                {'name': 'redmi 10c', 'brand': 'xiaomi', 'price': '149', 'rating': '4.1'},
            ]
        ),
    ]
)
def test_sorter(condition, expected, table):
    handler = Sorter.from_condition(condition)
    result = handler(table)

    assert result == expected


@pytest.mark.parametrize(
    'handlers,expected',
    [
        (
            (None, None, None), 
            [
                {'name': 'iphone 15 pro', 'brand': 'apple', 'price': '999', 'rating': '4.9'},
                {'name': 'galaxy s23 ultra', 'brand': 'samsung', 'price': '1199', 'rating': '4.8'},
                {'name': 'redmi note 12', 'brand': 'xiaomi', 'price': '199', 'rating': '4.6'},
                {'name': 'iphone 14', 'brand': 'apple', 'price': '799', 'rating': '4.7'},
                {'name': 'galaxy a54', 'brand': 'samsung', 'price': '349', 'rating': '4.2'},
                {'name': 'poco x5 pro', 'brand': 'xiaomi', 'price': '299', 'rating': '4.4'},
                {'name': 'iphone se', 'brand': 'apple', 'price': '429', 'rating': '4.1'},
                {'name': 'galaxy z flip 5', 'brand': 'samsung', 'price': '999', 'rating': '4.6'},
                {'name': 'redmi 10c', 'brand': 'xiaomi', 'price': '149', 'rating': '4.1'},
                {'name': 'iphone 13 mini', 'brand': 'apple', 'price': '599', 'rating': '4.5'},
            ]
        ),
        (
            (Filter.from_condition('brand=apple'), Aggregator.from_condition('price=max')),
            [{'max': 999}],
        ),
        (
            (Filter.from_condition('brand=apple'), Sorter.from_condition('price=asc')),
            [
                {'name': 'iphone se', 'brand': 'apple', 'price': '429', 'rating': '4.1'},
                {'name': 'iphone 13 mini', 'brand': 'apple', 'price': '599', 'rating': '4.5'},
                {'name': 'iphone 14', 'brand': 'apple', 'price': '799', 'rating': '4.7'},
                {'name': 'iphone 15 pro', 'brand': 'apple', 'price': '999', 'rating': '4.9'},
            ]
        ),
        (
            (Filter.from_condition('abc=123'),),
            ValueError,
        )
    ]
)
def test_handle_table(handlers, expected, table, columns):
    if expected == ValueError:
        with pytest.raises(ValueError):
            handle_table(table, columns, handlers)
    else:
        assert handle_table(table, columns, handlers) == expected


@pytest.mark.parametrize(
    'path,expected',
    [
        ('a.csv', ValueError),
        (
            'products.csv',
            (
                [
                    {'name': 'iphone 15 pro', 'brand': 'apple', 'price': '999', 'rating': '4.9'},
                    {'name': 'galaxy s23 ultra', 'brand': 'samsung', 'price': '1199', 'rating': '4.8'},
                    {'name': 'redmi note 12', 'brand': 'xiaomi', 'price': '199', 'rating': '4.6'},
                    {'name': 'iphone 14', 'brand': 'apple', 'price': '799', 'rating': '4.7'},
                    {'name': 'galaxy a54', 'brand': 'samsung', 'price': '349', 'rating': '4.2'},
                    {'name': 'poco x5 pro', 'brand': 'xiaomi', 'price': '299', 'rating': '4.4'},
                    {'name': 'iphone se', 'brand': 'apple', 'price': '429', 'rating': '4.1'},
                    {'name': 'galaxy z flip 5', 'brand': 'samsung', 'price': '999', 'rating': '4.6'},
                    {'name': 'redmi 10c', 'brand': 'xiaomi', 'price': '149', 'rating': '4.1'},
                    {'name': 'iphone 13 mini', 'brand': 'apple', 'price': '599', 'rating': '4.5'},
                ],
                ['name', 'brand', 'price', 'rating'],
            )
        ),
    ]
)
def test_load_csv_file(path, expected):
    if expected == ValueError:
        with pytest.raises(ValueError):
            load_csv_file(path)
    else:
        assert load_csv_file(path) == expected


@pytest.mark.parametrize(
    'args, expected',
    [
        (
            '--file products.csv'.split(' '),
            {'table_and_columns': tuple, 'where': type(None), 'aggregate': type(None), 'order_by': type(None)},
        ),
        (
            '--file products.csv --where "a=1" --order-by "a=asc" --aggregate "a=min"'.split(' '),
            {'table_and_columns': tuple, 'where': Filter, 'aggregate': Aggregator, 'order_by': Sorter},
        ),
    ]
)
def test_parser(args, expected):
    parser = get_parser()

    args = parser.parse_args(args)
    assert isinstance(args.table_and_columns, expected['table_and_columns'])
    assert isinstance(args.where, expected['where'])
    assert isinstance(args.aggregate, expected['aggregate'])
    assert isinstance(args.order_by, expected['order_by'])