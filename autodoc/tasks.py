"""Define tasks that can be run asynchonously by a dramatiq worker."""

from typing import Optional

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from autodoc.config import DB_PATH, REDIS_HOST
from autodoc.data.manager import DatabaseManager
from autodoc.workflow import Workflow

redis_broker = RedisBroker(host=REDIS_HOST, port=6379)
dramatiq.set_broker(redis_broker)


@dramatiq.actor
def process_instance(instance_id: int, upload_mapping: Optional[dict], form_data=Optional[dict]):
    """Process an instance."""
    manager = DatabaseManager(db_file=DB_PATH)

    workflow = Workflow.from_instance_id(
        instance_id=instance_id,
        manager=manager,
        upload_mapping=upload_mapping,
        form_data=form_data,
    )

    workflow.process()
