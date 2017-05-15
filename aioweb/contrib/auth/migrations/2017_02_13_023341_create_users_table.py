from orator.migrations import Migration


class CreateUsersTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('users') as table:
            table.increments('id')
            table.string('email', 50).nullable().unique()
            table.string('phone', 50).nullable().unique()
            table.string('password', 512)

            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('users')
