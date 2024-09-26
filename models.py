from dataclasses import dataclass, field
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

# Base class to handle inserting into DB and shared validation logic
# e.g, report range check
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

    def validate(self):
        if len(self.report_ranges) == 0:
            ValueError("At least one report range is required")


# subclasses handle individual reports' validation
@dataclass
class TypeIReportSpec(ReportSpec):
    report_type: str = "Type I"
    data_source: str = "SYNDICATED"
    model_group: str
    outcomes: List[str] = field(default_factory=lambda: ["site_visits", "product_searches"])
    def validate(self):
        super().validate()
        if not self.model_group:
            raise ValueError("Type I reports require a model group")


@dataclass
class TypeIIReportSpec(ReportSpec):
    report_type: str = "Type II"
    data_source: str
    model_group: str
    outcomes: List[str] = field(default_factory=lambda: ["site_visits", "product_searches"])

    def validate(self):
        super().validate()
        if not self.model_group:
            raise ValueError("Type II reports require a model group")
        if not self.data_source:
            raise ValueError("Type II reports require a data source")


@dataclass
class TypeIIIReportSpec(ReportSpec):
    report_type: str = "Type III"
    data_source: str
    model_group: str = None
    include_brands: List[str]
    outcomes: List[str] 

    def validate(self):
        super().validate()
        if not self.model_group:
            raise ValueError("Type III reports require a model group")
        if not self.data_source:
            raise ValueError("Type III reports require a data source")
        if not self.include_brands:
            raise ValueError("At least one brand must be included for Type III reports.")