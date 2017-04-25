from orator.migrations import Migration


class CreateGroupsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('groups') as table:
            table.increments('id')
            table.string('name', 50).unique()

            table.timestamps()


    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('groups')
