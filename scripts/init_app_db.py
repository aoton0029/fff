"""app.dbの初期化・シードスクリプト（開発・テスト用）

使い方:
    uv run python scripts/init_app_db.py
    uv run python scripts/init_app_db.py --clear   # 既存データを削除してから投入

CSVファイルは instance/ ディレクトリに配置する:
    instance/mst_district.csv
    instance/mst_account.csv
    instance/mst_cost_center.csv
    instance/mst_wbs.csv
    instance/mst_kbn.csv
    instance/mst_section.csv
    instance/mst_department.csv
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app.extensions import db
from app.models.mst_district import DistrictMaster
from app.models.mst_account import AccountMaster
from app.models.mst_cost_center import CostCenterMaster
from app.models.mst_wbs import WBSMaster
from app.models.mst_kbn import KbnMaster
from app.models.mst_filetype import FileTypeMaster
from app.models.mst_section import SectionMaster
from app.models.mst_department import DepartmentMaster

INSTANCE_DIR = Path(__file__).parent.parent / 'instance'

# filetype_code は api/*.py の _FILE_TYPE 定数と一致させること（CSV管理外）
FILE_TYPES = [
    ('salary',         '給与データ'),
    ('allocation',     '工程配賦データ'),
    ('labor_transfer', '労務費振替データ'),
    ('ouen',           '応援連絡票'),
]


def read_csv(filename: str) -> list[dict]:
    path = INSTANCE_DIR / filename
    if not path.exists():
        print(f'[WARN] {path} が見つかりません。スキップします。')
        return []
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def init(clear: bool) -> None:
    app = create_app('development')
    with app.app_context():
        db.create_all()

        if clear:
            db.session.query(DepartmentMaster).delete()
            db.session.query(SectionMaster).delete()
            db.session.query(FileTypeMaster).delete()
            db.session.query(KbnMaster).delete()
            db.session.query(WBSMaster).delete()
            db.session.query(CostCenterMaster).delete()
            db.session.query(AccountMaster).delete()
            db.session.query(DistrictMaster).delete()
            db.session.commit()
            print('[INFO] 既存データを削除しました。')

        added = {'district': 0, 'account': 0, 'cost_center': 0, 'wbs': 0,
                 'kbn': 0, 'filetype': 0, 'section': 0, 'department': 0}

        for row in read_csv('mst_district.csv'):
            if not db.session.get(DistrictMaster, row['district_code']):
                db.session.add(DistrictMaster(**row))
                added['district'] += 1

        for row in read_csv('mst_account.csv'):
            if not db.session.get(AccountMaster, row['account_code']):
                db.session.add(AccountMaster(**row))
                added['account'] += 1

        for row in read_csv('mst_cost_center.csv'):
            if not db.session.get(CostCenterMaster, row['cost_center_code']):
                db.session.add(CostCenterMaster(**row))
                added['cost_center'] += 1

        for row in read_csv('mst_wbs.csv'):
            if not db.session.get(WBSMaster, row['wbs_code']):
                db.session.add(WBSMaster(**row))
                added['wbs'] += 1

        for row in read_csv('mst_kbn.csv'):
            if not db.session.get(KbnMaster, row['kbn_code']):
                db.session.add(KbnMaster(**row))
                added['kbn'] += 1

        for code, name in FILE_TYPES:
            if not db.session.get(FileTypeMaster, code):
                db.session.add(FileTypeMaster(filetype_code=code, filetype_name=name))
                added['filetype'] += 1

        db.session.flush()  # District/CostCenter が確定してから Section を挿入

        for row in read_csv('mst_section.csv'):
            if not db.session.get(SectionMaster, row['section_code']):
                db.session.add(SectionMaster(**row))
                added['section'] += 1

        db.session.flush()  # Section が確定してから Department を挿入

        for row in read_csv('mst_department.csv'):
            if not db.session.get(DepartmentMaster, row['department_code']):
                db.session.add(DepartmentMaster(**row))
                added['department'] += 1

        db.session.commit()

        print(f'[OK] 地区マスタ            : {added["district"]} 件追加')
        print(f'[OK] 勘定科目マスタ        : {added["account"]} 件追加')
        print(f'[OK] 原価センタマスタ      : {added["cost_center"]} 件追加')
        print(f'[OK] WBSマスタ             : {added["wbs"]} 件追加')
        print(f'[OK] 区分マスタ            : {added["kbn"]} 件追加')
        print(f'[OK] ファイルタイプマスタ  : {added["filetype"]} 件追加')
        print(f'[OK] 課マスタ              : {added["section"]} 件追加')
        print(f'[OK] 変換マスタ            : {added["department"]} 件追加')
        print('[INFO] ユーザーは create_admin.py で作成してください。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='マスタ用SQLiteを初期化・シードします。')
    parser.add_argument(
        '--clear',
        action='store_true',
        help='投入前に既存データを全削除する',
    )
    args = parser.parse_args()
    init(clear=args.clear)
