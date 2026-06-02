"""app.db（マスタ用SQLite）の初期化・シードスクリプト（開発・テスト用）

別DBサーバーに存在するマスタテーブル（地区・勘定科目・原価センタ・WBS・ユーザー）を
SQLiteファイル（instance/app.db）に作成してサンプルデータを投入します。

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

# ---------------------------------------------------------------------------


def init(clear: bool) -> None:
    app = create_app('development')
    with app.app_context():
        db.create_all(bind_key='master_db')

        if clear:
            db.session.query(WBSMaster).delete()
            db.session.query(CostCenterMaster).delete()
            db.session.query(AccountMaster).delete()
            db.session.query(DistrictMaster).delete()
            db.session.commit()
            print('[INFO] 既存データを削除しました。')

        added = {'district': 0, 'account': 0, 'cost_center': 0, 'wbs': 0}

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

        db.session.commit()

        print(f'[OK] 地区マスタ        : {added["district"]} 件追加')
        print(f'[OK] 勘定科目マスタ    : {added["account"]} 件追加')
        print(f'[OK] 原価センタマスタ  : {added["cost_center"]} 件追加')
        print(f'[OK] WBSマスタ         : {added["wbs"]} 件追加')
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
