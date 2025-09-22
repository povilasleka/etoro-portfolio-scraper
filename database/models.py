from peewee import Model, CharField, BigIntegerField, DecimalField, ForeignKeyField, DateTimeField
import hashlib
from .connection import db


class BaseModel(Model):
    class Meta:
        database = db


class Portfolio(BaseModel):
    display_name = CharField(max_length=255, unique=True)


class Position(BaseModel):
    portfolio = ForeignKeyField(Portfolio, backref='positions', null=False)
    position_id = BigIntegerField(null=False)
    cid = BigIntegerField(null=False)
    instrument_id = BigIntegerField(null=False)
    open_datetime = DateTimeField(null=False)
    open_rate = DecimalField(null=False)
    amount = DecimalField(null=False)
    direction = CharField(max_length=255, null=False)
    take_profit_rate = DecimalField(null=True)
    stop_loss_rate = DecimalField(null=True)
    display_name = CharField(max_length=255, null=False)
    symbol = CharField(max_length=255, null=False)
    leverage = BigIntegerField(null=False)
    hash_value = CharField(max_length=64, null=True)

    def __init__(self, **kwargs):
        super(Position, self).__init__(**kwargs)
        if not self.hash_value:  # Only generate if not already set
            self.hash_value = self._generate_sha256()

    def __str__(self):
        return f"<Position: {self.display_name} ({self.symbol})>"

    def _generate_sha256(self):
        data = f"{self.position_id}{self.cid}{self.instrument_id}{self.open_datetime}{self.open_rate}{self.amount}{self.direction}{self.take_profit_rate}{self.stop_loss_rate}{self.display_name}{self.symbol}{self.leverage}"
        return hashlib.sha256(data.encode()).hexdigest()