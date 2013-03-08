from django.db import models

# anonymized information about a user. 
class User(models.Model):
    id = models.AutoField(primary_key=True)
    hashed_username = models.CharField(max_length=40, blank=True) # Use SHA-1
    def __unicode__(self):
        return "User %s" % self.id
    class Meta:
        db_table = u'users'

# anonymized information about a machine. location, domain, region, etc
class Machine(models.Model):
    id = models.AutoField(primary_key=True)
    hashed_hostname = models.CharField(max_length=40, null=False, blank=False) # Use SHA-1
    platform = models.CharField(max_length=30, null=True, blank=True)
    platform_version = models.CharField(max_length=30, null=True, blank=True)
    def __unicode__(self):
        return "Machine %s - %s - %s" % (self.id, self.platform, self.platform_version)
    class Meta:
        db_table = u'machines'

# anonymized information gleaned from the IP address
class NetInfo(models.Model):
    # IP anonymized by zerio-ing out the last 2 octets. ie: '10.254.23.156' will be stored as '10.254.0.0'
    ip = models.GenericIPAddressField()
    latitude = models.DecimalField(max_digits=13, decimal_places=10, null=True)
    longitude = models.DecimalField(max_digits=13, decimal_places=10, null=True)
    country = models.CharField(max_length=2, null=True, blank=True)
    domain = models.CharField(max_length=50, blank=True, null=True)
    organization = models.CharField(max_length=50, null=True, blank=True)
    def __unicode__(self):
        if self.latitude != None and self.longitude != None:
            return "%s @ %s  (%d, %d)" % (self.ip, self.domain, self.latitude, self.longitude)
        else:
            return "%s @ %s" % (self.ip, self.domain)
    class Meta:
        db_table = u'netinfo'

# program submitting this log entry. 'cdat', 'uvcdat', 'search', etc...
class Source(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=12, blank=True, null=True)
    # use CharField for version number because sometimes versions have multiple decimal places or letters (eg 2.3.2rc1)
    version = models.CharField(max_length=10, blank=True, null=True)
    def __unicode__(self):
        if self.version != None and self.version != '':
            return "%s v%s" % (self.name, self.version)
        else:
            return "%s" % (self.name)
    class Meta:
        db_table = u'sources'

# action taken
class Action(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = u'actions'

# log entries. time, user, location, action performed, etc...
class LogEvent(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    machine = models.ForeignKey(Machine, null=True, blank=True)
    netInfo = models.ForeignKey(NetInfo, null=True, blank=True)
    source = models.ForeignKey(Source, null=True, blank=True)
    action = models.ForeignKey(Action, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    def __unicode__(self):
        return "%s by User %s at %s" % (self.action.name, self.user.id, self.date)

    class Meta:
        db_table = u'access'
