import os
from app import current_app, db
from app.models import Role, User
from flask_script import Manager,Shell
from flask_migrate import Migrate, MigrateCommand

app = current_app('default')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app= app, db=db, User=User, Role=Role)
manager.add_command("shell",Shell(make_shell_context()))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

