import math
import readtime
from django.db import models
from django_editorjs_fields import EditorJsJSONField
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
import os

class Category(models.Model):
    name = models.CharField(max_length=150)
    thumbnail = models.ImageField(upload_to='category_thumbnails', blank=True, null=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=150)
    profile_photo = models.ImageField(upload_to='profiles', blank=True, null=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    
    def path_for_blog_image(instance, filename):
        return 'blog_images/{0}/{1}'.format(instance.title, filename)
    id = models.AutoField(primary_key=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, related_name='blogs')
    title = models.CharField(max_length=150)
    short_desc = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=100)
    body = EditorJsJSONField(
        null=True,
        blank=True
    )
    view_count = models.PositiveIntegerField(default=0)
    tags = models.CharField(max_length=150, blank=True, null=True)
    mobile_image = models.ImageField(upload_to=path_for_blog_image, blank=True, null=True)
    desktop_image = models.ImageField(upload_to=path_for_blog_image, blank=True, null=True)
    published_at = models.DateField(auto_now_add=True)
    read_time = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_editor_choice = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField()

    def __str__(self):
        return self.title

    def clean(self):
        if Blog.objects.filter(sort_order=self.sort_order).exclude(id=self.id).exists():
            raise ValidationError("Sort Order already exists!")

    def save(self):
        if self.body:
            readtime_min = readtime.of_text(str(self.body), wpm=80)
            self.read_time = round(math.ceil(readtime_min.seconds / 60))
        super(Blog, self).save()

class Subscription(models.Model):
    email = models.EmailField(unique=True, max_length=255, help_text='Provide email')

    def __str__(self):
        return self.email