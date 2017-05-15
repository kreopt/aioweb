from orator.migrations import Migration


class CreateGroupsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('groups') as table:
            table.increments('id')
            table.string('name', 50).unique()
            table.integer('parent_id').nullable()

            table.timestamps()

            table.foreign('parent_id').references('id').on('groups').on_delete('restrict')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('groups')
