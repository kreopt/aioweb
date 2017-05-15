from orator.migrations import Migration


class CreateUserGroupsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('user_groups') as table:
            table.integer('user_id').unsigned()
            table.integer('group_id').unsigned()
            table.boolean('active').default(False)
            table.boolean('is_default').default(False)

            table.foreign('user_id').references('id').on('users')
            table.foreign('group_id').references('id').on('groups').on_delete('cascade')
            table.primary(['user_id', 'group_id'])

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('user_groups')
