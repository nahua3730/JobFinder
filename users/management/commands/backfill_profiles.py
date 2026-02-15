from django.core.management.base import BaseCommand
from users.models import User, JobSeekerProfile, RecruiterProfile


class Command(BaseCommand):
    help = "Backfill role flags and ensure profiles exist for existing users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default=None,
            help="Only backfill a specific username (e.g., alaahelwa)."
        )

    def handle(self, *args, **options):
        username = options.get("username")

        qs = User.objects.all()
        if username:
            qs = qs.filter(username=username)

        if not qs.exists():
            self.stdout.write(self.style.ERROR("No matching users found."))
            return

        for u in qs:
            # --- Decide role if missing ---
            # If both are False, default them to job seeker (safe default).
            if not u.is_job_seeker and not u.is_recruiter:
                u.is_job_seeker = True
                u.is_recruiter = False
                u.save(update_fields=["is_job_seeker", "is_recruiter"])
                self.stdout.write(self.style.WARNING(
                    f"{u.username}: role flags were missing -> set as job seeker"
                ))

            # --- Ensure correct profile exists ---
            if u.is_job_seeker:
                JobSeekerProfile.objects.get_or_create(user=u)
                self.stdout.write(self.style.SUCCESS(
                    f"{u.username}: JobSeekerProfile ensured"
                ))

            if u.is_recruiter:
                RecruiterProfile.objects.get_or_create(
                    user=u,
                    defaults={"company_name": "Pending Company"}
                )
                self.stdout.write(self.style.SUCCESS(
                    f"{u.username}: RecruiterProfile ensured"
                ))

        self.stdout.write(self.style.SUCCESS("Backfill complete."))
