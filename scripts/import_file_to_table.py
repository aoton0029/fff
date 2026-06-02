"""ファイルからテーブルへのデータインポートスクリプト

CSVまたはExcelファイルを読み込み、指定したデータベーステーブルにinsertします。

使い方:
    uv run python scripts/import_file_to_table.py <ファイルパス> <テーブル名> [オプション]

例:
    uv run python scripts/import_file_to_table.py data.csv my_table
    uv run python scripts/import_file_to_table.py data.xlsx my_table --if-exists replace
    uv run python scripts/import_file_to_table.py data.csv my_table --if-exists append
    uv run python scripts/import_file_to_table.py data.xlsx my_table --sheet Sheet2 --chunksize 500
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app.extensions import db


def read_file(file_path: Path) -> pd.DataFrame:
    """CSVまたはExcelファイルをDataFrameとして読み込む。

    Args:
        file_path: 読み込むファイルのパス。
        sheet_name: Excelの場合のシート名またはインデックス（省略時は最初のシート）。

    Returns:
        読み込んだDataFrame。
    """
    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(file_path)
    elif suffix in (".xlsx", ".xls", ".xlsm"):
        # header=0: 1行目をヘッダ列として扱う（デフォルト）
        return pd.read_excel(file_path, header=0)
    else:
        raise ValueError(f"未対応のファイル形式です: {suffix}  (csv / xlsx / xls / xlsm のみ対応)")


def import_to_table(
    file_path: str | Path,
    table_name: str,
    if_exists: str = "append",
    chunksize: int = 1000,
    index: bool = False,
) -> int:
    """ファイルを読み込み、指定テーブルにデータを挿入する。

    Args:
        file_path: 読み込むCSV / Excelファイルのパス。
        table_name: 挿入先のテーブル名。
        if_exists: テーブルが既に存在する場合の挙動。
            - 'fail'    : エラーを発生させる（デフォルト動作ではない）
            - 'replace' : テーブルを削除して再作成する
            - 'append'  : 既存テーブルに追記する（デフォルト）
        chunksize: 一度にinsertする行数。
        index: DataFrameのインデックスをカラムとして書き込むか否か。

    Returns:
        挿入した行数。
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

    df = read_file(file_path)

    app = create_app()
    with app.app_context():
        engine = db.engine
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=index,
            chunksize=chunksize,
            method="multi",
        )

    return len(df)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CSV / Excel ファイルをデータベーステーブルにインポートします。"
    )
    parser.add_argument("file", help="読み込むファイルのパス（CSV または Excel）")
    parser.add_argument("table", help="挿入先のテーブル名")
    parser.add_argument(
        "--if-exists",
        choices=["fail", "replace", "append"],
        default="append",
        help="テーブルが既に存在する場合の挙動（デフォルト: append）",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=1000,
        help="一度にinsertする行数（デフォルト: 1000）",
    )
    parser.add_argument(
        "--index",
        action="store_true",
        help="DataFrameのインデックスをカラムとして書き込む",
    )

    args = parser.parse_args()

    try:
        count = import_to_table(
            file_path=args.file,
            table_name=args.table,
            if_exists=args.if_exists,
            chunksize=args.chunksize,
            index=args.index,
        )
        print(f"完了: {count} 行を '{args.table}' テーブルにインポートしました。")
    except (FileNotFoundError, ValueError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
