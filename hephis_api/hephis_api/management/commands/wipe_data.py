from django.core.management.base import BaseCommand
from hephis_core.utils.eraser import delete_data_folder, delete_all

class Command(BaseCommand):

    help = "Safely deletes local data folders (music, recipes, all). Supports dry-run."

    def add_arguments(self, parser):
        parser.add_argument("target", choices=["music", "recipes", "all"])
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):

        target = options["target"]
        dry_run = options["dry_run"]

        # Run the correct deletion function
        if target == "music":
            result = delete_data_folder("music", dry_run)

        elif target == "recipes":
            result = delete_data_folder("recipes", dry_run)

        elif target == "all":
            result = delete_all(dry_run)

        # Print result nicely
        self.stdout.write(self.style.SUCCESS("=== WIPE RESULT ==="))
        for key, value in result.items():
            self.stdout.write(f"{key}: {value}")
