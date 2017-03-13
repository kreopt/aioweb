from orator.migrations import Migration


class CreateUsersTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('users') as table:
            table.increments('id')
            table.timestamps()
            table.string('username', 50).unique()
            table.string('password', 256)
            table.string('email', 50).unique()
            table.boolean('disabled').default(False)
            table.boolean('is_superuser').default(False)
            table.boolean('is_staff').default(False)


    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('users')
