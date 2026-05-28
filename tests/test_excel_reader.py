"""Tests for the Excel reader service."""
import os
import tempfile
import pytest
import openpyxl

from app.services.excel_reader import read_excel, get_format_config


def _make_salary_xlsx() -> str:
    """Create a minimal salary Excel file and return its path."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '給与データ'
    # Header row (row 1)
    ws.append(['部署コード', '本給', '能力給', '報酬', '手当', '人員数', '給与額'])
    # Data rows
    ws.append(['00000100', 300000, 50000, 20000, 30000, 10, 4000000])
    ws.append(['00000200', 250000, 40000, 15000, 25000, 5, 1625000])

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    wb.save(tmp.name)
    tmp.close()
    return tmp.name


def _make_allocation_xlsx() -> str:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '配賦データ'
    # header_row=2 means header is at row 2; row 1 is ignored
    ws.append(['(ignored row 1)'])
    ws.append(['地区コード', '課コード', '按分人員数'])
    ws.append(['10', '1111', 0.1])
    ws.append(['10', '2222', 0.2])

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    wb.save(tmp.name)
    tmp.close()
    return tmp.name


class TestGetFormatConfig:
    def test_salary_config_loaded(self):
        cfg = get_format_config('salary')
        assert cfg['sheet_name'] == '給与データ'
        assert len(cfg['columns']) == 7

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError, match='未定義'):
            get_format_config('unknown_type')


class TestReadExcel:
    def test_read_salary(self):
        path = _make_salary_xlsx()
        try:
            rows = read_excel(path, 'salary')
            assert len(rows) == 2
            assert rows[0]['部署コード'] == '00000100'
            assert rows[0]['本給'] == 300000
        finally:
            os.unlink(path)

    def test_read_allocation_with_header_row2(self):
        path = _make_allocation_xlsx()
        try:
            rows = read_excel(path, 'allocation')
            assert len(rows) == 2
            assert rows[0]['地区コード'] == '10'
            assert rows[0]['按分人員数'] == pytest.approx(0.1)
        finally:
            os.unlink(path)

    def test_missing_sheet_raises(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'WrongSheet'
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        wb.save(tmp.name)
        tmp.close()
        try:
            with pytest.raises(ValueError, match='シート'):
                read_excel(tmp.name, 'salary')
        finally:
            os.unlink(tmp.name)
