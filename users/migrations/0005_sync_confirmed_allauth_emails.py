from django.db import migrations


def mark_custom_confirmed_emails(apps, schema_editor):
    Profile = apps.get_model('users', 'Profile')
    EmailAddress = apps.get_model('account', 'EmailAddress')
    database = schema_editor.connection.alias

    profiles = (
        Profile.objects.using(database)
        .filter(user__is_active=True, email_verification_sent_at__isnull=False)
        .select_related('user')
    )
    for profile in profiles.iterator():
        email = profile.user.email
        if not email:
            continue

        address, _ = EmailAddress.objects.using(database).get_or_create(
            user_id=profile.user_id,
            email=email,
            defaults={'verified': True, 'primary': True},
        )
        EmailAddress.objects.using(database).filter(
            user_id=profile.user_id,
            primary=True,
        ).exclude(pk=address.pk).update(primary=False)
        if not address.verified or not address.primary:
            address.verified = True
            address.primary = True
            address.save(using=database, update_fields=['verified', 'primary'])


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_emailaddress_unique_primary_email'),
        ('users', '0004_profile_email_verification'),
    ]

    operations = [
        migrations.RunPython(mark_custom_confirmed_emails, migrations.RunPython.noop),
    ]
