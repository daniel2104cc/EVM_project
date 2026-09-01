from decimal import Decimal

from app.services.evm_service import (
    CostStatus,
    EVMActivityInput,
    EVMService,
    ScheduleStatus,
)


def test_calculate_activity_metrics() -> None:
    result = EVMService.calculate_metrics(
        bac=Decimal(2000000),
        planned_progress=Decimal(60),
        actual_progress=Decimal(45),
        actual_cost=Decimal(1100000),
    )

    assert result.bac == Decimal(2000000)
    assert result.pv == Decimal(1200000)
    assert result.ev == Decimal(900000)
    assert result.actual_cost == Decimal(1100000)

    assert result.cv == Decimal(-200000)
    assert result.sv == Decimal(-300000)

    assert result.cpi == Decimal(900000) / Decimal(1100000)
    assert result.spi == Decimal(900000) / Decimal(1200000)

    assert result.cost_status == CostStatus.OVER_BUDGET
    assert result.schedule_status == ScheduleStatus.BEHIND_SCHEDULE

def test_cpi_is_not_available_when_actual_cost_is_zero() -> None:
    result = EVMService.calculate_metrics(
        bac=Decimal(1000000),
        planned_progress=Decimal(50),
        actual_progress=Decimal(40),
        actual_cost=Decimal(0),
    )

    assert result.cpi is None
    assert result.eac is None
    assert result.vac is None
    assert result.cost_status == CostStatus.NOT_AVAILABLE

def test_zero_actual_progress_produces_zero_cpi() -> None:
    result = EVMService.calculate_metrics(
        bac=Decimal(800000),
        planned_progress=Decimal(25),
        actual_progress=Decimal(0),
        actual_cost=Decimal(100000),
    )

    assert result.pv == Decimal(200000)
    assert result.ev == Decimal(0)
    assert result.cv == Decimal(-100000)
    assert result.sv == Decimal(-200000)

    assert result.cpi == Decimal(0)
    assert result.spi == Decimal(0)

    assert result.eac is None
    assert result.vac is None

    assert result.cost_status == CostStatus.OVER_BUDGET
    assert result.schedule_status == ScheduleStatus.BEHIND_SCHEDULE

def test_spi_is_not_available_when_planned_value_is_zero() -> None:
    result = EVMService.calculate_metrics(
        bac=Decimal(1000000),
        planned_progress=Decimal(0),
        actual_progress=Decimal(0),
        actual_cost=Decimal(0),
    )

    assert result.pv == Decimal(0)
    assert result.ev == Decimal(0)

    assert result.cpi is None
    assert result.spi is None

    assert result.cost_status == CostStatus.NOT_AVAILABLE
    assert result.schedule_status == ScheduleStatus.NOT_AVAILABLE

def test_project_without_activities_returns_empty_metrics() -> None:
    result = EVMService.calculate_project_metrics([])

    assert result.bac == Decimal(0)
    assert result.pv == Decimal(0)
    assert result.ev == Decimal(0)
    assert result.actual_cost == Decimal(0)

    assert result.cv == Decimal(0)
    assert result.sv == Decimal(0)

    assert result.cpi is None
    assert result.spi is None
    assert result.eac is None
    assert result.vac is None

    assert result.cost_status == CostStatus.NOT_AVAILABLE
    assert result.schedule_status == ScheduleStatus.NOT_AVAILABLE

def test_calculate_project_metrics() -> None:
    activities = [
        EVMActivityInput(
            bac=Decimal(1000000),
            planned_progress=Decimal(50),
            actual_progress=Decimal(40),
            actual_cost=Decimal(450000),
        ),
        EVMActivityInput(
            bac=Decimal(600000),
            planned_progress=Decimal(60),
            actual_progress=Decimal(50),
            actual_cost=Decimal(350000),
        ),
        EVMActivityInput(
            bac=Decimal(400000),
            planned_progress=Decimal(50),
            actual_progress=Decimal(50),
            actual_cost=Decimal(300000),
        ),
    ]

    result = EVMService.calculate_project_metrics(activities)

    assert result.bac == Decimal(2000000)
    assert result.pv == Decimal(1060000)
    assert result.ev == Decimal(900000)
    assert result.actual_cost == Decimal(1100000)

    assert result.cv == Decimal(-200000)
    assert result.sv == Decimal(-160000)

    assert result.cpi == Decimal(900000) / Decimal(1100000)
    assert result.spi == Decimal(900000) / Decimal(1060000)

    assert result.cost_status == CostStatus.OVER_BUDGET
    assert result.schedule_status == ScheduleStatus.BEHIND_SCHEDULE

def test_metrics_report_good_cost_and_schedule_performance() -> None:
    result = EVMService.calculate_metrics(
        bac=Decimal(1000000),
        planned_progress=Decimal(50),
        actual_progress=Decimal(60),
        actual_cost=Decimal(500000),
    )

    assert result.cpi == Decimal("1.2")
    assert result.spi == Decimal("1.2")

    assert result.cost_status == CostStatus.UNDER_BUDGET
    assert result.schedule_status == ScheduleStatus.AHEAD_OF_SCHEDULE

def test_metrics_report_on_budget_and_on_schedule() -> None:
    result = EVMService.calculate_metrics(
        bac=Decimal(1000000),
        planned_progress=Decimal(50),
        actual_progress=Decimal(50),
        actual_cost=Decimal(500000),
    )

    assert result.cpi == Decimal(1)
    assert result.spi == Decimal(1)

    assert result.cost_status == CostStatus.ON_BUDGET
    assert result.schedule_status == ScheduleStatus.ON_SCHEDULE