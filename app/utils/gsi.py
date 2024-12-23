from types import UnionType
from typing import Optional, Union, get_args, Any, Generic

import msgspec




class Provider(msgspec.Struct):
    name: Optional[str] = None
    appid: Optional[int] = None
    version: Optional[int] = None
    steamid: Optional[str] = None
    timestamp: Optional[int] = None


class Team(msgspec.Struct):
    score: Optional[int] = None
    name: Optional[str] = None
    consecutive_round_losses: Optional[int] = None
    timeouts_remaining: Optional[int] = None
    matches_won_this_series: Optional[int] = None


class Map(msgspec.Struct):
    mode: Optional[str] = None
    name: Optional[str] = None
    phase: Optional[str] = None
    round: Optional[int] = None
    team_ct: Optional[Team] = None
    team_t: Optional[Team] = None
    num_matches_to_win_series: Optional[int] = None
    win_team: Optional[str] = None
    round_wins: Optional[dict[str, str]] = None


class Bomb(msgspec.Struct):
    state: Optional[str] = None
    position: Optional[str] = None
    player: Optional[str] = None
    countdown: Optional[str] = None


class Round(msgspec.Struct):
    phase: Optional[str] = None
    win_team: Optional[str] = None
    bomb: Optional[str] = None

class PlayerState(msgspec.Struct):
    health: Optional[int] = None
    armor: Optional[int] = None
    helmet: Optional[bool] = None
    flashed: Optional[int] = None
    smoked: Optional[int] = None
    burning: Optional[int] = None
    money: Optional[int] = None
    round_kills: Optional[int] = None
    round_killhs: Optional[int] = None
    round_totaldmg: Optional[int] = None
    equip_value: Optional[int] = None
    defusekit: Optional[bool] = None

class Player(msgspec.Struct):
    steamid: Optional[str] = None
    name: Optional[str] = None
    observer_slot: Optional[int] = None
    team: Optional[str] = None
    activity: Optional[str] = None
    position: Optional[str] = None
    spectarget: Optional[str] = None
    forward: Optional[str] = None
    state: Optional[PlayerState] = None

class PhaseCountdowns(msgspec.Struct):
    phase: Optional[str] = None
    phase_ends_in: Optional[str] = None

class Grenade(msgspec.Struct):
    owner: Optional[str] = None
    position: Optional[str] = None
    velocity: Optional[str] = None
    lifetime: Optional[str] = None
    type: Optional[str] = None
    effecttime: Optional[str] = None

class HUDGSI(msgspec.Struct):
    provider: Provider | bool | None = None
    player: Player | bool | None = None
    round: Round | bool | None = None
    bomb: Bomb | bool | None = None
    map: Map | bool | None = None
    phase_countdowns: PhaseCountdowns | bool | None = None
    previously: Optional['HUDGSI'] = None
    allplayers: dict[str, Player] | bool | None = None
    grenades: dict[str, Grenade] | bool | None = None
    added: dict[Any, Any] | bool | None = None



def compare_struct(model: msgspec.Struct, obj: dict, prefix_path: tuple = None):
    unexpected_fields = set()
    _expected_fields = set(model.__struct_fields__)
    _unexpected_fields = set(obj.keys()) - _expected_fields
    if prefix_path is None:
        unexpected_fields.update((_unexpected_field,) for _unexpected_field in _unexpected_fields)
    else:
        unexpected_fields.update((*prefix_path, _unexpected_field) for _unexpected_field in _unexpected_fields)

    for _expected_field in _expected_fields:
        if _expected_field not in obj:
            continue
        ann = model.__annotations__[_expected_field]

        if (hasattr(ann, "__origin__") and ann.__origin__ is Union) or isinstance(ann, (UnionType, dict, tuple)):
            options = get_args(ann)
        else:
            options = (ann,)

        for option in options:
            if not isinstance(option, type):
                continue
            if not issubclass(option, msgspec.Struct):
                continue
            prefix_path_new = (_expected_field,) if prefix_path is None else prefix_path + (_expected_field,)
            unexpected_fields.update(compare_struct(option, obj[_expected_field], prefix_path=prefix_path_new))
    return unexpected_fields


if __name__ == '__main__':
    some = HUDGSI.__annotations__['provider']
    print(HUDGSI.__annotations__['provider'])