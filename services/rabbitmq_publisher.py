import aio_pika
import asyncio
import json
import logging
from tenacity import retry, wait_exponential, stop_after_attempt
from config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    def __init__(self):
        self.url = settings.RABBITMQ_URL
        self.connection = None
        self.channel = None
        self.exchange = None
        self.exchange_name = "journey.events"

    async def connect(self):
        try:
            logger.info(
                "Attempting to connect to RabbitMQ (Journey Booking Service)...")
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
            )
            logger.info(
                "Connected to RabbitMQ and declared exchange successfully.")
        except Exception as e:
            logger.exception(f"Failed to connect to RabbitMQ: {e}")
            raise

    @retry(wait=wait_exponential(multiplier=1, min=1, max=10), stop=stop_after_attempt(5))
    async def publish(self, message: dict):
        if not self.exchange:
            await self.connect()
        try:
            logger.info(
                f"Publishing event with routing key: {message['event_type']}")
            logger.info(f"Payload: {message}")
            body = json.dumps(message, default=str).encode()
            await self.exchange.publish(
                aio_pika.Message(body=body),
                routing_key=message['event_type']
            )
            logger.info("Event published successfully.")
        except Exception as e:
            logger.exception(f"Error publishing event: {e}")
            raise

    async def close(self):
        if self.connection:
            await self.connection.close()
            logger.info("RabbitMQ connection closed.")


publisher = EventPublisher()
