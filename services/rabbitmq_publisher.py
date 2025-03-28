import aio_pika
import json
from config import settings


class EventPublisher:
    def __init__(self):
        self._connection = None
        self._channel = None

    async def connect(self):
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self._channel = await self._connection.channel()

    async def publish(self, routing_key: str, message: dict):
        if self._channel is None:
            await self.connect()

        message_body = json.dumps(message).encode()
        await self._channel.default_exchange.publish(
            aio_pika.Message(
                body=message_body,
                content_type="application/json"
            ),
            routing_key=routing_key
        )

    async def close(self):
        if self._connection:
            await self._connection.close()


publisher = EventPublisher()
