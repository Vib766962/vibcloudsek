from django.db import models

# Create your models here.
class Usercache(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    userkey = models.CharField(db_column='Userkey', max_length=100)  # Field name made lowercase.
    limit = models.IntegerField(db_column='Limit')  # Field name made lowercase.
    hour_limit = models.IntegerField(db_column='Hour_Limit')
    class Meta:
        managed = True
        db_table = 'usercache'

class CacheTable(models.Model):
    cache_key = models.CharField(primary_key=True, max_length=255)
    value = models.TextField()
    expires = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'cache_table'
