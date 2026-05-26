from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Any

import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Regex for safe SQL identifiers (schema.table notation also allowed)
_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")


def _validate_identifier(name: str) -> str:
    """Raise ValueError if *name* is not a safe SQL identifier."""
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(
            f"Invalid SQL identifier: {name!r}. "
            "Only alphanumeric characters, underscores, and dots are allowed."
        )
    return name


class DbManager:
    """Flask-SQLAlchemy + pandas unified SQL execution layer.

    Provides CRUD operations, view queries, and stored procedure calls,
    all returning results as ``pandas.DataFrame``.

    Usage::

        from app.db import db_manager

        df = db_manager.fetch("SELECT * FROM users WHERE role = :role", {"role": "admin"})
    """

    def __init__(self, db: SQLAlchemy) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Core primitives
    # ------------------------------------------------------------------

    def fetch(self, sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        """Execute a SELECT statement and return results as a :class:`DataFrame`.

        Args:
            sql: Raw SQL string. Use ``:name`` placeholders for parameters.
            params: Dict of bind parameters.

        Returns:
            DataFrame with query results. Empty DataFrame if no rows.
        """
        with self._db.engine.connect() as conn:
            return pd.read_sql(text(sql), conn, params=params or {})

    def execute(self, sql: str, params: dict[str, Any] | None = None) -> int:
        """Execute a DML statement (INSERT / UPDATE / DELETE).

        Runs in its own transaction; commits automatically on success
        and rolls back on any exception.

        Args:
            sql: Raw SQL string. Use ``:name`` placeholders for parameters.
            params: Dict of bind parameters.

        Returns:
            Number of rows affected.
        """
        with self._db.engine.begin() as conn:
            result = conn.execute(text(sql), params or {})
            return result.rowcount

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------

    def insert_df(
        self,
        table: str,
        df: pd.DataFrame,
        if_exists: str = "append",
        index: bool = False,
    ) -> int:
        """Bulk-insert a :class:`DataFrame` into *table*.

        Wraps :meth:`pandas.DataFrame.to_sql` with ``method='multi'``
        for efficient batch inserts.

        .. note::
            Audit columns (``created_at``, ``created_by``, etc.) from
            :class:`~app.models.base.BaseModel` must be added to the
            DataFrame by the caller before invoking this method.

        Args:
            table: Target table name.
            df: DataFrame whose columns match the target table schema.
            if_exists: Behaviour when the table already exists:
                ``"append"`` (default), ``"replace"``, or ``"fail"``.
            index: Whether to write the DataFrame index as a column.

        Returns:
            Number of rows inserted.
        """
        _validate_identifier(table)
        with self._db.engine.begin() as conn:
            df.to_sql(table, conn, if_exists=if_exists, index=index, method="multi")
        return len(df)

    def update(
        self,
        table: str,
        values: dict[str, Any],
        where: str,
        params: dict[str, Any] | None = None,
    ) -> int:
        """Update rows in *table*.

        Args:
            table: Target table name.
            values: Mapping of ``{column: new_value}``.
                Column names are used directly as bind-parameter names,
                so they must not overlap with names used in *where*.
            where: SQL WHERE clause (without the ``WHERE`` keyword).
                Use ``:name`` placeholders; supply values in *params*.
            params: Additional bind parameters referenced in *where*.

        Returns:
            Number of rows affected.

        Example::

            db_manager.update(
                "users",
                values={"role": "admin"},
                where="id = :user_id",
                params={"user_id": 42},
            )
        """
        _validate_identifier(table)
        set_clause = ", ".join(f"{col} = :{col}" for col in values)
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        merged: dict[str, Any] = {**values, **(params or {})}
        return self.execute(sql, merged)

    def delete(
        self,
        table: str,
        where: str,
        params: dict[str, Any] | None = None,
    ) -> int:
        """Delete rows from *table* matching *where*.

        Args:
            table: Target table name.
            where: SQL WHERE clause (without the ``WHERE`` keyword).
                Use ``:name`` placeholders; supply values in *params*.
            params: Bind parameters referenced in *where*.

        Returns:
            Number of rows affected.

        Example::

            db_manager.delete("uploaded_files", "id = :id", {"id": 5})
        """
        _validate_identifier(table)
        sql = f"DELETE FROM {table} WHERE {where}"
        return self.execute(sql, params)

    # ------------------------------------------------------------------
    # View queries
    # ------------------------------------------------------------------

    def fetch_view(
        self,
        view_name: str,
        where: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> pd.DataFrame:
        """Select all columns from a SQL view, with an optional WHERE filter.

        Args:
            view_name: Name of the view (validated against safe-identifier rules).
            where: Optional SQL WHERE clause (without the ``WHERE`` keyword).
            params: Bind parameters for *where*.

        Returns:
            DataFrame with the view's rows.

        Example::

            df = db_manager.fetch_view("v_active_users", "role = :role", {"role": "admin"})
        """
        _validate_identifier(view_name)
        sql = f"SELECT * FROM {view_name}"
        if where:
            sql += f" WHERE {where}"
        return self.fetch(sql, params)

    # ------------------------------------------------------------------
    # Stored procedures
    # ------------------------------------------------------------------

    def call_proc(
        self,
        proc_name: str,
        params: dict[str, Any] | None = None,
    ) -> pd.DataFrame:
        """Execute a stored procedure and return its first result set as a DataFrame.

        Dialect-aware syntax:

        * **mssql**: ``EXEC proc_name @param1 = :param1, @param2 = :param2``
        * **others** (PostgreSQL, MySQL, etc.): ``CALL proc_name(:param1, :param2)``

        .. note::
            Only the **first result set** is returned. Stored procedures that
            produce multiple result sets require direct use of
            ``db.engine.raw_connection()``.

        Args:
            proc_name: Stored procedure name (validated against safe-identifier rules).
            params: Input parameters as ``{param_name: value}``.

        Returns:
            DataFrame of the first result set. Empty DataFrame if no rows.

        Example::

            df = db_manager.call_proc("sp_get_report", {"year": 2026, "month": 5})
        """
        _validate_identifier(proc_name)
        params = params or {}
        dialect = self._db.engine.dialect.name

        if dialect == "mssql":
            param_str = ", ".join(f"@{k} = :{k}" for k in params)
            sql = f"EXEC {proc_name} {param_str}".rstrip()
        else:
            param_str = ", ".join(f":{k}" for k in params)
            sql = f"CALL {proc_name}({param_str})"

        return self.fetch(sql, params)

    # ------------------------------------------------------------------
    # Paginated fetch
    # ------------------------------------------------------------------

    def fetch_page(
        self,
        sql: str,
        page: int,
        per_page: int,
        order_by: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> tuple[pd.DataFrame, int]:
        """Execute a paginated SELECT and return ``(DataFrame, total_count)``.

        Wraps *sql* in a ``COUNT(*)`` subquery to get the total, then appends
        dialect-appropriate pagination clauses for the page fetch.

        Args:
            sql: Base SELECT statement **without** ``ORDER BY`` or pagination
                clauses. Use ``:name`` placeholders for parameters.
            page: 1-based page number.
            per_page: Number of rows per page.
            order_by: Optional ``ORDER BY`` expression appended verbatim,
                e.g. ``"created_at DESC"``.  The caller is responsible for
                validating any identifier components.
            params: Bind parameters referenced in *sql*.

        Returns:
            Tuple of ``(page_DataFrame, total_row_count)``.
        """
        count_sql = f"SELECT COUNT(*) AS _cnt FROM ({sql}) AS _sub"
        count_df = self.fetch(count_sql, params)
        total = int(count_df.iloc[0]["_cnt"])

        offset = (page - 1) * per_page
        ordered = f"{sql} ORDER BY {order_by}" if order_by else sql
        dialect = self._db.engine.dialect.name

        if dialect == "mssql":
            paged_sql = (
                f"{ordered} OFFSET :_offset ROWS FETCH NEXT :_limit ROWS ONLY"
            )
        else:
            paged_sql = f"{ordered} LIMIT :_limit OFFSET :_offset"

        merged: dict[str, Any] = {**(params or {}), "_limit": per_page, "_offset": offset}
        df = self.fetch(paged_sql, merged)
        return df, total

    # ------------------------------------------------------------------
    # Transaction context manager
    # ------------------------------------------------------------------

    @contextmanager
    def transaction(self):
        """Context manager that wraps multiple operations in a single transaction.

        On exit without exception the transaction is committed; on exception
        it is rolled back.

        Example::

            with db_manager.transaction() as conn:
                conn.execute(text("INSERT INTO ..."), {...})
                conn.execute(text("UPDATE ..."), {...})
        """
        with self._db.engine.begin() as conn:
            yield conn
