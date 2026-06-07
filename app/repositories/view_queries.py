from sqlalchemy import text

# V_人事給与データ: 課単位の給与集計・応援単価計算
SALARY_SQL = text("""
SELECT
    地区
    , 課コード
    , MAX(集約課コード) AS 集約課コード
    , MAX(原価センタ) AS 原価センタ
    , MAX(区分) AS 区分
    , MAX(勘定科目) AS 勘定科目
    , SUM([合計])/SUM([合計_明細2_人件費人数会計])/:days_of_month AS 応援単価
    , SUM(合計) AS 合計
    , SUM([合計_明細2_人件費人数会計]) AS 人員数
FROM dat_人事給与データ
GROUP BY 地区, 課コード
""")

# V_応援連絡票: 応援延日数・応援金額の計算
OUEN_RENRAKUHYO_SQL = text("""
SELECT
    送り出し_地区
    , 送り出し_課コード
    , 受け入れ_地区
    , 受け入れ_課コード
    , 延日数
    , 応援単価
    , ROUND(CAST(延日数 AS REAL) / :days_of_month, 1) AS 応援人員
    , 応援単価 * 延日数 AS 応援金額
FROM dat_応援連絡票 AS T
LEFT JOIN (
    SELECT
        地区コード
        , 課コード
        , SUM(合計_明細1_本給 + 合計_明細1_能力給 + 合計_明細1_職務役割給)/SUM([合計_明細2_人件費人数会計]) / :days_of_month AS 応援単価
        , SUM(合計_明細1_本給 + 合計_明細1_能力給 + 合計_明細1_職務役割給) AS 合計
    FROM dat_人事給与データ AS A
	LEFT JOIN mst_変換マスタ AS B
	ON A.行ラベル = B.行ラベル
    GROUP BY 地区コード, 課コード
) AS J
ON J.地区コード = T.送り出し_地区
AND J.課コード = T.送り出し_課コード
""")

# V_応援計算データ: V_人事給与データ・V_応援連絡票 をCTEに展開
OUEN_KEISAN_SQL = text("""
WITH V_人事給与データ AS (
    SELECT
        地区
        , 課コード
        , MAX(集約課コード) AS 集約課コード
        , MAX(原価センタ) AS 原価センタ
        , MAX(区分) AS 区分
        , MAX(勘定科目) AS 勘定科目
        , SUM([合計])/SUM([合計_明細2_人件費人数会計])/:days_of_month AS 応援単価
        , SUM(合計) AS 合計
        , SUM([合計_明細2_人件費人数会計]) AS 人員数
    FROM dat_人事給与データ
    GROUP BY 地区, 課コード
),
V_応援連絡票 AS (
    SELECT
        送り出し_地区
        , 送り出し_課コード
        , 受け入れ_地区
        , 受け入れ_課コード
        , 延日数
        , 応援単価
        , ROUND(CAST(延日数 AS REAL) / :days_of_month, 1) AS 応援人員
        , 応援単価 * 延日数 AS 応援金額
    FROM dat_応援連絡票 AS T
    LEFT JOIN (
        SELECT
            地区コード
            , 課コード
            , SUM(合計_明細1_本給 + 合計_明細1_能力給 + 合計_明細1_職務役割給)/SUM([合計_明細2_人件費人数会計]) / :days_of_month AS 応援単価
            , SUM(合計_明細1_本給 + 合計_明細1_能力給 + 合計_明細1_職務役割給) AS 合計
        FROM dat_人事給与データ AS A
        LEFT JOIN mst_変換マスタ AS B
        ON A.行ラベル = B.行ラベル
        GROUP BY 地区コード, 課コード
    ) AS J
    ON J.地区コード = T.送り出し_地区
    AND J.課コード = T.送り出し_課コード
)
SELECT
    T.地区
    , T.課コード
    , T.区分
    , C1.課コード名 AS 課コード名
    , T.応援単価
    , T.集約課コード
    , IFNULL(OKURI.送出金額, 0) AS 送出金額
    , IFNULL(OKURI.送出人員数, 0) AS 送出人員数
    , IFNULL(UKEIRE.受入金額, 0) AS 受入金額
    , IFNULL(UKEIRE.受入人員数, 0) AS 受入人員数
    , IFNULL(T.合計, 0) + IFNULL(OKURI.送出金額, 0) + IFNULL(UKEIRE.受入金額, 0) AS 応援後人件費
    , IFNULL(T.人員数, 0) + IFNULL(OKURI.送出人員数, 0) + IFNULL(UKEIRE.受入人員数, 0) AS 応援後人員数
FROM V_人事給与データ AS T
LEFT JOIN (
    SELECT
        送り出し_地区
        , 送り出し_課コード
        , -SUM(応援金額) AS 送出金額
        , -SUM(応援人員) AS 送出人員数
    FROM V_応援連絡票
    GROUP BY 送り出し_地区, 送り出し_課コード
) AS OKURI
ON T.地区 = OKURI.送り出し_地区
AND T.課コード = OKURI.送り出し_課コード
LEFT JOIN (
    SELECT
        受け入れ_地区
        , 受け入れ_課コード
        , SUM(応援金額) AS 受入金額
        , SUM(応援人員) AS 受入人員数
    FROM V_応援連絡票
    GROUP BY 受け入れ_地区, 受け入れ_課コード
) AS UKEIRE
ON T.地区 = UKEIRE.受け入れ_地区
AND T.課コード = UKEIRE.受け入れ_課コード
LEFT JOIN mst_課コード AS C1
ON T.課コード = C1.課コード
""")

# V_工程配賦: V_応援計算データ（および依存ビュー）をCTEに展開
KOUTEI_HAIFU_SQL = text("""
WITH V_人事給与データ AS (
    SELECT
        地区
        , 課コード
        , MAX(集約課コード) AS 集約課コード
        , MAX(原価センタ) AS 原価センタ
        , MAX(区分) AS 区分
        , MAX(勘定科目) AS 勘定科目
        , SUM([合計])/SUM([合計_明細2_人件費人数会計])/:days_of_month AS 応援単価
        , SUM(合計) AS 合計
        , SUM([合計_明細2_人件費人数会計]) AS 人員数
    FROM dat_人事給与データ
    GROUP BY 地区, 課コード
),
V_応援連絡票 AS (
    SELECT
        送り出し_地区
        , 送り出し_課コード
        , 受け入れ_地区
        , 受け入れ_課コード
        , 延日数
        , 応援単価
        , ROUND(CAST(延日数 AS REAL) / :days_of_month, 1) AS 応援人員
        , 応援単価 * 延日数 AS 応援金額
    FROM dat_応援連絡票 AS T
    LEFT JOIN (
        SELECT
            地区コード
            , 課コード
            , SUM(合計_明細1_本給 + 合計_明細1_能力給 + 合計_明細1_職務役割給)/SUM([合計_明細2_人件費人数会計]) / :days_of_month AS 応援単価
            , SUM(合計_明細1_本給 + 合計_明細1_能力給 + 合計_明細1_職務役割給) AS 合計
        FROM dat_人事給与データ AS A
        LEFT JOIN mst_変換マスタ AS B
        ON A.行ラベル = B.行ラベル
        GROUP BY 地区コード, 課コード
    ) AS J
    ON J.地区コード = T.送り出し_地区
    AND J.課コード = T.送り出し_課コード
),
V_応援計算データ AS (
    SELECT
        T.地区
        , T.課コード
        , T.区分
        , T.応援単価
        , T.集約課コード
        , IFNULL(OKURI.送出金額, 0) AS 送出金額
        , IFNULL(OKURI.送出人員数, 0) AS 送出人員数
        , IFNULL(UKEIRE.受入金額, 0) AS 受入金額
        , IFNULL(UKEIRE.受入人員数, 0) AS 受入人員数
        , IFNULL(T.合計, 0) + IFNULL(OKURI.送出金額, 0) + IFNULL(UKEIRE.受入金額, 0) AS 応援後人件費
        , IFNULL(T.人員数, 0) + IFNULL(OKURI.送出人員数, 0) + IFNULL(UKEIRE.受入人員数, 0) AS 応援後人員数
    FROM V_人事給与データ AS T
    LEFT JOIN (
        SELECT
            送り出し_地区
            , 送り出し_課コード
            , -SUM(応援金額) AS 送出金額
            , -SUM(応援人員) AS 送出人員数
        FROM V_応援連絡票
        GROUP BY 送り出し_地区, 送り出し_課コード
    ) AS OKURI
    ON T.地区 = OKURI.送り出し_地区
    AND T.課コード = OKURI.送り出し_課コード
    LEFT JOIN (
        SELECT
            受け入れ_地区
            , 受け入れ_課コード
            , SUM(応援金額) AS 受入金額
            , SUM(応援人員) AS 受入人員数
        FROM V_応援連絡票
        GROUP BY 受け入れ_地区, 受け入れ_課コード
    ) AS UKEIRE
    ON T.地区 = UKEIRE.受け入れ_地区
    AND T.課コード = UKEIRE.受け入れ_課コード
)
SELECT
    KOUTEI.地区
    , KOUTEI.課コード
    , KOUTEI.工程コード
    , KOUTEI.原価センタ
    , KOUTEI.編成
    , KOUTEI.固定
    , KOUTEI.人員計
    , KOUTEI.人員比
    , ROUND(OUEN.応援後人件費 * KOUTEI.人員比, 0) AS 工程配賦
    , 0 AS 端数調整
    , ROUND(OUEN.応援後人件費 * KOUTEI.人員比, 0) AS 工程配賦計
FROM (
    SELECT
        *
        , T.[人員計] / SUM(T.[人員計]) OVER (PARTITION BY T.地区コード, T.集約課コード) AS 人員比
    FROM (
        SELECT
            *
            , [編成] + [固定] AS [人員計]
            , H.[地区+集約課コード]
            , H.集約課コード
        FROM dat_工程別人員配賦データ AS T1
        LEFT JOIN SAP原価センタマスタ AS T2
        ON T1.地区コード || SUBSTR('0000' || T1.工程コード, -4) = T2.[地区+工程]
        LEFT JOIN (
            SELECT
                地区
                , 課コード
                , MIN(集約課コード) AS 集約課コード
                , MIN([(明細)（人事）所属コード]) AS [(明細)（人事）所属コード]
                , MIN([地区+集約課コード]) AS [地区+集約課コード]
            FROM 変換マスタ
            GROUP BY 地区, 課コード
        ) AS H
        ON H.地区 = T1.地区コード
        AND H.課コード = T1.課コード
    ) AS T
) AS KOUTEI
LEFT JOIN (
    SELECT
        地区
        , 集約課コード
        , SUM(応援後人件費) AS 応援後人件費
    FROM V_応援計算データ
    GROUP BY 地区, 集約課コード
) AS OUEN
ON KOUTEI.地区コード = OUEN.地区
AND KOUTEI.集約課コード = OUEN.集約課コード
""")

# V_労務費振替依頼書: 振替金額付き労務費データ
ROUMUHI_FURIKAE_SQL = text("""
SELECT
    *
    , ROUND(作業時間 * :unit_price, 0) AS 振替金額
FROM 労務費振替依頼書 AS A
LEFT JOIN 課コード変換 AS B
ON A.[地区+課コード] = B.[地区＋課コード]
""")
