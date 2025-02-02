import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agricola.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = 'true'
django.setup()


async def main():
    from core.redis import connection
    from play.models.game import Game

    redis = connection()

    # redis DB 전체 초기화
    redis.flushdb()

    # ! 임시 코드 작성 시작
    from cards.models import Card, CardEffect
    redis = connection()
    cards = Card.objects.all().values('card_number', 'command', 'name', 'score', 'cost', 'condition')
    effects = CardEffect.objects.all().values('card_number', 'condition', 'effect', 'command')
    for effect in effects:
        redis.hset(f'cards:{effect["card_number"]}', effect["effect"], effect["command"])
        if effect['condition'] is not None:
            redis.hset(f'cards:effects:{effect["effect"]}', effect["card_number"], effect["condition"])
    redis.hset(
        'commands',
        mapping={card['card_number']: card['command'] for card in cards if card['command'] is not None}
    )
    redis.hset(
        'costs',
        mapping={card['card_number']: card['cost'] for card in cards if card['cost'] is not None}
    )
    redis.hset(
        'condition',
        mapping={card['card_number']: card['condition'] for card in cards if card['condition'] is not None}
    )

    redis.hset('cards', mapping={card['card_number']: str({
        'card_number': card['card_number'],
        'name': card['name'],
        'score': card['score']
    }) for card in cards})
    # ! 임시 코드 작성 끝

    game = await Game.initialize(["1", "2", "3", "4"])
    redis.set("game_3", str(game.to_dict()))


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
