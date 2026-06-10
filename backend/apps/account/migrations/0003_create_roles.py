from django.db import migrations


# Сейчас роли создаем через команды (BaseCommands)
def create_roles(apps, schema_editor):
    UserRole = apps.get_model("account", "UserRole")
    roles = ["Сотрудник", "Администратор"]
    for role in roles:
        UserRole.objects.get_or_create(name=role)


def removes_roles(apps, schema_editor):
    UserRole = apps.get_model("account", "UserRole")
    UserRole.objects.filter(name__in=["Сотрудник", "Администратор"]).delete()


class Migration(migrations.Migration):
    dependencies = [("account", "0001_initial")]

    operations = [migrations.RunPython(create_roles, removes_roles)]
