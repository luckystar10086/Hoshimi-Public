"""Go 版 Hoshimi 存档兼容：把 materials 里的货币类道具并入 currencies。

Go 版把 40901（中级情报徽章）、41601（行动记录）等货币材料存放在
``materials``；Python 版的余额体系统一读 ``currencies``。直接复制 Go 存档时
这些余额会显示为 0，导致商店扣款失败。这里在读取存档时做一次性迁移：
仅当 currencies 中该键缺失或为 0 时，才用 materials 的数值填充；随后删除
materials 中的同名键，避免两套余额各写一份后出现“余额回弹”。
"""

from .currency_data import MATERIAL_TOKEN_IDS, NATIVE_CURRENCY_IDS

BALANCE_IDS = frozenset(NATIVE_CURRENCY_IDS + MATERIAL_TOKEN_IDS)


def normalize_go_save(user: dict) -> bool:
    """就地迁移，返回是否发生了改动。"""
    materials = user.get('materials')
    if not isinstance(materials, dict) or not materials:
        return False
    currencies = user.setdefault('currencies', {})
    changed = False
    for key in list(materials.keys()):
        try:
            item = int(key)
        except (TypeError, ValueError):
            continue
        if item not in BALANCE_IDS:
            continue
        try:
            amount = int(materials.get(key) or 0)
        except (TypeError, ValueError):
            amount = 0
        current_key = str(item)
        try:
            current = int(currencies.get(current_key) or 0)
        except (TypeError, ValueError):
            current = 0
        if amount > 0 and current <= 0:
            currencies[current_key] = amount
        # Python 版以 currencies 为准，材料表里的货币键不再保留副本。
        del materials[key]
        changed = True
    return changed
