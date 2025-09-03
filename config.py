from flask_login import UserMixin
from peewee import SqliteDatabase, Model, IntegerField, CharField, TextField
 
db = SqliteDatabase("db.sqlite")
 
 

class User(UserMixin, Model):
     id = IntegerField(primary_key=True)
     name = CharField(unique=True)
     email = CharField(unique=True)
     password = TextField()
 
     class Meta:
         database = db
         table_name = "users"
 
class Item(UserMixin, Model):
     id = IntegerField(primary_key=True)
     item_name = CharField(unique=True)
     start_date = CharField(unique=True)
     end_date = CharField(unique=True)
     status = CharField(unique=True)
 
     class Meta:
         database = db
         table_name = "items"
          
db.create_tables([User])
db.create_tables([Item])
