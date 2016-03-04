"""from rest_framework import serializers

from .models import User, Post, Photo


class UserSerializer(serializers.ModelSerializer):
    posts = serializers.HyperlinkedIdentityField('posts',  lookup_field='username') #view_name='userpost-list',

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'posts', )


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    photos = serializers.HyperlinkedIdentityField('photos', view_name='postphoto-list')
    # author = serializers.HyperlinkedRelatedField(view_name='user-detail', lookup_field='username')

    def get_validation_exclusions(self):
        # Need to exclude `author` since we'll add that later based off the request
        exclusions = super(PostSerializer, self).get_validation_exclusions()
        return exclusions + ['author']

    class Meta:
        model = Post


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.Field('image.url')

    class Meta:
        model = Photo
"""