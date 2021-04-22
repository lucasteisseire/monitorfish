from typing import Union


def catch_zone_isin_fao_zone(
    catch_zone: Union[None, str], fao_zone: Union[None, str]
) -> bool:
    """Return
    - True if a catch zone (e.g. '27.7.b') is in a given fao_zone (e.g. '27.7.b' or
    '27')
    - False if a catch zone (e.g. '27.7.b') is NOT in a given fao_zone (e.g. '28.6' or
    '27.7.b.4')
    - True if the fao_zone if None (whatever the value of the catch_zone)
    - False if the fao_zone is not None and the catch_zone is None
    """
    if fao_zone is None:
        return True
    elif catch_zone is None:
        return False
    else:
        return fao_zone in catch_zone
