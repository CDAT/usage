from django.db import models

# Create your models here.
class Domains(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    ip1 = models.IntegerField(null=True,blank=True)
    ip2 = models.IntegerField(null=True,blank=True)
    class Meta:
        db_table=u'domains'
        ordering = ['name']
 
class Machines(models.Model):
    id = models.AutoField(primary_key=True)
    md5 = models.CharField(max_length=32, blank=True,null=True)
    domain = models.ForeignKey(Domains,null=True,blank=True)
    platform = models.CharField(max_length=20, null=True, blank=True)
    class Meta:
        db_table = u'machines'

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    md5 = models.CharField(max_length=32, blank=True)
    machine = models.ForeignKey(Machines,null=True,blank=True)
    class Meta:
        db_table = u'users'

class Sources(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=8, blank=True, null=True)
    class Meta:
        db_table = u'sources'

class Actions(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=12, blank=True, null=True)
    class Meta:
        db_table = u'actions'

class Access(models.Model):
    user = models.ForeignKey(Users,null=True, blank=True)
    source = models.ForeignKey(Sources,null=True, blank=True)
    action = models.ForeignKey(Actions,null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = u'access'
    
    
   
    

