"""Tests for Pydantic validators."""
import pytest
from pydantic import ValidationError

from app.validators.salary import SalaryRow
from app.validators.allocation import AllocationRow
from app.validators.labor_transfer import LaborTransferRow


class TestSalaryRow:
    def test_valid_row(self):
        row = SalaryRow(
            行ラベル='00000100',
            本給=300000,
            能力給=50000,
            職務役割給=20000,
            役割業績給=30000,
        )
        assert row.行ラベル == '00000100'
        assert row.本給 == 300000

    def test_comma_numbers_coerced(self):
        row = SalaryRow(
            行ラベル='A01',
            本給='300,000',
            能力給='50,000',
            職務役割給='20,000',
            役割業績給='30,000',
        )
        assert row.本給 == 300000

    def test_empty_row_label_raises(self):
        with pytest.raises(ValidationError):
            SalaryRow(行ラベル='', 本給=0, 能力給=0, 職務役割給=0, 役割業績給=0)

    def test_invalid_numeric_raises(self):
        with pytest.raises(ValidationError):
            SalaryRow(行ラベル='X', 本給='abc', 能力給=0, 職務役割給=0, 役割業績給=0)

    def test_missing_row_label_raises(self):
        with pytest.raises(ValidationError):
            SalaryRow(本給=0, 能力給=0, 職務役割給=0, 役割業績給=0)


class TestAllocationRow:
    def test_valid_row(self):
        row = AllocationRow(事業部='50', 地区='10', 課コード='5020', 原価区分='A', 工程='200', 日数=20.0, 編成=0.2, 固定=0.0)
        assert row.編成 == pytest.approx(0.2)
        assert row.工程名 is None

    def test_optional_process_name(self):
        row = AllocationRow(事業部='50', 地区='10', 課コード='5020', 原価区分='A', 工程='200', 日数=20.0, 工程名='工程名テスト', 編成=0.2, 固定=0.0)
        assert row.工程名 == '工程名テスト'

    def test_empty_code_raises(self):
        with pytest.raises(ValidationError):
            AllocationRow(事業部='', 地区='10', 課コード='5020', 原価区分='A', 工程='200', 日数=20.0, 編成=0.2, 固定=0.0)

    def test_invalid_numeric_raises(self):
        with pytest.raises(ValidationError):
            AllocationRow(事業部='50', 地区='10', 課コード='5020', 原価区分='A', 工程='200', 日数='abc', 編成=0.2, 固定=0.0)


class TestLaborTransferRow:
    def test_valid_row(self):
        row = LaborTransferRow(勘定科目コード='9103030000', 担当課='3300', 作業時間=100.0)
        assert row.作業時間 == pytest.approx(100.0)
        assert row.原価センタ is None
        assert row.負担課 is None

    def test_optional_fields(self):
        row = LaborTransferRow(勘定科目コード='9101010000', 負担課='5020', 担当課='3300', 工事名='大津改修工事', 作業時間=30.0, WBS='12411503920910')
        assert row.工事名 == '大津改修工事'
        assert row.WBS == '12411503920910'

    def test_empty_required_code_raises(self):
        with pytest.raises(ValidationError):
            LaborTransferRow(勘定科目コード='', 担当課='3300', 作業時間=100.0)

    def test_invalid_hours_raises(self):
        with pytest.raises(ValidationError):
            LaborTransferRow(勘定科目コード='9103030000', 担当課='3300', 作業時間='invalid')
