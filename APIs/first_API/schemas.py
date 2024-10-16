from marshmallow import Schema, fields

# Plain Schemas
class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)
    
class PlainStoreSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    
class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

    
# Others
class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()
    
class ItemSchema(PlainItemSchema):
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    # many to many
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)
    
class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True )
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True )
    
class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    # many to many
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    
class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)
    
    
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(rquired=True)
    password = fields.Str(rquired=True, load_only=True) # load_only == Not returned value, only the client can send it