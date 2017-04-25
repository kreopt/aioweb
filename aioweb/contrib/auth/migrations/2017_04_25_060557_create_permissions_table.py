from orator.migrations import Migration


class CreatePermissionsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('permissions') as table:
            table.increments('id')
            table.string('name', 50).unique()

            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('permissions')
