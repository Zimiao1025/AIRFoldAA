from celery import Celery

import os
from typing import Any, Dict, List
from loguru import logger

from lib.base import BaseCommandRunner
from lib.utils import misc, pathtool
from lib.tool import run_chai


CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")
CELERY_BROKER_URL = (
    os.environ.get("CELERY_BROKER_URL", "pyamqp://guest:guest@localhost:5672/"),
)

celery = Celery(
    __name__,
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

celery.conf.task_routes = {
    "worker.*": {"queue": "queue_chai"},
}

@celery.task(name="chai")
def chaiTask(request: Dict[str, Any]):
    ChaiRunner(requests=[request])()


class ChaiRunner(BaseCommandRunner):
    def __init__(
        self, requests: List[Dict[str, Any]]
    ):
        super().__init__(requests)
    
    def build_command(self, request: Dict[str, Any]) -> str:
        chai_config = request["run_config"]
        
        pred_model = os.path.join(request["output_dir"], "pred.model_idx_0.cif")
        if os.path.exists(pred_model):
            logger.info("pred_model already exists! skip.")
            command = ""
            
        else:
            command = "".join(
                [
                    f"python {pathtool.get_module_path(run_chai)} ",
                    f"--fasta_path {misc.safe_get(request, 'fasta_path')} ",
                    f"--output_dir {misc.safe_get(request, 'output_dir')} ",
                    f"--msa_dir {misc.safe_get(request, 'msa_dir')} ",
                    f"--a3m_paths {misc.safe_get(request, 'a3m_paths')} ",
                    # get chai params
                    f"--ntr {misc.safe_get(chai_config, 'ntr')} "
                        if misc.safe_get(chai_config, "ntr")
                        else "",
                    f"--ndt {misc.safe_get(chai_config, 'ndt')} "
                        if misc.safe_get(chai_config, "ndt")
                        else "",
                    f"--random_seed {misc.safe_get(chai_config, 'random_seed')} "
                        if misc.safe_get(chai_config, "random_seed")
                        else "",
                ]
            )

        return command
