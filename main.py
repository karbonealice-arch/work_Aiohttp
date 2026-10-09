from aiohttp import web
from datetime import datetime

# In-memory storage for ads
ads: dict[int, dict] = {}
next_id: int = 1


async def create_ad(request: web.Request) -> web.Response:
    global next_id

    try:
        data = await request.json()
    except Exception:
        return web.json_response({'error': 'Request body must be JSON'}, status=400)

    required_fields = ['title', 'description', 'owner']
    for field in required_fields:
        if field not in data:
            return web.json_response({'error': f'Missing required field: {field}'}, status=400)

    ad_id = next_id
    next_id += 1

    ad = {
        'id': ad_id,
        'title': data['title'],
        'description': data['description'],
        'creation_date': datetime.now().isoformat(),
        'owner': data['owner']
    }

    ads[ad_id] = ad
    return web.json_response(ad, status=201)


async def get_ads(request: web.Request) -> web.Response:
    ad_id = request.query.get('id')

    if ad_id:
        ad_id = int(ad_id)
        if ad_id not in ads:
            return web.json_response({'error': 'Ad not found'}, status=404)
        return web.json_response(ads[ad_id])

    return web.json_response(list(ads.values()))


async def update_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['id'])

    if ad_id not in ads:
        return web.json_response({'error': 'Ad not found'}, status=404)

    try:
        data = await request.json()
    except Exception:
        return web.json_response({'error': 'Request body must be JSON'}, status=400)

    updatable_fields = ['title', 'description', 'owner']
    for field in updatable_fields:
        if field in data:
            ads[ad_id][field] = data[field]

    return web.json_response(ads[ad_id])


async def delete_ad(request: web.Request) -> web.Response:
    ad_id = int(request.match_info['id'])

    if ad_id not in ads:
        return web.json_response({'error': 'Ad not found'}, status=404)

    deleted_ad = ads.pop(ad_id)
    return web.json_response(deleted_ad)


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post('/ads', create_ad)
    app.router.add_get('/ads', get_ads)
    app.router.add_put('/ads/{id}', update_ad)
    app.router.add_delete('/ads/{id}', delete_ad)
    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app)
