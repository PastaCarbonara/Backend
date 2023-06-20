from sqlalchemy import and_, select
from core.db.models import File
from core.tasks.base_task import BaseTask
import asyncio
from datetime import datetime, timedelta
from app.image.interface import AzureBlobInterface
from azure.core.exceptions import ResourceNotFoundError

SIZES = ["thumbnail", "sm", "md", "lg", "xs"]


class Task(BaseTask):
    def __init__(self, session, capture_exceptions) -> None:
        self.azure_blob_interface = AzureBlobInterface()
        name = "Remove unused images from Azure Blob Storage"
        super().__init__(session, capture_exceptions, name)

    @property
    def countdown(self):
        # Everyday at 01:15:00
        x = datetime.today()
        y = x.replace(day=x.day, hour=1, minute=15, second=0, microsecond=0)
        if x > y:
            y += timedelta(days=1)

        delta_t = y - x
        return delta_t.total_seconds()

    def exec(self) -> None:
        # check if files are referenced in recipe, group, user if not delete from database and blob storage

        query = select(File).where(
            and_(File.group == None, File.recipe == None, File.user == None)
        )
        files_not_referenced = self.session.execute(query).scalars().all()
        for file in files_not_referenced:
            # delete from blob storage
            for size in SIZES:
                filename = file.filename.split(".")[0] + "-" + size + ".webp"
                try:
                    asyncio.run(self.azure_blob_interface.delete_image(filename))
                except ResourceNotFoundError as e:
                    print("has already been deleted from blob storage")
                # delete from database
            self.session.delete(file)

        self.session.commit()
