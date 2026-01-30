"""
이벤트 발행을 위한 Kafka Producer 서비스.
"""
from aiokafka import AIOKafkaProducer
from ..config import get_settings
import json
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


class KafkaService:
    """Kafka 토픽으로 메시지를 발행하는 서비스."""
    
    def __init__(self):
        self.producer: AIOKafkaProducer | None = None
    
    async def start(self):
        """Kafka Producer를 시작합니다."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            logger.info("Kafka producer started successfully")
        except Exception as e:
            logger.warning(f"Failed to start Kafka producer: {e}")
            self.producer = None
    
    async def stop(self):
        """Kafka Producer를 정지합니다."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")
    
    async def publish(self, topic: str, message: dict):
        """Kafka 토픽으로 메시지를 발행합니다."""
        if self.producer:
            try:
                await self.producer.send_and_wait(topic, message)
            except Exception as e:
                logger.warning(f"Failed to publish to Kafka: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Kafka Producer 연결 상태를 확인합니다."""
        return self.producer is not None


# 싱글톤 인스턴스
kafka_service = KafkaService()
