from orator.migrations import Migration


class AcidTest(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table('shits') as table:
            self.integer("lsd_quality")
            for i in [1,1,2,3]:
              print(i)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table('shits') as table:
            pass
