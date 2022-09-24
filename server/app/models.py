"""DB models"""

from tortoise import Model, fields

from server.constants import REGICIDE


class Player(Model):
    """Player model"""

    date_joined = fields.DatetimeField(auto_now_add=True)
    email = fields.TextField(email=True)
    id = fields.UUIDField(pk=True)
    name = fields.TextField(null=True)
    nickname = fields.CharField(unique=True, max_length=60)
    password = fields.TextField()


class Game(Model):
    """Game model"""

    id = fields.UUIDField(pk=True)
    name = fields.TextField()


class Room(Model):
    """Room model"""

    admin = fields.ForeignKeyField("models.Player", related_name="admin_rooms")
    date_closed = fields.DatetimeField(null=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    game = fields.ForeignKeyField("models.Game", related_name="rooms")
    id = fields.UUIDField(pk=True)
    participants = fields.ManyToManyField("models.Player", related_name="")
    status = fields.SmallIntField()


async def init_fake_data():
    game = await Game.create(name=REGICIDE)
    foo = await Player.create(
        email="foo@f.oo",
        name="Foo",
        nickname="foo",
        password="$2b$12$5LAFLk9LJlem6ZUH2KmZO.T81anazVEcqoMZjZ5ezzmS7b13JUQeS",
    )
    await Player.create(
        email="bar@b.ar",
        name="Bar",
        nickname="bar",
        password="$2b$12$5LAFLk9LJlem6ZUH2KmZO.T81anazVEcqoMZjZ5ezzmS7b13JUQeS",
    )
    room = await Room.create(admin=foo, game=game, status=0)
    await room.participants.add(foo)
