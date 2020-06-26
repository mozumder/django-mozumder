from django.db import models

class Collection(models.Model):
    cover_photo = models.ForeignKey('Photo', related_name='cover_photo', on_delete=models.CASCADE)
    social_photo = models.ForeignKey('Photo', related_name='social_photo', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    author = models.ForeignKey('Person', on_delete=models.CASCADE)
    description = models.TextField()
    album = models.ForeignKey('Album', on_delete=models.CASCADE)
    season = models.ForeignKey('Season', on_delete=models.CASCADE)
    rating = models.SmallIntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_published = models.DateTimeField(null=True, blank=True,db_index=True,)
    date_modified = models.DateTimeField(auto_now=True)
    date_expired = models.DateTimeField(null=True, blank=True,db_index=True,)
    date_deleted = models.DateTimeField(null=True, blank=True,db_index=True,)

class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

class Brand(models.Model):
    name = models.CharField(max_length=50)

class Season(models.Model):
    name = models.CharField(max_length=50)

class Album(models.Model):
    looks = models.ManyToManyField('Look')

class Look(models.Model):
    view = models.OneToManyField('View')
    name = models.CharField(max_length=50)
    rating = models.SmallIntegerField(default=0)
    
class View(models.Model):
    photo = models.ForeignKey('Photo', on_delete=models.CASCADE)
    type = models.ForeignKey('ViewTypes', on_delete=models.CASCADE)

class ViewTypes(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=2)

class Photo(models.Model):
    original = models.ForeignKey('Photo', related_name='original_file', on_delete=models.CASCADE)
    small = models.ForeignKey('Photo', related_name='small_file', on_delete=models.CASCADE)
    medium = models.ForeignKey('Photo', related_name='medium_file', on_delete=models.CASCADE)
    large = models.ForeignKey('Photo', related_name='large_file', on_delete=models.CASCADE)
    thumbnail = models.ForeignKey('Photo', related_name='thumbnail_file', on_delete=models.CASCADE)

class Image(models.Model):
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    file = models.ImageField()
