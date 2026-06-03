"""app.dbの初期化・シードスクリプト（開発・テスト用）

使い方:
    uv run python scripts/init_app_db.py
    uv run python scripts/init_app_db.py --clear   # 既存データを削除してから投入
"""
import argparse
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
from app.models.mst_user import User

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

WBS_LIST = [
    ('WBS001', 'プロジェクトA'),
    ('WBS002', 'プロジェクトB'),
    ('WBS003', '間接費'),
]

KBN_LIST = [
    ('K01', '正社員'),
    ('K02', '嘱託社員'),
    ('K03', 'パート・アルバイト'),
]

# filetype_code は api/*.py の _FILE_TYPE 定数と一致させること
FILE_TYPES = [
    ('salary',         '給与データ'),
    ('allocation',     '工程配賦データ'),
    ('labor_transfer', '労務費振替データ'),
    ('ouen',           '応援連絡票'),
]

# (section_code, section_name, district_code, cost_center_code)
SECTIONS = [
    ('S0101', '東京製造課',   '01', 'CC0101'),
    ('S0102', '東京営業課',   '01', 'CC0102'),
    ('S0103', '東京管理課',   '01', 'CC0103'),
    ('S0201', '大阪製造課',   '02', 'CC0201'),
    ('S0202', '大阪営業課',   '02', 'CC0202'),
    ('S0301', '名古屋製造課', '03', 'CC0301'),
    ('S0401', '福岡製造課',   '04', 'CC0401'),
    ('S0501', '札幌営業課',   '05', 'CC0501'),
]

# (department_code, department_name, district_code,
#  section_code, agg_section_code, kbn_code, account_code, cost_center_code)
DEPARTMENTS = [
    ('01010101', '東京製造課・正社員・基本給',    '01', 'S0101', 'S0101', 'K01', '4101', 'CC0101'),
    ('01010102', '東京製造課・正社員・能力給',    '01', 'S0101', 'S0101', 'K01', '4102', 'CC0101'),
    ('01010201', '東京製造課・嘱託社員・基本給',  '01', 'S0101', 'S0101', 'K02', '4101', 'CC0101'),
    ('01020101', '東京営業課・正社員・基本給',    '01', 'S0102', 'S0102', 'K01', '4101', 'CC0102'),
    ('02010101', '大阪製造課・正社員・基本給',    '02', 'S0201', 'S0201', 'K01', '4101', 'CC0201'),
    ('02010102', '大阪製造課・正社員・能力給',    '02', 'S0201', 'S0201', 'K01', '4102', 'CC0201'),
    ('03010101', '名古屋製造課・正社員・基本給',  '03', 'S0301', 'S0301', 'K01', '4101', 'CC0301'),
    ('04010101', '福岡製造課・正社員・基本給',    '04', 'S0401', 'S0401', 'K01', '4101', 'CC0401'),
    ('05010101', '札幌営業課・正社員・基本給',    '05', 'S0501', 'S0501', 'K01', '4101', 'CC0501'),
]

# ---------------------------------------------------------------------------


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

        for code, name in WBS_LIST:
            if not db.session.get(WBSMaster, code):
                db.session.add(WBSMaster(wbs_code=code, wbs_name=name))
                added['wbs'] += 1

        for code, name in KBN_LIST:
            if not db.session.get(KbnMaster, code):
                db.session.add(KbnMaster(kbn_code=code, kbn_name=name))
                added['kbn'] += 1

        for code, name in FILE_TYPES:
            if not db.session.get(FileTypeMaster, code):
                db.session.add(FileTypeMaster(filetype_code=code, filetype_name=name))
                added['filetype'] += 1

        db.session.flush()  # District/CostCenter が確定してから Section を挿入

        for code, name, district, cost_center in SECTIONS:
            if not db.session.get(SectionMaster, code):
                db.session.add(SectionMaster(
                    section_code=code,
                    section_name=name,
                    district_code=district,
                    cost_center_code=cost_center,
                ))
                added['section'] += 1

        db.session.flush()  # Section が確定してから Department を挿入

        for code, name, district, section, agg_section, kbn, account, cost_center in DEPARTMENTS:
            if not db.session.get(DepartmentMaster, code):
                db.session.add(DepartmentMaster(
                    department_code=code,
                    department_name=name,
                    district_code=district,
                    section_code=section,
                    agg_section_code=agg_section,
                    kbn_code=kbn,
                    account_code=account,
                    cost_center_code=cost_center,
                ))
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
