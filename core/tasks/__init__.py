from datetime import datetime, timedelta
import os
import glob
import importlib.util
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import config

from core.tasks.base_task import BaseTask
from core.helpers import bcolors
from dotenv import load_dotenv

load_dotenv()


def get_tasks(session) -> list[BaseTask]:
    paths_to_tasks = glob.glob(f"{os.getcwd()}\\core\\tasks\\task_*.py")
    tasks: list[BaseTask] = []

    for path_to_task in paths_to_tasks:
        # https://stackoverflow.com/questions/67631

        spec = importlib.util.spec_from_file_location("module.name", path_to_task)
        module = importlib.util.module_from_spec(spec)

        sys.modules["module.name"] = module
        spec.loader.exec_module(module)

        tasks.append(module.Task(session=session, capture_exceptions=config.TASK_CAPTURE_EXCEPTIONS))

    return tasks


def start_tasks() -> None:
    # Not using the config's connection string as that uses async.
    engine = create_engine(f"postgresql+psycopg2://{os.getenv('DU')}:{os.getenv('DP')}@{os.getenv('H')}:{os.getenv('P')}/{os.getenv('DB')}")
    Session = sessionmaker(engine)

    with Session() as session:
        tasks = get_tasks(session)

        for task in tasks:
            task.start()

            next_iteration = datetime.today() + timedelta(seconds=task.countdown)
            next_iteration = next_iteration.replace(microsecond=0)

            print(
                f"{bcolors.OKGREEN}INFO{bcolors.ENDC}:  "
                f"Task {bcolors.BOLD}{task.name}{bcolors.ENDC}"
                f" starts at: {bcolors.BOLD}{next_iteration}{bcolors.ENDC}"
            )
