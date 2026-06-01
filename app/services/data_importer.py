"""Data importer service.

Orchestrates: validate rows → save to DB → return result summary.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError
from flask_login import current_user

from ..extensions import db
from ..services.excel_reader import read_excel
from ..validators.salary import SalaryRow
from ..validators.allocation import AllocationRow
from ..validators.labor_transfer import LaborTransferRow
from ..validators.ouen import OuenRow
from ..models.upload_batch import UploadBatch
from ..models.salary import SalaryData
from ..models.allocation import AllocationData
from ..models.labor_transfer import LaborTransferData
from ..models.ouen import OuenData


@dataclass
class ImportResult:
    success: bool
    saved_count: int = 0
    errors: list[dict] = field(default_factory=list)
    batch_id: int | None = None


def _validate_rows(rows: list[dict], file_type: str) -> tuple[list[Any], list[dict]]:
    """Validate all rows. Returns (valid_models, error_list)."""
    validator_map = {
        'salary': SalaryRow,
        'allocation': AllocationRow,
        'labor_transfer': LaborTransferRow,
        'ouen': OuenRow,
    }
    validator_cls = validator_map[file_type]
    valid_models: list[Any] = []
    errors: list[dict] = []

    for row in rows:
        row_num = row.pop('_row', '?')
        try:
            model = validator_cls.model_validate(row)
            valid_models.append(model)
        except ValidationError as exc:
            for err in exc.errors():
                errors.append({
                    'row': row_num,
                    'field': ' / '.join(str(loc) for loc in err['loc']),
                    'message': err['msg'],
                })

    return valid_models, errors


def _build_db_record(model: Any, file_type: str, batch_id: int, user_id: int) -> Any:
    common = {'batch_id': batch_id, 'created_by': user_id}
    if file_type == 'salary':
        return SalaryData(
            row_label=model.行ラベル,
            chiku=model.地区,
            ka_code=model.課コード,
            chiku_ka_code=model.地区課コード,
            shuuyaku_ka_code=model.集約課コード,
            chiku_shuuyaku_ka_code=model.地区集約課コード,
            cost_center=model.原価センタ,
            kubun=model.区分,
            account_subject=model.勘定科目,
            section_name=model.所属名,
            honkyu=model.本給,
            nouryoku_kyu=model.能力給,
            shokumu_yakuwari_kyu=model.職務役割給,
            yakuwari_gyoseki_kyu=model.役割業績給,
            hoshu=model.報酬,
            honpo=model.本俸,
            kihon_chingin=model.基本賃金,
            kokunai_kyuyo=model.国内給与,
            chuzaiin_kyuyo_chosei=model.駐在員給与調整,
            kazoku_teate=model.家族手当,
            shikaku_teate=model.資格手当,
            koutai_kinmu_kazan_kyu=model.交替勤務加算給,
            furikae_kinmu_shugyo_teate=model.振替勤務就業手当,
            hayade_zangyou_teate=model.早出残業手当,
            kyujitsu_shukkin_teate=model.休日出勤手当,
            tokutei_kyujitsu_shukkin_teate=model.特定休日出勤手当,
            koutai_kinmu_teate=model.交替勤務手当,
            keibi_teate=model.守衛手当,
            shinya_teate=model.深夜業手当,
            tanshin_funin_teate=model.単身赴任手当,
            ichiji_kisei_ryohi=model.一時帰省旅費,
            yakan_yobidate_teate=model.夜間呼出手当,
            shukkou_hoshou_jikan=model.出向補償時間,
            sonota_teate=model.その他手当,
            zengetsu_ikukai_kingaku=model.前月育介金額,
            kouteki_shikaku_teate=model.公的資格手当,
            chingin_koujyo=model.賃金控除,
            shokuba_ridatsu_kaikei=model.職場離脱会計,
            jinkenhi_ninzuu_kaikei=model.人件費人数会計,
            total=model.合計,
            **common,
        )
    elif file_type == 'allocation':
        return AllocationData(
            division_code=model.事業部,
            district_code=model.地区,
            section_code=model.課コード,
            cost_category=model.原価区分,
            process_code=model.工程,
            days=model.日数,
            process_name=model.工程名,
            formation=model.編成,
            fixed_count=model.固定,
            **common,
        )
    elif file_type == 'labor_transfer':
        return LaborTransferData(
            account_code=model.勘定科目コード,
            cost_center=model.原価センタ,
            burden_section=model.負担課,
            charge_section=model.担当課,
            construction_name=model.工事名,
            work_hours=model.作業時間,
            wbs=model.WBS,
            asset_number=model.資産集約番号,
            order_number=model.指図,
            note=model.備考,
            **common,
        )
    elif file_type == 'ouen':
        return OuenData(
            from_district=model.送り出し地区,
            from_section_code=model.送り出し課コード,
            to_district=model.受け入れ地区,
            to_section_code=model.受け入れ課コード,
            departure_date=model.出課日,
            return_date=model.帰課日,
            days=model.日数,
            extended_days=model.延日数,
            note=model.備考,
            **common,
        )
    raise ValueError(f'未定義のファイル種別: {file_type}')


def import_excel_file(file_storage, file_type: str, user_id: int) -> ImportResult:
    """Process an uploaded FileStorage object.

    Saves to a temp file, reads, validates, persists to DB, then deletes the temp file.
    """
    suffix = os.path.splitext(file_storage.filename)[1]
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            file_storage.save(tmp_path)

        rows = read_excel(tmp_path, file_type)
        if not rows:
            return ImportResult(success=False, errors=[{'row': '-', 'field': '-', 'message': 'データが見つかりませんでした。'}])

        valid_models, errors = _validate_rows(rows, file_type)
        if errors:
            return ImportResult(success=False, errors=errors)

        # Persist
        batch = UploadBatch(
            file_name=file_storage.filename,
            file_type=file_type,
            created_by=user_id,
        )
        db.session.add(batch)
        db.session.flush()  # get batch.id

        records = [_build_db_record(m, file_type, batch.id, user_id) for m in valid_models]
        db.session.bulk_save_objects(records)
        batch.record_count = len(records)
        db.session.commit()

        return ImportResult(success=True, saved_count=len(records), batch_id=batch.id)

    except Exception as exc:
        db.session.rollback()
        return ImportResult(success=False, errors=[{'row': '-', 'field': '-', 'message': str(exc)}])
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)



