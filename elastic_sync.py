import asyncio
import json
import sys
from datetime import UTC, datetime
from typing import Any, Generator

import psycopg2
from elasticsearch import Elasticsearch, NotFoundError, helpers
from psycopg2.extras import RealDictCursor

from config import settings
from elastic_db_init import create_index

SQL_STREAM_VERSES = """
SELECT
  verse.poem_id,
  verse.vorder,
  verse.text AS verse_text,
  poem.title AS poem_title,
  poet.name AS poet_name
FROM verse
JOIN poem ON verse.poem_id = poem.id
JOIN cat ON poem.cat_id = cat.id
JOIN poet ON cat.poet_id = poet.id
ORDER BY verse.poem_id, verse.vorder;
"""


def log_event(event: str, **fields: Any) -> None:
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event,
        **fields,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def create_es_client() -> Elasticsearch:
    api_key = settings.get("ES_API_KEY", "")
    if api_key:
        return Elasticsearch(settings.ES_HOST, api_key=api_key)
    return Elasticsearch(settings.ES_HOST)


def create_pg_connection() -> psycopg2.extensions.connection:
    conn = psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )
    conn.set_session(
        isolation_level="REPEATABLE READ",
        readonly=True,
        autocommit=False,
    )
    return conn


def fetch_verse_count(conn: psycopg2.extensions.connection) -> int:
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM verse")
        row = cursor.fetchone()
        return int(row[0])


def iter_bulk_actions(
        conn: psycopg2.extensions.connection,
        index_name: str,
        batch_size: int,
) -> Generator[dict[str, Any], None, None]:
    cursor_name = f"es_sync_cursor_{int(datetime.now(UTC).timestamp())}"
    with conn.cursor(name=cursor_name, cursor_factory=RealDictCursor) as cursor:
        cursor.itersize = batch_size
        cursor.execute(SQL_STREAM_VERSES)
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            for row in rows:
                poem_id = int(row["poem_id"])
                vorder = int(row["vorder"])
                yield {
                    "_op_type": "index",
                    "_index": index_name,
                    "_id": f"{poem_id}:{vorder}",
                    "_source": {
                        "poem_id": poem_id,
                        "poet_name": row["poet_name"] or "",
                        "poem_title": row["poem_title"] or "",
                        "verse_text": row["verse_text"] or "",
                    },
                }


def build_physical_index_name(alias_name: str) -> str:
    suffix = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
    return f"{alias_name}_{suffix}"


def get_alias_indices(client: Elasticsearch, alias_name: str) -> list[str]:
    try:
        alias_response = client.indices.get_alias(name=alias_name)
        return sorted(alias_response.keys())
    except NotFoundError:
        return []


def cutover_alias(client: Elasticsearch, alias_name: str, new_index: str) -> None:
    current_indices = get_alias_indices(client, alias_name)
    actions: list[dict[str, Any]] = []
    for index_name in current_indices:
        actions.append({"remove": {"index": index_name, "alias": alias_name}})
    actions.append({"add": {"index": new_index, "alias": alias_name}})
    client.indices.update_aliases(actions=actions)


def cleanup_old_indices(
        client: Elasticsearch,
        alias_name: str,
        keep_historical: int,
) -> list[str]:
    keep_historical = max(0, int(keep_historical))
    keep_total = keep_historical + 1  # Include current active index.
    pattern = f"{alias_name}_*"
    try:
        physical_indices = sorted(client.indices.get(index=pattern).keys())
    except NotFoundError:
        return []

    if len(physical_indices) <= keep_total:
        return []

    to_delete = physical_indices[:-keep_total]
    for index_name in to_delete:
        client.indices.delete(index=index_name)
    return to_delete


def acquire_advisory_lock(conn: psycopg2.extensions.connection, lock_key: int) -> bool:
    with conn.cursor() as cursor:
        cursor.execute("SELECT pg_try_advisory_lock(%s)", (lock_key,))
        row = cursor.fetchone()
        return bool(row[0])


def release_advisory_lock(conn: psycopg2.extensions.connection, lock_key: int) -> None:
    with conn.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_unlock(%s)", (lock_key,))


def _sync_blocking() -> int:
    alias_name = settings.ES_INDEX_NAME
    chunk_size = int(settings.get("ES_SYNC_CHUNK_SIZE", 1000))
    keep_historical = int(settings.get("ES_SYNC_KEEP_INDICES", 2))
    lock_key = int(settings.get("ES_SYNC_LOCK_KEY", 6072026001))

    log_event(
        "sync_start",
        alias_name=alias_name,
        chunk_size=chunk_size,
        keep_historical=keep_historical,
    )

    pg_conn = create_pg_connection()
    es_client = create_es_client()
    lock_acquired = False

    try:
        lock_acquired = acquire_advisory_lock(pg_conn, lock_key)
        if not lock_acquired:
            log_event("sync_skipped_lock_not_acquired", lock_key=lock_key)
            return 0

        if not es_client.ping():
            raise RuntimeError("Could not connect to Elasticsearch.")

        verse_count = fetch_verse_count(pg_conn)
        physical_index_name = build_physical_index_name(alias_name)

        create_index(es_client, physical_index_name, delete_if_exists=False)
        log_event("index_created", index_name=physical_index_name, verse_count=verse_count)

        indexed_count = 0
        failed_count = 0
        first_error: dict[str, Any] | None = None
        actions = iter_bulk_actions(pg_conn, physical_index_name, batch_size=chunk_size)
        for ok, result in helpers.streaming_bulk(
                client=es_client,
                actions=actions,
                chunk_size=chunk_size,
                raise_on_error=False,
                raise_on_exception=False,
                max_retries=2,
        ):
            if ok:
                indexed_count += 1
            else:
                failed_count += 1
                if first_error is None:
                    first_error = result

        if failed_count > 0:
            raise RuntimeError(
                f"Bulk indexing completed with failures: failed_count={failed_count}, "
                f"first_error={first_error}"
            )

        es_client.indices.refresh(index=physical_index_name)
        es_count = int(es_client.count(index=physical_index_name)["count"])

        log_event(
            "indexing_finished",
            index_name=physical_index_name,
            indexed_count=indexed_count,
            postgres_count=verse_count,
            elastic_count=es_count,
        )

        if verse_count != es_count:
            raise RuntimeError(
                f"Count mismatch after sync: postgres_count={verse_count}, elastic_count={es_count}"
            )

        cutover_alias(es_client, alias_name, physical_index_name)
        log_event("alias_cutover_completed", alias_name=alias_name, index_name=physical_index_name)

        deleted_indices = cleanup_old_indices(es_client, alias_name, keep_historical=keep_historical)
        log_event("cleanup_completed", deleted_indices=deleted_indices, deleted_count=len(deleted_indices))

        log_event("sync_success", index_name=physical_index_name)
        return 0
    except Exception as exc:
        log_event("sync_failed", error=str(exc))
        return 1
    finally:
        if lock_acquired:
            try:
                release_advisory_lock(pg_conn, lock_key)
            except Exception as unlock_exc:
                log_event("lock_release_failed", error=str(unlock_exc), lock_key=lock_key)
        pg_conn.close()
        es_client.close()


async def sync(_=None) -> int:
    """Async entrypoint for PTB job_queue; runs blocking sync in a worker thread."""
    return await asyncio.to_thread(_sync_blocking)


def sync_on_startup() -> None:
    result = _sync_blocking()
    if result != 0:
        raise RuntimeError("Elasticsearch startup sync failed.")


if __name__ == "__main__":
    sys.exit(_sync_blocking())
