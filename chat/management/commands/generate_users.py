import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

class Command(BaseCommand):
    help = "Generate 500 fake users"

    def handle(self, *args, **kwargs):
        fake = Faker()
        users_created = 0

        for _ in range(500):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}_{last_name.lower()}{random.randint(100, 999)}"
            email = f"{username}@example.com"
            password = "password123" 
            

            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password
                )
                users_created += 1
        
        self.stdout.write(self.style.SUCCESS(f"Successfully created {users_created} fake users!"))
