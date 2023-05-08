from datetime import datetime, timedelta
import os
import glob
import importlib.util
import sys

from core.tasks.base_task import BaseTask
from core.helpers import bcolors


def get_tasks() -> list[BaseTask]:
    paths_to_tasks = glob.glob(f"{os.getcwd()}\\core\\tasks\\task_*.py")
    tasks: list[BaseTask] = []

    for path_to_task in paths_to_tasks:
        # https://stackoverflow.com/questions/67631

        spec = importlib.util.spec_from_file_location("module.name", path_to_task)
        module = importlib.util.module_from_spec(spec)

        sys.modules["module.name"] = module
        spec.loader.exec_module(module)

        tasks.append(module.Task())

    return tasks


def start_tasks() -> None:
    tasks = get_tasks()

    for task in tasks:
        task.start()

    # print(
    #     f"{bcolors.OKGREEN}INFO{bcolors.ENDC}:  "
    #     f"Tasks {bcolors.BOLD}{[j.name for j in tasks]}{bcolors.ENDC} have started."
    # )

    for task in tasks:
        next_iteration = datetime.today() + timedelta(seconds=task.countdown)
        next_iteration = next_iteration.replace(microsecond=0)

        print(
            f"{bcolors.OKGREEN}INFO{bcolors.ENDC}:  "
            f"Task {bcolors.BOLD}{task.name}{bcolors.ENDC}"
            f" starts at: {bcolors.BOLD}{next_iteration}{bcolors.ENDC}"
        )
