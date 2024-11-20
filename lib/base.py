import os
import sys
import time
import traceback
from collections import OrderedDict
from typing import Any, Dict, List, Union

from loguru import logger

from lib.utils.execute import execute
from lib.utils.logging import timeit_logger
from lib.utils.systool import wait_until_memory_available

class ErrorMessage(str):
    def __repr__(self):
        return (
            "Error Message >>>>>>>>>\n"
            + str(self)
            + "\n<<<<<<<<<< Error Message"
        )


class BaseRunner:
    def __init__(
        self, requests: List[Dict[str, Any]]
    ) -> None:

        self.requests = requests
        self._runners = OrderedDict()
        self.run_time = 0.0

        self._info_reportor = None

    def add_runner(self, name, runner: "BaseRunner"):
        # set child runner's db_path to parent's db_path
        # self.set_defaults(runner, "db_path", self.db_path)
        self._runners[name] = runner

    def remove_runner(self, name):
        del self._runners[name]

    def __setattr__(self, name: str, value: Union["BaseRunner", Any]) -> None:
        runners = self.__dict__.get("_runners")
        if isinstance(value, BaseRunner):
            self.add_runner(name, value)
        else:
            if runners is not None and name in runners:
                self.remove_runner(name)
        object.__setattr__(self, name, value)

    def __repr__(self) -> str:
        str_repr = ""
        str_repr += f"{self.__class__.__name__} ({len(self.requests)})"
        if len(self._runners) > 0:
            str_repr += "\n["
            for runner in self._runners.values():
                str_repr += f"\n{runner}".replace("\n", "\n  ")
            str_repr += "\n]"
        return str_repr

    def on_run_start(self):
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def on_run_end(self):
        pass

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.on_run_start()
        t_start = time.time()
        res = None
        try:
            # someting error when processing long sequence
            wait_until_memory_available(min_percent=20.0, min_memory=20.0)
            run_wrapper = timeit_logger(self.run)
            res = run_wrapper(*args, **kwds)
        except Exception as e:
            traceback.print_exception(*sys.exc_info())
            return False

        self.run_time += time.time() - t_start
        self.on_run_end()
        return res


class BaseCommandRunner(BaseRunner):
    """Process requests one by one."""

    def _decorate_command(self, command):
        # Add PYTHONPATH to execute scripts
        command = f"export PYTHONPATH={os.getcwd()}:$PYTHONPATH && {command}"
        return command

    def build_command(self, request: Dict[str, Any]) -> str:
        """Build a bash command according to the request."""
        raise NotImplementedError

    def run(self, dry=False):
        for i, request in enumerate(self.requests):
            try:
                command = self._decorate_command(self.build_command(request))
                logger.info(f"[{i}] {command}")
                if not dry:
                    execute(command)
            except:
                logger.exception("Exception happend during executing!")
                