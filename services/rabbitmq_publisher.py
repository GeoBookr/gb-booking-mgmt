import aio_pika
import asyncio
from tenacity import retry, wait_exponential, stop_after_attempt
import json
from config import settings


class EventPublisher:
    def __init__(self):
        self.url = settings.RABBITMQ_URL
        self.connection = None
        self.channel = None
        self.exchange_name = "journey.events"
        self.loop = asyncio.get_event_loop()

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.url, loop=self.loop)
        self.channel = await self.connection.channel()
        await self.channel.declare_exchange(self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
    async def publish(self, routing_key: str, message: dict):
        if not self.channel:
            await self.connect()
        print(f"[PUBLISHING] Routing key: {routing_key}")
        print(f"[Payload] {message}")
        exchange = await self.channel.get_exchange(self.exchange_name)
        body = message.encode() if isinstance(
            message, str) else json.dumps(message).encode()
        await exchange.publish(
            aio_pika.Message(body=body),
            routing_key=routing_key
        )

    async def close(self):
        if self._connection:
            await self._connection.close()


publisher = EventPublisher()
