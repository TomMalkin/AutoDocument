"""Define tasks that can be run asynchonously by a dramatiq worker."""

from typing import Optional

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from autodoc.config import DB_PATH, REDIS_HOST
from autodoc.data.manager import DatabaseManager
from autodoc.workflow.workflow_factory import WorkflowRunnerFactory

redis_broker = RedisBroker(host=REDIS_HOST, port=6379)
dramatiq.set_broker(redis_broker)


@dramatiq.actor(max_retries=1)
def process_instance(instance_id: int, form_data: Optional[dict], upload_mapping: Optional[dict]):
    """Process an instance."""
    manager = DatabaseManager(db_file=DB_PATH)

    workflow_runner = WorkflowRunnerFactory.create_runner(
        instance_id=instance_id, manager=manager, form_data=form_data, upload_mapping=upload_mapping
    )

    workflow_runner.process()
