import redis.asyncio as redis
import json
import os
from typing import Optional, Dict, Any
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        self.redis_client = redis.from_url(self.redis_url)
        await self.redis_client.ping()
        logger.info("Redis connected successfully")

    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()

    async def get_cache(self, key: str) -> Optional[Dict]:
        if not self.redis_client:
            return None
        try:
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set_cache(self, key: str, data: Dict, expire: int = 300):
        if not self.redis_client:
            return
        try:
            await self.redis_client.setex(key, expire, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def delete_cache(self, pattern: str):
        if not self.redis_client:
            return
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                await self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

class KafkaService:
    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        self.producer: Optional[AIOKafkaProducer] = None

    async def start_producer(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8')
        )
        await self.producer.start()
        logger.info("Kafka producer started")

    async def stop_producer(self):
        if self.producer:
            await self.producer.stop()

    async def send_message(self, topic: str, message: Dict[str, Any]):
        if not self.producer:
            logger.warning("Kafka producer not initialized")
            return
        try:
            await self.producer.send_and_wait(topic, message)
            logger.info(f"Message sent to topic {topic}: {message}")
        except Exception as e:
            logger.error(f"Failed to send message to Kafka: {e}")

redis_service = RedisService()
kafka_service = KafkaService()