from dataclasses import dataclass
from typing import List, Optional, Union
from datetime import datetime
from blackbox import parse_string_datetime, SnowflakeConnection


class FixedTime:
    def __init__(self, time: Union[datetime, AbstractTime, str]):
        if isinstance(time, datetime):
            self.time = time
        else:
            self.time = parse_string_datetime(time)


@dataclass
class TimeRange:
    start: FixedTime
    end: FixedTime


@dataclass
class ReportSpec:
    report_type: str
    data_source: str
    model_group: Optional[str]
    include_brands: List[str]
    report_ranges: List[TimeRange]
    outcomes: List[str]

    def upsert_report_spec(self, connection: SnowflakeConnection) -> None:
        """Inserts row in report spec table with metadata"""
        upsert_to_spec_table(
            connection,
            self.model_group,
            self.outcomes,
            self.report_type,
            self.data_source,
            self.report_ranges,
            self.include_brands,
        )

