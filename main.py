from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import TypeIReportSpec, TypeIIReportSpec, TypeIIIReportSpec, TimeRange

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("report_form.html", {"request": request})


@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    data_source: str = Form(None),
    model_group: str = Form(None),
    outcomes: str = Form(None),
    include_brands: str = Form(None),
    start_date: str = Form(...),
    end_date: str = Form(...),
):

    try:
        # Split input fields
        outcomes_list = outcomes.split(",") if outcomes else []
        brands_list = include_brands.split(",") if include_brands else None

        # Create a TimeRange object for the provided start and end dates
        # Made this a single datetime range, not sure
        report_ranges = [TimeRange(start=start_date, end=end_date)]

        # Determine report type based on input
        default_outcomes = ["site_visits", "product_searches"]
        if not data_source and not outcomes:
            # Type I: No custom data source or outcomes
            report = TypeIReportSpec(
                model_group=model_group,
                include_brands=brands_list,
                report_ranges=report_ranges,
                outcomes=default_outcomes,
            )
        elif data_source and not outcomes:
            # Type II: Custom data source, default outcomes
            report = TypeIIReportSpec(
                data_source=data_source,
                model_group=model_group,
                report_ranges=report_ranges,
                outcomes=default_outcomes,
            )
        elif data_source and outcomes:
            # Type III: Custom outcomes or data source
            report = TypeIIIReportSpec(
                data_source=data_source,
                include_brands=brands_list,
                report_ranges=report_ranges,
                outcomes=outcomes_list,
            )
        else:
            raise ValueError("Cannot provide outcomes without data source")

        # Perform validation
        report.validate()

        return templates.TemplateResponse(
            "report_form.html",
            {
                "request": request,
                "message": f"{report.report_type} report successfully created!",
            },
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "report_form.html",
            {"request": request, "message": f"Validation error: {str(e)}"},
        )
