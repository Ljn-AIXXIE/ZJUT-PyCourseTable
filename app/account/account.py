import json
import pickle
import os

from app.utils import check_dir, encrypt_password, _project_root


class Account:
    STORE_DIR: str = os.path.join(_project_root, 'app/store')

    storeName: str
    storeType: str

    _studentId: str
    _password: str
    _store: dict

    _type: str

    def __init__(self, storePath: str, studentId: str, password: str):
        self.storeName, self.storeType = storePath.split('.', maxsplit=1)
        self._studentId = studentId
        self._password = password
        self._store = {}
        return

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return iter(self._store)

    def __contains__(self, key):
        return key in self._store

    def __repr__(self):
        return f"{self.__class__.__name__}({self._store})"

    @property
    def studentId(self):
        return self._studentId
    @property
    def password(self):
        return self._password

    def crypto(self, exponent: str, modulus: str) -> str:
        return encrypt_password(self.password, exponent, modulus)

    def _to_dict(self):
        return {
            'storeName': self.storeName,
            'storeType': self.storeType,
            'studentId': self.studentId,
            'password': self.password,
            '_store': self._store
        }

    def to_pkl(self):
        check_dir(Account.STORE_DIR)
        with open(f'{Account.STORE_DIR}/{self.storeName}.pkl', 'wb') as file:
            pickle.dump(self, file)
    def to_json(self):
        check_dir(Account.STORE_DIR)
        with open(f'{Account.STORE_DIR}/{self.storeName}.json', 'w') as file:
            json.dump(self._to_dict(), file, indent=2)

    @classmethod
    def _from_dict(cls, data):
        store_name = data['storeName']
        store_type = data['storeType']
        student_id = data['studentId']
        password = data['password']
        account = cls(f'{store_name}.{store_type}', student_id, password)
        account._store = data.get('_store', {})
        return account

    def save(self):
        check_dir(Account.STORE_DIR)
        if self.storeType == 'pkl':
            with open(f'{Account.STORE_DIR}/{self.storeName}.{self.storeType}', 'wb') as file:
                pickle.dump(self, file)
        elif self.storeType == 'json':
            with open(f'{Account.STORE_DIR}/{self.storeName}.{self.storeType}', 'w') as file:
                json.dump(self._to_dict(), file, indent=2)

    @staticmethod
    def from_file(fileName: str):
        check_dir(Account.STORE_DIR)
        path = f'{Account.STORE_DIR}/{fileName}'
        if not os.path.exists(path):
            raise FileNotFoundError(f"JSON file {path} not found")

        if path.endswith('.pkl'):
            with open(path, 'rb') as file:
                return pickle.load(file)
        elif path.endswith('.json'):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Account._from_dict(data)
        return None

    @staticmethod
    def delete(fileName: str):
        check_dir(Account.STORE_DIR)
        path: str = f'{Account.STORE_DIR}/{fileName}'
        if not os.path.exists(path):
            raise FileNotFoundError(f"JSON file {path} not found")

        os.remove(path)