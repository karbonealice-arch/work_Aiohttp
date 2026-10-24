import aiosqlite
from aiohttp import web
from datetime import datetime

DB_PATH = "ads.db"

DB_SCHEMA = """
            CREATE TABLE IF NOT EXISTS ads
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                title
                TEXT
                NOT
                NULL,
                description
                TEXT
                NOT
                NULL,
                owner
                TEXT
                NOT
                NULL,
                created_at
                TEXT
                NOT
                NULL
            ) \
            """


async def init_db(app: web.Application) -> None:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    app["db"] = db
    await db.execute(DB_SCHEMA)
    await db.commit()


async def close_db(app: web.Application) -> None:
    await app["db"].close()


def _row_to_dict(row: aiosqlite.Row) -> dict:
    return dict(row)


async def create_ad(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Request body must be JSON"}, status=400)

    required_fields = ["title", "description", "owner"]
    for field in required_fields:
        if field not in data:
            return web.json_response(
                {"error": f"Missing required field: {field}"}, status=400
            )

    db: aiosqlite.Connection = request.app["db"]
    created_at = datetime.now().isoformat()
    cursor = await db.execute(
        "INSERT INTO ads (title, description, owner, created_at) VALUES (?, ?, ?, ?)",
        (data["title"], data["description"], data["owner"], created_at),
    )
    await db.commit()
    ad_id = cursor.lastrowid

    async with db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)) as cursor:
        row = await cursor.fetchone()

    return web.json_response(_row_to_dict(row), status=201)


async def get_ads(request: web.Request) -> web.Response:
    ad_id = request.match_info.get("id")

    db: aiosqlite.Connection = request.app["db"]

    if ad_id:
        async with db.execute(
                "SELECT * FROM ads WHERE id = ?", (int(ad_id),)
        ) as cursor:
            row = await cursor.fetchone()
        if not row:
            return web.json_response({"error": "Ad not found"}, status=404)
        return web.json_response(_row_to_dict(row))

    async with db.execute("SELECT * FROM ads") as cursor:
        rows = await cursor.fetchall()

    return web.json_response([_row_to_dict(r) for r in rows])


async def update_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info["id"])
    db: aiosqlite.Connection = request.app["db"]

    async with db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)) as cursor:
        row = await cursor.fetchone()
    if not row:
        return web.json_response({"error": "Ad not found"}, status=404)

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Request body must be JSON"}, status=400)

    updatable_fields = ["title", "description", "owner"]
    sets = []
    values = []
    for field in updatable_fields:
        if field in data:
            sets.append(f"{field} = ?")
            values.append(data[field])

    if sets:
        values.append(ad_id)
        await db.execute(
            f"UPDATE ads SET {', '.join(sets)} WHERE id = ?", values
        )
        await db.commit()

    async with db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)) as cursor:
        row = await cursor.fetchone()

    return web.json_response(_row_to_dict(row))


async def patch_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info["id"])
    db: aiosqlite.Connection = request.app["db"]

    async with db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)) as cursor:
        row = await cursor.fetchone()
    if not row:
        return web.json_response({"error": "Ad not found"}, status=404)

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Request body must be JSON"}, status=400)

    updatable_fields = ["title", "description", "owner"]
    sets = []
    values = []
    for field in updatable_fields:
        if field in data:
            sets.append(f"{field} = ?")
            values.append(data[field])

    if sets:
        values.append(ad_id)
        await db.execute(
            f"UPDATE ads SET {', '.join(sets)} WHERE id = ?", values
        )
        await db.commit()

    async with db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)) as cursor:
        row = await cursor.fetchone()

    return web.json_response(_row_to_dict(row))


async def delete_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info["id"])
    db: aiosqlite.Connection = request.app["db"]

    async with db.execute("SELECT * FROM ads WHERE id = ?", (ad_id,)) as cursor:
        row = await cursor.fetchone()
    if not row:
        return web.json_response({"error": "Ad not found"}, status=404)

    await db.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
    await db.commit()

    return web.json_response(_row_to_dict(row))


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(init_db)
    app.on_cleanup.append(close_db)

    app.router.add_post("/ads", create_ad)
    app.router.add_get("/ads", get_ads)
    app.router.add_get("/ads/{id}", get_ads)
    app.router.add_put("/ads/{id}", update_ad)
    app.router.add_patch("/ads/{id}", patch_ad)
    app.router.add_delete("/ads/{id}", delete_ad)

    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app)
