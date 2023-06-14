# pylint: skip-file


from core.db.enums import SwipeSessionActionEnum, WebsocketActionEnum

x = {
    SwipeSessionActionEnum.CONNECTION_CODE: "1",
    SwipeSessionActionEnum.GET_RECIPES: "2",
    SwipeSessionActionEnum.GLOBAL_MESSAGE: "3",
    SwipeSessionActionEnum.POOL_MESSAGE: "4",
}

print(x)

print()
print(x.get(WebsocketActionEnum.CONNECTION_CODE, "chicken"))
