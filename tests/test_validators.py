"""Tests for Pydantic validators."""
import pytest
from pydantic import ValidationError

from app.validators.salary import SalaryRow
from app.validators.allocation import AllocationRow
from app.validators.labor_transfer import LaborTransferRow


class TestSalaryRow:
    def test_valid_row(self):
        row = SalaryRow(
            部署コード='00000100',
            本給=300000,
            能力給=50000,
            報酬=20000,
            手当=30000,
            人員数=10,
            給与額=4000000,
        )
        assert row.部署コード == '00000100'
        assert row.本給 == 300000

    def test_comma_numbers_coerced(self):
        row = SalaryRow(
            部署コード='A01',
            本給='300,000',
            能力給='50,000',
            報酬='20,000',
            手当='30,000',
            人員数='10',
            給与額='4,000,000',
        )
        assert row.本給 == 300000

    def test_empty_department_code_raises(self):
        with pytest.raises(ValidationError):
            SalaryRow(部署コード='', 本給=0, 能力給=0, 報酬=0, 手当=0, 人員数=0, 給与額=0)

    def test_invalid_numeric_raises(self):
        with pytest.raises(ValidationError):
            SalaryRow(部署コード='X', 本給='abc', 能力給=0, 報酬=0, 手当=0, 人員数=0, 給与額=0)

    def test_negative_value_raises(self):
        with pytest.raises(ValidationError):
            SalaryRow(部署コード='X', 本給=-1, 能力給=0, 報酬=0, 手当=0, 人員数=0, 給与額=0)


class TestAllocationRow:
    def test_valid_row(self):
        row = AllocationRow(地区コード='10', 課コード='1111', 按分人員数=0.1)
        assert row.按分人員数 == pytest.approx(0.1)

    def test_empty_code_raises(self):
        with pytest.raises(ValidationError):
            AllocationRow(地区コード='', 課コード='1111', 按分人員数=0.1)


class TestLaborTransferRow:
    def test_valid_row(self):
        row = LaborTransferRow(勘定科目コード='5400010000', from課コード='5020', to課コード='3300', 作業時間=100.0)
        assert row.作業時間 == pytest.approx(100.0)

    def test_invalid_hours_raises(self):
        with pytest.raises(ValidationError):
            LaborTransferRow(勘定科目コード='X', from課コード='Y', to課コード='Z', 作業時間='invalid')
