"""Tests for ValidationReport, CheckResult and enums."""

from __future__ import annotations

import pytest

from tempify.validation.report import (
    CheckPhase,
    CheckResult,
    CheckSeverity,
    ValidationReport,
)


def _result(code: str, severity: CheckSeverity, phase: CheckPhase, passed: bool) -> CheckResult:
    return CheckResult(
        check_id=code,
        name=f"check {code}",
        severity=severity,
        phase=phase,
        passed=passed,
        message="",
    )


def test_severity_enum_values() -> None:
    assert CheckSeverity.INFO == "info"
    assert CheckSeverity.WARN == "warn"
    assert CheckSeverity.ERROR == "error"


def test_phase_enum_values() -> None:
    assert CheckPhase.PRE_PROCESS == "pre"
    assert CheckPhase.POST_PROCESS == "post"


def test_report_partitions_by_severity() -> None:
    checks = (
        _result("A", CheckSeverity.INFO, CheckPhase.PRE_PROCESS, True),
        _result("B", CheckSeverity.WARN, CheckPhase.POST_PROCESS, True),
        _result("C", CheckSeverity.ERROR, CheckPhase.POST_PROCESS, False),
    )
    r = ValidationReport(checks=checks)
    assert len(r.info_items) == 1
    assert len(r.warnings) == 1
    assert len(r.errors) == 1


def test_report_pre_post_passed_flags() -> None:
    ok_pre = _result("pre-ok", CheckSeverity.INFO, CheckPhase.PRE_PROCESS, True)
    bad_post = _result("post-fail", CheckSeverity.ERROR, CheckPhase.POST_PROCESS, False)
    r = ValidationReport(checks=(ok_pre, bad_post))
    assert r.pre_passed is True
    assert r.post_passed is False
    assert r.has_warnings() is False


def test_report_is_immutable() -> None:
    r = ValidationReport(checks=())
    with pytest.raises((AttributeError, TypeError)):
        r.checks = ()  # type: ignore[misc]
