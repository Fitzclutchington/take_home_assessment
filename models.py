# Note: Base class was adjusted to ignore blackbox code

from dataclasses import dataclass, field
from typing import List, Optional, Union
from datetime import datetime
#from blackbox import parse_string_datetime, SnowflakeConnection


# dummy functions so we can import this code
def parse_string_datetime(time):
    pass

def upsert_to_spec_table(*args):
    pass

class FixedTime:
    def __init__(self, time: Union[datetime, str]):
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
# using kw_only to handle ordering of attributes in subclasses
@dataclass(kw_only=True)
class ReportSpec:
    report_type: str
    data_source: str
    model_group: Optional[str] = None
    # set this to None by default since instructions make no explicit mention
    # until Type III reports
    include_brands: Optional[List[str]] = None
    report_ranges: List[TimeRange]
    outcomes: List[str]

    # removed type hint for importing
    def upsert_report_spec(self, connection) -> None:
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
        for report_range in self.report_ranges:
            if report_range.start > report_range.end:
                raise ValueError("End date cannot come before start date")


# subclasses handle individual reports' validation
# including "model_group" as an attribute forces this model type
# to be included in the kwarg list
# e.g. TypeIReportSpec(report_ranges=[d1, d2]) will fail because
# model_group was not provided
@dataclass(kw_only=True)
class TypeIReportSpec(ReportSpec):
    model_group: str
    report_type: str = "Type I"
    data_source: str = "SYNDICATED"
    outcomes: List[str] = field(default_factory=lambda: ["site_visits", "product_searches"])
    
    def validate(self):
        super().validate()
        # ensure model_group is not None
        if not self.model_group:
            raise ValueError("Type I reports require a model group")


@dataclass(kw_only=True)
class TypeIIReportSpec(ReportSpec):
    data_source: str
    model_group: str
    report_type: str = "Type II"
    outcomes: List[str] = field(default_factory=lambda: ["site_visits", "product_searches"])

    def validate(self):
        super().validate()
        if not self.model_group:
            raise ValueError("Type II reports require a model group")
        if not self.data_source:
            raise ValueError("Type II reports require a data source")


@dataclass(kw_only=True)
class TypeIIIReportSpec(ReportSpec):
    data_source: str
    include_brands: List[str]
    outcomes: List[str] 
    report_type: str = "Type III"
    model_group: str = None
    

    def validate(self):
        super().validate()
        if not self.data_source:
            raise ValueError("Type III reports require a data source")
        if not self.include_brands:
            raise ValueError("At least one brand must be included for Type III reports.")