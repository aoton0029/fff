"""アプリDBマスタのサンプルデータ投入スクリプト

課マスタ・変換マスタにテスト用サンプルデータを挿入します。
地区・勘定科目・原価センタ・WBS・ユーザーは別DBサーバー管理のため、
init_app_db.py で app.db に投入してください。

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
from app.models.mst_section import SectionMaster
from app.models.mst_department import DepartmentMaster

# ---------------------------------------------------------------------------
# サンプルデータ定義
# ---------------------------------------------------------------------------

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
    ('D010101', '東京製造一課・基本給',   '01', 'S0101', 'S0101', '4101', 'CC0101'),
    ('D010102', '東京製造一課・能力給',   '01', 'S0101', 'S0101', '4102', 'CC0101'),
    ('D010201', '東京製造二課・基本給',   '01', 'S0102', 'S0102', '4101', 'CC0101'),
    ('D010301', '東京営業課・基本給',     '01', 'S0103', 'S0103', '4101', 'CC0102'),
    ('D010401', '東京管理課・基本給',     '01', 'S0104', 'S0104', '4101', 'CC0103'),
    ('D020101', '大阪製造課・基本給',     '02', 'S0201', 'S0201', '4101', 'CC0201'),
    ('D020201', '大阪営業課・基本給',     '02', 'S0202', 'S0202', '4101', 'CC0202'),
    ('D030101', '名古屋製造課・基本給',   '03', 'S0301', 'S0301', '4101', 'CC0301'),
    ('D040101', '福岡製造課・基本給',     '04', 'S0401', 'S0401', '4101', 'CC0401'),
    ('D050101', '札幌営業課・基本給',     '05', 'S0501', 'S0501', '4101', 'CC0501'),
]


# ---------------------------------------------------------------------------

def seed(clear: bool) -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        if clear:
            db.session.query(DepartmentMaster).delete()
            db.session.query(SectionMaster).delete()
            db.session.commit()
            print('[INFO] 既存データを削除しました。')

        added = {'section': 0, 'department': 0}

        for code, name, district, cost_center in SECTIONS:
            if not db.session.get(SectionMaster, code):
                db.session.add(SectionMaster(
                    section_code=code,
                    section_name=name,
                    district_code=district,
                    cost_center_code=cost_center,
                ))
                added['section'] += 1

        for code, name, district, section, agg_section, account, cost_center in DEPARTMENTS:
            if not db.session.get(DepartmentMaster, code):
                db.session.add(DepartmentMaster(
                    department_code=code,
                    department_name=name,
                    district_code=district,
                    section_code=section,
                    agg_section_code=agg_section,
                    kbn_code='',
                    account_code=account,
                    cost_center_code=cost_center,
                ))
                added['department'] += 1

        db.session.commit()

        print(f'[OK] 課マスタ    : {added["section"]} 件追加')
        print(f'[OK] 変換マスタ  : {added["department"]} 件追加')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='アプリDBマスタのサンプルデータを投入します。')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='投入前に既存データを全削除する',
    )
    args = parser.parse_args()
    seed(clear=args.clear)
