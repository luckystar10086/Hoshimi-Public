# -*- coding: utf-8 -*-
"""满超越角色多余情报兑换徽章（cs_14032 -> sc_14033）。

规则与官服口径一致：
- 每个已解锁角色从当前星级到 504 的剩余升级需求为 needed；
- 碎片数超过 needed 的部分为多余；
- 多余碎片按 1:5 转化；
- 初始星级 300（SSR / rare 5）给高级情报徽章 40902，其余给中级 40901。
"""

from functools import lru_cache

from .gameplay_protocol import read_client_data

_STAR_ORDER = [100, 101, 102, 103, 104, 200, 201, 202, 203, 204,
               300, 301, 302, 303, 304, 400, 401, 402, 403, 404,
               500, 501, 502, 503, 504]
_STAR_UP_MAP = {
    100: 2, 101: 2, 102: 2, 103: 2, 104: 4,
    200: 3, 201: 3, 202: 3, 203: 3, 204: 6,
    300: 5, 301: 5, 302: 5, 303: 5, 304: 10,
    400: 10, 401: 10, 402: 10, 403: 10, 404: 50,
    500: 20, 501: 20, 502: 20, 503: 20, 504: 100,
}


@lru_cache(maxsize=8192)
def hero_badge_rare(hero_id: int) -> int:
    """返回徽章档位：3=中级(40901)，5=高级(40902)。

    HeroCfg.rare 是 1/2/3 的稀有度枚举，不能直接拿来判断；
    按 unlock_star 映射到官服 3/4/5 的徽章档位。
    """
    cfg = read_client_data(f"require('HeroCfg')[{hero_id}]")
    unlock_star = int(cfg.get('unlock_star') or 100)
    if unlock_star >= 300:
        return 5
    if unlock_star >= 200:
        return 4
    return 3


def resolve_fragments(user: dict) -> dict:
    """就地扣掉多余碎片并发放徽章，返回本次产出。"""
    heroes = {}
    for hero in user.get('heroes', []):
        hid = int(hero['id'])
        if hero.get('unlock', 0) == 1 or int(hero.get('star', 0)) > 0:
            heroes[hid] = hero

    pieces = user.setdefault('hero_pieces', {})
    total_mid = 0
    total_adv = 0

    for hid, hero in heroes.items():
        star = int(hero.get('star', 100))
        needed = 0
        if star in _STAR_ORDER:
            needed = sum(_STAR_UP_MAP.get(s, 0) for s in _STAR_ORDER[_STAR_ORDER.index(star):])
        # 504 之后、600 及以上：needed 保持 0

        have = int(pieces.get(str(hid), 0))
        if have <= needed:
            continue
        surplus = have - needed
        pieces[str(hid)] = needed
        if hero_badge_rare(hid) == 5:
            total_adv += surplus * 5
        else:
            total_mid += surplus * 5

    # 40901/40902 属于 MATERIAL_TOKEN_IDS，Python 版统一以 currencies 为准；
    # 若沿用 Go 的 materials 写法，余额检查仍读 currencies，兑换后会无法再消费。
    currencies = user.setdefault('currencies', {})
    materials = user.get('materials')
    for key, amount in (('40901', total_mid), ('40902', total_adv)):
        if amount:
            currencies[key] = int(currencies.get(key, 0)) + amount
        if isinstance(materials, dict):
            materials.pop(key, None)
    return {'mid': total_mid, 'adv': total_adv}
