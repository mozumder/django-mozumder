from django.db import models

    class Article(models.Model):
        cover_photo = models.ForeignKey('Photo', on_delete=models.CASCADE)
        headline = models.CharField(max_length=255)
        author = models.ForeignKey('Person', on_delete=models.CASCADE)
        body = models.TextField()

    class Person(models.Model):
        first_name = models.CharField(max_length=50)
        last_name = models.CharField(max_length=50)

    class Photo(models.Model):
        original = models.ForeignKey('Photo', related_name='original_file', on_delete=models.CASCADE)
        small = models.ForeignKey('Photo', related_name='small_file', on_delete=models.CASCADE)
        medium = models.ForeignKey('Photo', related_name='medium_file', on_delete=models.CASCADE)
        large = models.ForeignKey('Photo', related_name='large_file', on_delete=models.CASCADE)
        thumbnail = models.ForeignKey('Photo', related_name='thumbnail_file', on_delete=models.CASCADE)

    class ImageFile(models.Model):
        width = models.PositiveIntegerField()
        height = models.PositiveIntegerField()
        file = models.ImageField()
