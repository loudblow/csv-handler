from __future__ import annotations

import abc
import argparse
import csv
import functools
import operator as op
import pathlib
import re
import statistics
import typing as t

import tabulate


T = t.TypeVar('T')
Table = t.Iterable[dict[str, t.Any]]
Columns = t.Iterable[str]
Operator = t.Callable[[t.Any, t.Any], bool]
AggregationFunc = t.Callable[[t.Iterable[float | int]], float | int]
ItemGetter = t.Callable[[t.Any], t.Any]
SortFunc = t.Callable[[t.Iterable[T], ItemGetter], t.Iterable[T]]


OPERATORS: dict[str, Operator] = {
    '>': op.gt,
    '<': op.lt,
    '=': op.eq,
}


AGGREGATION_FUNCS: dict[str, AggregationFunc] = {
    'avg': statistics.fmean,
    'med': statistics.median,
    'min': min,
    'max': max,
}


SORT_FUNCS: dict[str, SortFunc] = {
    'asc': sorted,
    'desc': functools.partial(sorted, reverse=True),
}


def validate_float(num: str | float) -> float:
    try:
        return float(num)
    except ValueError:
        return num


class Handler:
    def __init__(self, column: str, operator: Operator, value: str | float) -> None:
        self.column = column
        self.operator = operator
        self.value = value

    @classmethod
    def from_condition(cls, condition: str) -> Handler:
        condition_match: re.Match | None = re.match(
            r'^"?'
            r'(?P<column>\w+)'
            r'(?P<operator>[><=])'
            r'(?P<value>(\w|\d|\s|\.)+)'
            r'"?$', 
            string=condition.lower(),
        )
        if not condition_match:
            raise ValueError(f'Unmatched condition "{condition}"')
        
        return cls(
            column=condition_match['column'], 
            operator=OPERATORS[condition_match['operator']], 
            value=validate_float(condition_match['value']),
        )

    @abc.abstractmethod
    def __call__(self, table: Table) -> Table:
        pass


class Filter(Handler):
    def __call__(self, table: Table) -> Table:
        result: Table = []
        for row in table:
            value = validate_float(row[self.column])
            if self.operator(value, self.value):
                result.append(row)
        return result


class Aggregator(Handler):
    def __call__(self, table: Table) -> Table:
        column_values = map(lambda row: float(row[self.column]), table)
        func: AggregationFunc = AGGREGATION_FUNCS[self.value]
        return [{self.value: func(column_values)}]


class Sorter(Handler):
    def __call__(self, table: Table) -> Table:
        func: SortFunc = SORT_FUNCS[self.value]
        return func(table, key=lambda row: float(row[self.column]))


def handle_table(table: Table, columns: Columns, handlers: list[Handler | None]) -> Table:
    result = table
    for handler in handlers:
        if not handler:
            continue
        if handler.column not in columns:
            raise ValueError(f"There's no column '{handler.column}' in csv-file")
        result = handler(result)
    return result


def load_csv_file(path: str) -> tuple[Table, Columns]:
    file = pathlib.Path(path)
    if not file.exists() or not file.is_file():
        raise ValueError("File doesn't exists")
    with file.open('r') as f:
        dict_reader = csv.DictReader(f)
        return list(dict_reader), dict_reader.fieldnames


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='csv-handler')
    parser.add_argument(
        '--file', 
        required=True, 
        type=load_csv_file,
        dest='table_and_columns',
    )
    parser.add_argument(
        '--where', 
        type=Filter.from_condition, 
        default=None,
    )
    parser.add_argument(
        '--aggregate', 
        type=Aggregator.from_condition, 
        default=None,
    )
    parser.add_argument(
        '--order-by', 
        type=Sorter.from_condition, 
        default=None,
    )
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args: argparse.Namespace = parser.parse_args()
    table, columns = args.table_and_columns
    result: Table = handle_table(
        table=table, 
        columns=columns, 
        handlers=(args.where, args.order_by, args.aggregate),
    )
    print(tabulate.tabulate(result, headers='keys', tablefmt='grid'))