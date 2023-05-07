import hashlib


def GetHashKey(text: str):
    """ 將用戶的資料加密"""
    hash_object = hashlib.sha256()
    hash_object.update(text.encode())
    return hash_object.hexdigest()


print(GetHashKey("a046829713"))