"""マスタサンプルデータ投入スクリプト

地区マスタ・勘定科目マスタ・原価センタマスタにテスト用サンプルデータを
挿入します。既存のレコードはスキップされます。

使い方:
    uv run python scripts/seed_masters.py
    uv run python scripts/seed_masters.py --clear   # 既存データを削除してから投入
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app.extensions import db
from app.models.district import DistrictMaster
from app.models.account import AccountMaster
from app.models.cost_center import CostCenterMaster
from app.models.section import SectionMaster
from app.models.department import DepartmentMaster

# ---------------------------------------------------------------------------
# サンプルデータ定義
# ---------------------------------------------------------------------------

DISTRICTS = [
    ('01', '東京'),
    ('02', '大阪'),
    ('03', '名古屋'),
    ('04', '福岡'),
    ('05', '札幌'),
]

ACCOUNTS = [
    ('4101', '基本給'),
    ('4102', '能力給'),
    ('4103', '職務役割給'),
    ('4104', '役割業績給'),
    ('4201', '家族手当'),
    ('4202', '資格手当'),
    ('4203', '交替勤務手当'),
    ('4301', '法定福利費'),
    ('4302', '福利厚生費'),
    ('4401', '退職給付費用'),
]

COST_CENTERS = [
    ('CC0101', '東京製造部'),
    ('CC0102', '東京営業部'),
    ('CC0103', '東京管理部'),
    ('CC0201', '大阪製造部'),
    ('CC0202', '大阪営業部'),
    ('CC0301', '名古屋製造部'),
    ('CC0401', '福岡製造部'),
    ('CC0501', '札幌営業部'),
]

# (section_code, section_name, district_code, cost_center_code)
SECTIONS = [
    ('S0101', '東京製造一課', '01', 'CC0101'),
    ('S0102', '東京製造二課', '01', 'CC0101'),
    ('S0103', '東京営業課',   '01', 'CC0102'),
    ('S0104', '東京管理課',   '01', 'CC0103'),
    ('S0201', '大阪製造課',   '02', 'CC0201'),
    ('S0202', '大阪営業課',   '02', 'CC0202'),
    ('S0301', '名古屋製造課', '03', 'CC0301'),
    ('S0401', '福岡製造課',   '04', 'CC0401'),
    ('S0501', '札幌営業課',   '05', 'CC0501'),
]

# (department_code, department_name, district_code, section_code, account_code, cost_center_code)
DEPARTMENTS = [
    ('D010101', '東京製造一課・基本給',   '01', 'S0101', '4101', 'CC0101'),
    ('D010102', '東京製造一課・能力給',   '01', 'S0101', '4102', 'CC0101'),
    ('D010201', '東京製造二課・基本給',   '01', 'S0102', '4101', 'CC0101'),
    ('D010301', '東京営業課・基本給',     '01', 'S0103', '4101', 'CC0102'),
    ('D010401', '東京管理課・基本給',     '01', 'S0104', '4101', 'CC0103'),
    ('D020101', '大阪製造課・基本給',     '02', 'S0201', '4101', 'CC0201'),
    ('D020201', '大阪営業課・基本給',     '02', 'S0202', '4101', 'CC0202'),
    ('D030101', '名古屋製造課・基本給',   '03', 'S0301', '4101', 'CC0301'),
    ('D040101', '福岡製造課・基本給',     '04', 'S0401', '4101', 'CC0401'),
    ('D050101', '札幌営業課・基本給',     '05', 'S0501', '4101', 'CC0501'),
]


# ---------------------------------------------------------------------------

def seed(clear: bool) -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        if clear:
            db.session.query(DepartmentMaster).delete()
            db.session.query(SectionMaster).delete()
            db.session.query(DistrictMaster).delete()
            db.session.query(AccountMaster).delete()
            db.session.query(CostCenterMaster).delete()
            db.session.commit()
            print('[INFO] 既存データを削除しました。')

        added = {'district': 0, 'account': 0, 'cost_center': 0, 'section': 0, 'department': 0}

        for code, name in DISTRICTS:
            if not db.session.get(DistrictMaster, code):
                db.session.add(DistrictMaster(district_code=code, district_name=name))
                added['district'] += 1

        for code, name in ACCOUNTS:
            if not db.session.get(AccountMaster, code):
                db.session.add(AccountMaster(account_code=code, account_name=name))
                added['account'] += 1

        for code, name in COST_CENTERS:
            if not db.session.get(CostCenterMaster, code):
                db.session.add(CostCenterMaster(cost_center_code=code, cost_center_name=name))
                added['cost_center'] += 1

        for code, name, district, cost_center in SECTIONS:
            if not db.session.get(SectionMaster, code):
                db.session.add(SectionMaster(
                    section_code=code,
                    section_name=name,
                    district_code=district,
                    cost_center_code=cost_center,
                ))
                added['section'] += 1

        for code, name, district, section, account, cost_center in DEPARTMENTS:
            if not db.session.get(DepartmentMaster, code):
                db.session.add(DepartmentMaster(
                    department_code=code,
                    department_name=name,
                    district_code=district,
                    section_code=section,
                    account_code=account,
                    cost_center_code=cost_center,
                ))
                added['department'] += 1

        db.session.commit()

        print(f'[OK] 地区マスタ        : {added["district"]} 件追加')
        print(f'[OK] 勘定科目マスタ    : {added["account"]} 件追加')
        print(f'[OK] 原価センタマスタ  : {added["cost_center"]} 件追加')
        print(f'[OK] 課マスタ          : {added["section"]} 件追加')
        print(f'[OK] 部署マスタ        : {added["department"]} 件追加')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='マスタサンプルデータを投入します。')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='投入前に既存データを全削除する',
    )
    args = parser.parse_args()
    seed(clear=args.clear)
