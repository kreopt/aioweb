from orator.migrations import Migration


class CreateCrudTestsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('crud_tests') as table:
            table.increments('id')
            table.timestamps()
            table.string('wtf').nullable()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('crud_tests')
