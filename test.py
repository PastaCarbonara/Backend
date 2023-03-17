
import datetime
import json
import random
import time
import uuid


class Packet:
    def __init__(self) -> None:
        self.id = str(uuid.uuid4())
        self.time = round(time.time() * 1000)
        self.recipe_id = 1
        self.like = False


    def json(self):
        return json.dumps(self.__dict__)
    

p1 = Packet(str(uuid.uuid4()), str(uuid.uuid4()), {"message": "cheese", "anything": "idk"})
p2 = Packet(str(uuid.uuid4()), str(uuid.uuid4()), {"message": "cheese",})

print(p1.json())
print(p2.json())

print()
