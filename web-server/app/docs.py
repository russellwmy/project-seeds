import pymongo
import inspect

conn = pymongo.MongoClient()
db = conn[settings.DB_NAME]

FIELD_TYPES = [dict, int, str, list]

def is_bound_method(obj):
    return hasattr(obj, '__self__') and obj.__self__ is not None

def is_fields(obj, attr):
    attr_obj = getattr(obj, attr, None)
    if attr.startswith('__'):
        return False

    for t in FIELD_TYPES:
        if type(attr_obj) is t:
            return True
    return False

class Base:
    __collection__ = None
    def __init__(self, data={}):
        if self.__collection__ is None:
            self.__collection__ = self.__class__.__name__.lower()
        global db
        self.__db__ = db 
        self.id = None

        for k,v in data.items():
            if k =='_id': k = 'id'
            setattr(self, k, v)

    def save(self, upsert=False, multi=False):
        data = {}
        attrs = [(attr , getattr(self,attr, None)) for attr in dir(self) if is_fields(self, attr)]
        for k, v in attrs:
            if k != 'id':
                data[k] = v
        if self.id is not None:

            self.__db__[self.__collection__].update  (
                                                {'_id':self.id},
                                                {'$set':data},
                                                upsert=upsert,
                                                multi=multi
                                            )
        else:
            self.__db__[self.__collection__].insert(data)

    def remove(self):
        if self.id is not None:
            self.__db__[self.__collection__].remove({"_id":self.id})

    @classmethod
    def find(cls, query={}, projection=None):
        resultset = []
        result =  db[cls.__collection__].find(query, projection)
        for record in result:
            d = cls(record)
            resultset.append(d)
        return resultset
