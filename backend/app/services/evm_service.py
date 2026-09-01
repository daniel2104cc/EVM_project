from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

HUNDRED = Decimal(100)
ONE = Decimal(1)
ZERO = Decimal(0)


class CostStatus(str, Enum):
    UNDER_BUDGET = "UNDER_BUDGET"
    ON_BUDGET = "ON_BUDGET"
    OVER_BUDGET = "OVER_BUDGET"
    NOT_AVAILABLE = "NOT_AVAILABLE"


class ScheduleStatus(str, Enum):
    AHEAD_OF_SCHEDULE = "AHEAD_OF_SCHEDULE"
    ON_SCHEDULE = "ON_SCHEDULE"
    BEHIND_SCHEDULE = "BEHIND_SCHEDULE"
    NOT_AVAILABLE = "NOT_AVAILABLE"

@dataclass(frozen=True)
class EVMMetrics:
    bac: Decimal
    pv: Decimal
    ev: Decimal
    actual_cost: Decimal
    cv: Decimal
    sv: Decimal
    cpi: Decimal | None
    spi: Decimal | None
    eac: Decimal | None
    vac: Decimal | None
    cost_status: CostStatus
    schedule_status: ScheduleStatus
@dataclass(frozen=True)
class EVMActivityInput:
    bac: Decimal
    planned_progress: Decimal
    actual_progress: Decimal
    actual_cost: Decimal
    
class EVMService:
    @staticmethod
    def calculate_pv(bac: Decimal, planned_progress: Decimal) -> Decimal:
        return (planned_progress / HUNDRED) * bac

    @staticmethod
    def calculate_ev(bac: Decimal, actual_progress: Decimal) -> Decimal:
        return (actual_progress / HUNDRED) * bac

    @staticmethod
    def calculate_cv(ev: Decimal, actual_cost: Decimal) -> Decimal:
        return ev - actual_cost

    @staticmethod
    def calculate_sv(ev: Decimal, pv: Decimal) -> Decimal:
        return ev - pv

    @staticmethod
    def calculate_cpi(
        ev: Decimal,
        actual_cost: Decimal,
    ) -> Decimal | None:
        if actual_cost == ZERO:
            return None

        return ev / actual_cost

    @staticmethod
    def calculate_spi(
        ev: Decimal,
        pv: Decimal,
    ) -> Decimal | None:
        if pv == ZERO:
            return None

        return ev / pv

    @staticmethod
    def calculate_eac(
        bac: Decimal,
        cpi: Decimal | None,
    ) -> Decimal | None:
        if cpi is None or cpi == ZERO:
            return None

        return bac / cpi

    @staticmethod
    def calculate_vac(
        bac: Decimal,
        eac: Decimal | None,
    ) -> Decimal | None:
        if eac is None:
            return None

        return bac - eac

    @staticmethod
    def interpret_cpi(cpi: Decimal | None) -> CostStatus:
        if cpi is None:
            return CostStatus.NOT_AVAILABLE

        if cpi > ONE:
            return CostStatus.UNDER_BUDGET

        if cpi < ONE:
            return CostStatus.OVER_BUDGET

        return CostStatus.ON_BUDGET

    @staticmethod
    def interpret_spi(spi: Decimal | None) -> ScheduleStatus:
        if spi is None:
            return ScheduleStatus.NOT_AVAILABLE

        if spi > ONE:
            return ScheduleStatus.AHEAD_OF_SCHEDULE

        if spi < ONE:
            return ScheduleStatus.BEHIND_SCHEDULE

        return ScheduleStatus.ON_SCHEDULE

    @classmethod
    def calculate_metrics(
        cls,
        bac: Decimal,
        planned_progress: Decimal,
        actual_progress: Decimal,
        actual_cost: Decimal,
    ) -> EVMMetrics:
        pv = cls.calculate_pv(bac, planned_progress)
        ev = cls.calculate_ev(bac, actual_progress)

        cv = cls.calculate_cv(ev, actual_cost)
        sv = cls.calculate_sv(ev, pv)

        cpi = cls.calculate_cpi(ev, actual_cost)
        spi = cls.calculate_spi(ev, pv)

        eac = cls.calculate_eac(bac, cpi)
        vac = cls.calculate_vac(bac, eac)

        return EVMMetrics(
            bac=bac,
            pv=pv,
            ev=ev,
            actual_cost=actual_cost,
            cv=cv,
            sv=sv,
            cpi=cpi,
            spi=spi,
            eac=eac,
            vac=vac,
            cost_status=cls.interpret_cpi(cpi),
            schedule_status=cls.interpret_spi(spi),
        )
    @classmethod
    def calculate_project_metrics(
        cls,
        activities: list[EVMActivityInput],
    ) -> EVMMetrics:
        total_bac = ZERO
        total_pv = ZERO
        total_ev = ZERO
        total_actual_cost = ZERO

        for activity in activities:
            total_bac += activity.bac
            total_pv += cls.calculate_pv(
                activity.bac,
                activity.planned_progress,
            )
            total_ev += cls.calculate_ev(
                activity.bac,
                activity.actual_progress,
            )
            total_actual_cost += activity.actual_cost

        cv = cls.calculate_cv(total_ev, total_actual_cost)
        sv = cls.calculate_sv(total_ev, total_pv)

        cpi = cls.calculate_cpi(total_ev, total_actual_cost)
        spi = cls.calculate_spi(total_ev, total_pv)

        eac = cls.calculate_eac(total_bac, cpi)
        vac = cls.calculate_vac(total_bac, eac)

        return EVMMetrics(
            bac=total_bac,
            pv=total_pv,
            ev=total_ev,
            actual_cost=total_actual_cost,
            cv=cv,
            sv=sv,
            cpi=cpi,
            spi=spi,
            eac=eac,
            vac=vac,
            cost_status=cls.interpret_cpi(cpi),
            schedule_status=cls.interpret_spi(spi),
        )
