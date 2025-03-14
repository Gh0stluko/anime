# Generated by Django 5.1.7 on 2025-03-09 13:37

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anime', '0007_genre_name_ukrainian_alter_genre_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIRequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(max_length=50, verbose_name='Назва API')),
                ('endpoint', models.CharField(max_length=255, verbose_name='Ендпоінт')),
                ('parameters', models.JSONField(blank=True, null=True, verbose_name='Параметри')),
                ('response_code', models.IntegerField(blank=True, null=True, verbose_name='Код відповіді')),
                ('success', models.BooleanField(default=False, verbose_name='Успіх')),
                ('error_message', models.TextField(blank=True, verbose_name='Повідомлення про помилку')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
            ],
            options={
                'verbose_name': 'Лог запитів API',
                'verbose_name_plural': 'Логи запитів API',
            },
        ),
        migrations.CreateModel(
            name='APIUsageStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_name', models.CharField(max_length=50, verbose_name='Назва API')),
                ('requests_count', models.IntegerField(default=0, verbose_name='Кількість запитів')),
                ('successful_requests', models.IntegerField(default=0, verbose_name='Успішні запити')),
                ('failed_requests', models.IntegerField(default=0, verbose_name='Невдалі запити')),
                ('last_request_at', models.DateTimeField(null=True, verbose_name='Останній запит')),
                ('daily_count', models.IntegerField(default=0, verbose_name='Запитів за день')),
                ('daily_reset_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Скидання лічильника')),
                ('is_rate_limited', models.BooleanField(default=False, verbose_name='Обмеження швидкості')),
                ('rate_limited_until', models.DateTimeField(blank=True, null=True, verbose_name='Обмеження діє до')),
            ],
            options={
                'verbose_name': 'Статистика використання API',
                'verbose_name_plural': 'Статистика використання API',
            },
        ),
        migrations.CreateModel(
            name='UpdateStrategy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Назва стратегії')),
                ('description', models.TextField(blank=True, verbose_name='Опис')),
                ('api_requests_per_minute', models.IntegerField(default=30, verbose_name='Запитів на хвилину')),
                ('api_requests_per_day', models.IntegerField(default=3000, verbose_name='Запитів на день')),
                ('ongoing_update_days', models.IntegerField(default=1, verbose_name='Днів між оновленнями для онгоінгів')),
                ('announced_update_days', models.IntegerField(default=7, verbose_name='Днів між оновленнями для анонсів')),
                ('completed_update_days', models.IntegerField(default=30, verbose_name='Днів між оновленнями для завершених')),
                ('ongoing_priority', models.IntegerField(default=8, verbose_name='Пріоритет онгоінгів')),
                ('popular_priority', models.IntegerField(default=7, verbose_name='Пріоритет популярних')),
                ('recent_priority', models.IntegerField(default=6, verbose_name='Пріоритет недавніх')),
                ('old_priority', models.IntegerField(default=3, verbose_name='Пріоритет старих')),
                ('batch_size', models.IntegerField(default=20, verbose_name='Розмір пакету оновлень')),
                ('is_active', models.BooleanField(default=False, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Стратегія оновлення',
                'verbose_name_plural': 'Стратегії оновлення',
            },
        ),
        migrations.AddField(
            model_name='anime',
            name='last_episodes_update',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Останнє оновлення епізодів'),
        ),
        migrations.AddField(
            model_name='anime',
            name='last_full_update',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Останнє повне оновлення'),
        ),
        migrations.AddField(
            model_name='anime',
            name='last_images_update',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Останнє оновлення зображень'),
        ),
        migrations.AddField(
            model_name='anime',
            name='last_metadata_update',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Останнє оновлення метаданих'),
        ),
        migrations.AddField(
            model_name='anime',
            name='next_update_scheduled',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Наступне оновлення'),
        ),
        migrations.AddField(
            model_name='anime',
            name='update_failures',
            field=models.IntegerField(default=0, verbose_name='Кількість невдалих спроб'),
        ),
        migrations.AddField(
            model_name='anime',
            name='update_priority',
            field=models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Пріоритет оновлення'),
        ),
        migrations.CreateModel(
            name='UpdateLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_type', models.CharField(choices=[('full', 'Повне оновлення'), ('metadata', 'Метадані'), ('episodes', 'Епізоди'), ('images', 'Зображення')], max_length=50, verbose_name='Тип оновлення')),
                ('success', models.BooleanField(default=False, verbose_name='Успіх')),
                ('error_message', models.TextField(blank=True, verbose_name='Повідомлення про помилку')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('anime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='update_logs', to='anime.anime')),
            ],
            options={
                'verbose_name': 'Лог оновлень',
                'verbose_name_plural': 'Логи оновлень',
            },
        ),
    ]
