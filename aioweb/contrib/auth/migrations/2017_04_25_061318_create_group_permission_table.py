from orator.migrations import Migration


class CreateGroupPermissionTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('group_permissions') as table:
            table.integer('group_id').unsigned()
            table.foreign('group_id').references('id').on('groups')
            table.integer('permission_id').unsigned()
            table.foreign('permission_id').references('id').on('permissions').on_delete('cascade')
            table.primary(['group_id', 'permission_id'])

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('user_permissions')
