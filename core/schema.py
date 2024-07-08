import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from blog.models import Blog, Author, Category, Subscription
from graphql_relay import from_global_id
from graphql.error import GraphQLError
from django.db.models import Q
from django.core.validators import validate_email
from graphql_relay import to_global_id
import uuid 


class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        fields = ('id', 'name')
        interfaces = (relay.Node, )

    profile_pic = graphene.String()

    def resolve_profile_pic(self, info):
        if self.profile_photo:
            return info.context.build_absolute_uri(self.profile_photo.url)
        return None
    
class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ('id', 'name')
        interfaces = (relay.Node, )

    thumbnail = graphene.String()

    def resolve_thumbnail(self, info):
        if self.thumbnail:
            return self.thumbnail.url
        return None
    
class BlogType(DjangoObjectType):
    class Meta:
        model = Blog
        fields = (
            'id',
            'author',
            'categories',
            'tags',
            'short_desc',
            'title',
            'slug',
            'body',
            'published_at',
            'view_count',
            'read_time',
        )

    mobile_image = graphene.String()
    desktop_image = graphene.String()

    def resolve_id(self, info):
        return to_global_id('Blog', self.pk)

    def resolve_mobile_image(self, info):
        if self.mobile_image:
            return info.context.build_absolute_uri(self.mobile_image.url)
        return None
    
    def resolve_desktop_image(self, info):
        if self.desktop_image:
           return info.context.build_absolute_uri(self.desktop_image.url)
        return None
    
class BlogENUM(graphene.Enum):
    featured = 'featured'
    all = 'all'
    recent = 'recent'
    trending = 'trending'
    news = 'news'
    editor_choice = 'editor_choice'


class Query(graphene.ObjectType):
    get_blogs = graphene.List(BlogType, blog_type=BlogENUM(required=True), search_term=graphene.String())
    get_blog_by_id = graphene.Field(BlogType, blog_id=graphene.String(required=True))
    get_categories = graphene.List(CategoryType, search_term=graphene.String())
    get_blogs_by_category_id = graphene.List(BlogType, category_id=graphene.String(required=True), search_term=graphene.String())

    def resolve_get_blogs(self, info, blog_type, search_term=None):
        match blog_type:
            case 'featured':
                blogs = Blog.objects.filter(is_active=True, is_featured=True)
            case 'all':
                blogs = Blog.objects.filter(is_active=True)
            case 'recent':
                blogs = Blog.objects.filter(is_active=True).order_by('-published_at')[:4]
            case 'trending':
                blogs = Blog.objects.filter(is_active=True).order_by('-view_count')[:4]
            case 'news':
                blogs = Blog.objects.filter(is_active=True, categories__name='News')
            case 'editor_choice':
                blogs = Blog.objects.filter(is_active=True, is_editor_choice=True)
        if search_term:
            return blogs.filter(Q(title__icontains=search_term) | Q(tags__icontains=search_term))
        from core.tasks import send_blog_notification
        send_blog_notification('test')
        return blogs
    
    def resolve_get_blog_by_id(self, info, blog_id):
        blog_id = from_global_id(blog_id)[1]
        try:
            blog = Blog.objects.get(id=blog_id)
            blog.view_count += 1
            blog.save()
        except Blog.DoesNotExist:
            raise GraphQLError("Blog doesn't exists")
        return blog
    
    def resolve_get_categories(self, info, search_term=None):
        if search_term:
            return Category.objects.filter(name__icontains=search_term)
        return Category.objects.all()
    
    def resolve_get_blogs_by_category_id(self, info, category_id, search_term=None):
        category_id = from_global_id(category_id)[1]
        try:
            blogs = Blog.objects.filter(category=category_id)
        except Blog.DoesNotExist:
            raise GraphQLError('No blogs found in this category')
        if search_term:
            return blogs.filter(Q(title__icontains=search_term) | Q(tags__icontains=search_term))
        return blogs

class SubscribeMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)

    status = graphene.String()
    message = graphene.String()

    def mutate(self, info, email):
        validate_email(email)
        if Subscription.objects.filter(email=email).exists():
            raise GraphQLError("you've subscribed already")
        Subscription.objects.create(
            email=email
        )
        return SubscribeMutation(status='SUCCESS', message='Email subscription added successfully')

class Mutation(graphene.ObjectType):
    subscribe = SubscribeMutation.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)