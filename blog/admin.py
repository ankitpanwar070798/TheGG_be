from django.contrib import admin
from blog.models import Blog, Author, Category, Subscription
from core.tasks import send_blog_notification

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Subscription)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # Only trigger for new blog uploads
            send_blog_notification(obj.title)
        super().save_model(request, obj, form, change)

    list_display = ['author', 'title', 'is_active']
    list_display_links = ['author', 'title']
    prepopulated_fields = {'title_slug': ('title', )}