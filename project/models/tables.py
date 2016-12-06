# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.



import datetime

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
db.define_table('steps_t',
                Field('user_email', default=auth.user.email if auth.user_id else None),
                Field('d0', 'integer', default=0),
                Field('d1', 'integer', default=0),
                Field('d2', 'integer', default=0),
                Field('d3', 'integer', default=0),
                Field('d4', 'integer', default=0),
                Field('d5', 'integer', default=0),
                Field('d6', 'integer', default=0),
                Field('week_total', 'integer', default=0),
                Field('lifetime', 'integer', default=0),
                Field('last_updated_day', 'integer'),
                Field('updated_on', 'datetime',
                      default=datetime.datetime.now(),
                      update=datetime.datetime.now() 
                ))

db.define_table('weight_t',
                Field('user_email', default=auth.user.email if auth.user_id else None),
                Field('weight', 'double'),
                Field('created_on', 'datetime', default=datetime.datetime.utcnow())
                )

db.define_table('user_t',
                Field('user_email', default=auth.user.email if auth.user_id else None),
                Field('image', 'blob'),
                Field('dob', 'date'),
                Field('sex', 'string'),
                Field('height', 'double'),
                Field('steps_target', 'integer'),
                Field('weight_target', 'double'),
                Field('weight', 'double'),
                Field('created_on', 'datetime', default=datetime.datetime.utcnow()),
                Field('updated_on', 'datetime', update=datetime.datetime.utcnow())
)

db.define_table('fitbit_user_t',
                Field('user_email', default=auth.user.email if auth.user_id else None),
                Field('fitbit_user_id', 'string'),
                Field('access_token', 'string'),
                Field('refresh_token', 'string'),
                Field('expires_at', 'double'),
)

db.define_table('friends_t',
                Field('user_email', default=auth.user.email if auth.user_id else None),
                Field('friend_email', 'string'),
                Field('accepted', 'boolean', default=False)
)

# I don't want to display the user email by default in all forms.
db.steps_t.user_email.readable = db.steps_t.user_email.writable = False
db.user_t.user_email.readable = db.user_t.user_email.writable = False
db.weight_t.user_email.readable = db.weight_t.user_email.writable = False

db.weight_t.created_on.readable = db.weight_t.created_on.writable = False
db.user_t.created_on.readable = db.user_t.created_on.writable = False
db.user_t.updated_on.readable = db.user_t.updated_on.writable = False


