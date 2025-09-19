# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedSearch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='검색 조건 이름', max_length=100)),
                ('description', models.TextField(blank=True, help_text='검색 조건 설명')),
                ('search_params', models.JSONField(help_text='검색 파라미터 (JSON)')),
                ('is_public', models.BooleanField(default=False, help_text='공개 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_searches', to='auth.user')),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='savedsearch',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique_user_search_name'),
        ),
    ]

