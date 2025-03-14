from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

class Genre(models.Model):
    name = models.CharField('Оригінальна назва', max_length=100, unique=True)
    name_ukrainian = models.CharField('Українська назва', max_length=100, blank=True)
    description = models.TextField('Опис', blank=True)
    slug = models.SlugField(unique=True, blank=True, max_length=255)  # Increased length

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.name_ukrainian:
            return f"{self.name_ukrainian} ({self.name})"
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'

class DubbingStudio(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='dubbing_studios/', blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Студія дубляжу'
        verbose_name_plural = 'Студії дубляжу'

class Anime(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Онгоінг'),
        ('completed', 'Завершено'),
        ('announced', 'Анонсовано'),
        ('dropped', 'Покинуто'),
    ]
    
    TYPE_CHOICES = [
        ('tv', 'TV Серіал'),
        ('movie', 'Фільм'),
        ('ova', 'OVA'),
        ('ona', 'ONA'),
        ('special', 'Спешл'),
    ]
    
    SEASON_CHOICES = [
        ('winter', 'Зима'),
        ('spring', 'Весна'),
        ('summer', 'Літо'),
        ('fall', 'Осінь'),
    ]

    # Titles
    title_original = models.CharField('Оригінальна назва', max_length=255)
    title_english = models.CharField('Англійська назва', max_length=255, blank=True)
    title_japanese = models.CharField('Японська назва', max_length=255, blank=True)
    title_ukrainian = models.CharField('Українська назва', max_length=255)
    
    # Slugs and IDs
    slug = models.SlugField(unique=True, blank=True, max_length=255)  # Increased length
    mal_id = models.IntegerField('MyAnimeList ID', blank=True, null=True)
    
    # Details
    description = models.TextField('Опис')
    
    # Changed from ImageField to URLField
    poster_url = models.URLField('URL постера', max_length=500, blank=True)
    banner_url = models.URLField('URL банера', max_length=500, blank=True)
    
    # Keeping these for backward compatibility, but will be deprecated
    poster = models.ImageField(upload_to='anime/posters/', blank=True, null=True)
    banner = models.ImageField(upload_to='anime/banners/', blank=True, null=True)
    
    youtube_trailer = models.CharField('YouTube трейлер', max_length=255, blank=True)
    
    # Classification
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='ongoing')
    type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, default='tv')
    genres = models.ManyToManyField(Genre, related_name='anime', verbose_name='Жанри')
    
    # Metadata
    year = models.IntegerField('Рік виходу')
    season = models.CharField('Сезон', max_length=10, choices=SEASON_CHOICES, blank=True, null=True)
    episodes_count = models.IntegerField('Кількість епізодів', default=0)
    rating = models.FloatField('Рейтинг', validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    
    # Ukrainian specific
    dubbing_studios = models.ManyToManyField(DubbingStudio, related_name='anime', blank=True, verbose_name='Студії дубляжу')
    has_ukrainian_dub = models.BooleanField('Українська озвучка', default=False)
    ukrainian_release_date = models.DateField('Дата виходу українською', blank=True, null=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Add duration per episode field
    duration_per_episode = models.IntegerField('Тривалість епізоду (хв)', default=24)

    # Update tracking fields
    update_priority = models.IntegerField('Пріоритет оновлення', default=5, 
                                         validators=[MinValueValidator(1), MaxValueValidator(10)])
    last_full_update = models.DateTimeField('Останнє повне оновлення', null=True, blank=True)
    last_metadata_update = models.DateTimeField('Останнє оновлення метаданих', null=True, blank=True)
    last_episodes_update = models.DateTimeField('Останнє оновлення епізодів', null=True, blank=True)
    last_images_update = models.DateTimeField('Останнє оновлення зображень', null=True, blank=True)
    update_failures = models.IntegerField('Кількість невдалих спроб', default=0)
    next_update_scheduled = models.DateTimeField('Наступне оновлення', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # If migrating from old format to new, ensure poster_url contains a value
        if not hasattr(self, 'poster_url'):
            self.poster_url = ''
            
        if not hasattr(self, 'banner_url'):
            self.banner_url = ''
            
        # If we have a poster image but no URL, try to get URL from the image
        if not self.poster_url and self.poster and hasattr(self.poster, 'url'):
            self.poster_url = self.poster.url
            
        # If we have a banner image but no URL, try to get URL from the image
        if not self.banner_url and self.banner and hasattr(self.banner, 'url'):
            self.banner_url = self.banner.url
            
        # Fix for empty slug issue - ensure we always have a non-empty slug
        if not self.slug or self.slug.strip() == '':
            if self.title_ukrainian and self.title_ukrainian.strip():
                base_slug = slugify(self.title_ukrainian)
            elif self.title_english and self.title_english.strip():
                base_slug = slugify(self.title_english)
            elif self.title_original and self.title_original.strip():
                base_slug = slugify(self.title_original)
            else:
                # As a last resort, use the ID or a timestamp if this is a new record
                import time
                base_slug = f"anime-{int(time.time())}"
                
            # Ensure the slug is not too long (max 250 chars to be safe)
            if len(base_slug) > 250:
                base_slug = base_slug[:250]
                
            # Ensure the slug is unique by appending a counter if needed
            original_slug = base_slug
            counter = 1
            while Anime.objects.filter(slug=base_slug).exclude(pk=self.pk).exists():
                base_slug = f"{original_slug[:245]}-{counter}"
                counter += 1
                
            self.slug = base_slug

        # Update priority if it hasn't been set manually
        if self.update_priority == 5 and 'update_fields' not in kwargs:
            self.update_priority = self.calculate_update_priority()
            
        # Schedule next update if not already set
        if not self.next_update_scheduled and 'update_fields' not in kwargs:
            self.schedule_next_update()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_ukrainian
    
    # Добавляем специальный метод для отображения японского названия
    def get_japanese_title(self):
        """Return proper encoded Japanese title"""
        return self.title_japanese if self.title_japanese else ""

    def calculate_update_priority(self):
        """Calculate update priority based on anime characteristics"""
        base_priority = 5  # Default medium priority
        
        # Ongoing anime get higher priority
        if self.status == 'ongoing':
            base_priority += 3
        
        # Recently updated anime get lower priority
        if self.last_full_update:
            days_since_update = (timezone.now() - self.last_full_update).days
            if days_since_update < 7:
                base_priority -= 2
            elif days_since_update < 30:
                base_priority -= 1
        
        # New anime (without updates) get higher priority
        if not self.last_full_update:
            base_priority += 2
        
        # Anime with failures get lower priority to prevent API waste
        if self.update_failures > 3:
            base_priority -= 2
        
        # Clamp value between 1-10
        return max(1, min(10, base_priority))
    
    def schedule_next_update(self):
        """Schedule next update based on priority and status"""
        base_days = 30  # Default: once a month
        
        # Adjust based on status
        if self.status == 'ongoing':
            base_days = 1  # Daily for ongoing
        elif self.status == 'announced':
            base_days = 7  # Weekly for announced
        
        # Adjust for priority (higher priority = more frequent updates)
        priority_factor = (11 - self.update_priority) / 5  # 10->0.2, 5->1.2, 1->2
        days = int(base_days * priority_factor)
        
        # Set next update time
        self.next_update_scheduled = timezone.now() + datetime.timedelta(days=max(1, days))

    class Meta:
        ordering = ['-year', 'title_ukrainian']
        verbose_name = 'Аніме'
        verbose_name_plural = 'Аніме'

# Remove the Season model completely

class Episode(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='episodes')
    # Remove season field
    number = models.IntegerField('Номер епізоду')
    # Keep absolute_number for convenience
    absolute_number = models.IntegerField('Загальний номер', blank=True, null=True)
    title = models.CharField('Назва епізоду', max_length=255, blank=True)
    title_japanese = models.CharField('Японська назва епізоду', max_length=255, blank=True)
    title_romanji = models.CharField('Романізована назва епізоду', max_length=255, blank=True)
    description = models.TextField('Опис', blank=True)
    duration = models.IntegerField('Тривалість (хв)')
    
    # Add thumbnail URL field
    thumbnail_url = models.URLField('URL мініатюри', max_length=500, blank=True)
    thumbnail = models.ImageField(upload_to='episodes/thumbnails/', blank=True, null=True)
    
    # Video sources - using URLs to external resources instead of storing files
    video_url_1080p = models.URLField('Відео 1080p', blank=True)
    video_url_720p = models.URLField('Відео 720p', blank=True)
    video_url_480p = models.URLField('Відео 480p', blank=True)
    
    # Ukrainian specific
    dubbing_studio = models.ForeignKey(DubbingStudio, on_delete=models.SET_NULL, null=True, blank=True, related_name='dubbed_episodes')
    
    # Episode metadata
    is_filler = models.BooleanField('Філлер', default=False)
    is_recap = models.BooleanField('Рекап', default=False)
    score = models.FloatField('Оцінка', null=True, blank=True)
    
    # Release info
    release_date = models.DateField('Дата виходу', default=timezone.now)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # If migrating from old format to new
        if not hasattr(self, 'thumbnail_url'):
            self.thumbnail_url = ''
            
        # If we have a thumbnail image but no URL, try to get URL from the image
        if not self.thumbnail_url and self.thumbnail and hasattr(self.thumbnail, 'url'):
            self.thumbnail_url = self.thumbnail.url
        
        # No more season-related code here
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.anime.title_ukrainian} - Епізод {self.number}: {self.title}" if self.title else f"{self.anime.title_ukrainian} - Епізод {self.number}"
    
    def display_thumbnail(self):
        if self.thumbnail_url:
            return self.thumbnail_url
        elif self.thumbnail and hasattr(self.thumbnail, 'url'):
            return self.thumbnail.url
        return None
    
    class Meta:
        ordering = ['anime', 'number']
        verbose_name = 'Епізод'
        verbose_name_plural = 'Епізоди'
        unique_together = ['anime', 'number']

class AnimeScreenshot(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='screenshots')
    
    # Add URL field and keep image field for compatibility
    image_url = models.URLField('URL зображення', max_length=500, blank=True)
    image = models.ImageField(upload_to='anime/screenshots/', blank=True, null=True)
    
    description = models.CharField(max_length=255, blank=True)
    
    def save(self, *args, **kwargs):
        # If migrating from old format to new
        if not hasattr(self, 'image_url'):
            self.image_url = ''
            
        # If we have an image but no URL, try to get URL from the image
        if not self.image_url and self.image and hasattr(self.image, 'url'):
            self.image_url = self.image.url
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Скріншот для {self.anime.title_ukrainian}"
    
    def display_image(self):
        if self.image_url:
            return self.image_url
        elif self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None
    
    class Meta:
        verbose_name = 'Скріншот'
        verbose_name_plural = 'Скріншоти'

class UpdateStrategy(models.Model):
    """Configuration for update strategies"""
    name = models.CharField('Назва стратегії', max_length=100)
    description = models.TextField('Опис', blank=True)
    
    # API limits
    api_requests_per_minute = models.IntegerField('Запитів на хвилину', default=30)
    api_requests_per_day = models.IntegerField('Запитів на день', default=3000)
    
    # Update frequency settings
    ongoing_update_days = models.IntegerField('Днів між оновленнями для онгоінгів', default=1)
    announced_update_days = models.IntegerField('Днів між оновленнями для анонсів', default=7)
    completed_update_days = models.IntegerField('Днів між оновленнями для завершених', default=30)
    
    # Priority weights
    ongoing_priority = models.IntegerField('Пріоритет онгоінгів', default=8)
    popular_priority = models.IntegerField('Пріоритет популярних', default=7)
    recent_priority = models.IntegerField('Пріоритет недавніх', default=6)
    old_priority = models.IntegerField('Пріоритет старих', default=3)
    
    # Update batch sizes
    batch_size = models.IntegerField('Розмір пакету оновлень', default=20)
    
    is_active = models.BooleanField('Активна', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Ensure only one strategy is active
        if self.is_active:
            UpdateStrategy.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'Стратегія оновлення'
        verbose_name_plural = 'Стратегії оновлення'

class APIUsageStatistics(models.Model):
    """Track API usage statistics"""
    api_name = models.CharField('Назва API', max_length=50)
    requests_count = models.IntegerField('Кількість запитів', default=0)
    successful_requests = models.IntegerField('Успішні запити', default=0)
    failed_requests = models.IntegerField('Невдалі запити', default=0)
    last_request_at = models.DateTimeField('Останній запит', null=True)
    
    # Daily tracking
    daily_count = models.IntegerField('Запитів за день', default=0)
    daily_reset_at = models.DateTimeField('Скидання лічильника', default=timezone.now)
    
    # Rate limiting information
    is_rate_limited = models.BooleanField('Обмеження швидкості', default=False)
    rate_limited_until = models.DateTimeField('Обмеження діє до', null=True, blank=True)
    
    def __str__(self):
        return f"{self.api_name} - {self.requests_count} запитів"
    
    def increment(self, success=True):
        """Increment request counters"""
        self.requests_count += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Handle daily count
        if timezone.now().date() > self.daily_reset_at.date():
            self.daily_count = 1
            self.daily_reset_at = timezone.now()
        else:
            self.daily_count += 1
            
        self.last_request_at = timezone.now()
        self.save()
    
    def check_limits(self, strategy=None):
        """Check if API limits are exceeded"""
        if not strategy:
            strategy = UpdateStrategy.objects.filter(is_active=True).first()
            if not strategy:
                return False
                
        # Check daily limit
        if self.daily_count >= strategy.api_requests_per_day:
            self.is_rate_limited = True
            self.rate_limited_until = timezone.now().replace(hour=0, minute=0, second=0) + datetime.timedelta(days=1)
            self.save()
            return True
            
        # Check per-minute limit
        if self.last_request_at and (timezone.now() - self.last_request_at).seconds < 60:
            recent_count = APIRequestLog.objects.filter(
                api_name=self.api_name,
                created_at__gte=timezone.now() - datetime.timedelta(minutes=1)
            ).count()
            
            if recent_count >= strategy.api_requests_per_minute:
                self.is_rate_limited = True
                self.rate_limited_until = timezone.now() + datetime.timedelta(minutes=1)
                self.save()
                return True
                
        return False
    
    class Meta:
        verbose_name = 'Статистика використання API'
        verbose_name_plural = 'Статистика використання API'

class APIRequestLog(models.Model):
    """Detailed log of API requests"""
    api_name = models.CharField('Назва API', max_length=50)
    endpoint = models.CharField('Ендпоінт', max_length=255)
    parameters = models.JSONField('Параметри', null=True, blank=True)
    response_code = models.IntegerField('Код відповіді', null=True, blank=True)
    success = models.BooleanField('Успіх', default=False)
    error_message = models.TextField('Повідомлення про помилку', blank=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лог запитів API'
        verbose_name_plural = 'Логи запитів API'

class UpdateLog(models.Model):
    """Log of anime update operations"""
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='update_logs')
    update_type = models.CharField('Тип оновлення', max_length=50, choices=[
        ('full', 'Повне оновлення'),
        ('metadata', 'Метадані'),
        ('episodes', 'Епізоди'),
        ('images', 'Зображення')
    ])
    success = models.BooleanField('Успіх', default=False)
    error_message = models.TextField('Повідомлення про помилку', blank=True)
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Лог оновлень'
        verbose_name_plural = 'Логи оновлень'
