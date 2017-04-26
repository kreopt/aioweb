from orator.migrations import Migration


class CreateUserPermissionTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('user_permissions') as table:
            table.integer('user_id').unsigned()
            table.foreign('user_id').references('id').on('users')
            table.integer('permission_id').unsigned()
            table.foreign('permission_id').references('id').on('permissions').on_delete('cascade')
            table.primary(['user_id', 'permission_id'])

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('user_permissions')
