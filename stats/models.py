from django.db import models
from uuid import uuid4

class User(models.Model):

    '''
    Stores anonymized information about a user.
    '''
    hashed_username = models.CharField(
        primary_key=True, max_length=40, blank=False)  # Use SHA-1

    def __unicode__(self):
        return "User: %s" % (self.hashed_username)

    class Meta:
        db_table = u'users'


class Machine(models.Model):

    '''
    Stores anonymized information about a machine.
    '''
    hashed_hostname = models.CharField(
        primary_key=True, max_length=40, null=False, blank=False)  # Use SHA-1
    platform = models.CharField(max_length=32, null=False, blank=True)
    platform_version = models.CharField(max_length=16, null=False, blank=True)

    def getPlatform(self):
        if self.platform_version not in [None, '']:
            return "%s v%s" % (self.platform, self.platform_version)
        else:
            return self.platform

    def __unicode__(self):
        return "Machine: %s - %s" % (self.platform, self.platform_version)

    class Meta:
        db_table = u'machines'


def get_or_make_user(username):
    try:
        user = User.objects.get(hashed_username=username)
    except User.DoesNotExist:
        user = User()
        user.hashed_username = username
        user.save()
    return user


def get_or_make_machine(platform, version, hostname):
    try:
        machine = Machine.objects.get(
            platform=platform,
            platform_version=version,
            hashed_hostname=hostname
        )
    except Machine.DoesNotExist:
        # Create a new machine matching this one
        machine = Machine()
        machine.platform = platform
        machine.platform_version = version
        machine.hashed_hostname = hostname
        machine.save()
    return machine


class NetInfo(models.Model):

    '''
    Stores anonymized information about a network end point, as determined by
    IP. (IP address anonymized by zerioing-out the last octet.)
    eg: 12.34.56.78 --> 12.34.56.0
    '''
    ip = models.GenericIPAddressField(
        primary_key=True, null=False, blank=False)
    latitude = models.DecimalField(
        max_digits=13, decimal_places=10, null=False)
    longitude = models.DecimalField(
        max_digits=13, decimal_places=10, null=False)
    country = models.CharField(max_length=2, null=False, blank=True)
    city = models.CharField(max_length=64, null=False, blank=True)
    domain = models.CharField(max_length=64, blank=True, null=False)
    organization = models.CharField(max_length=64, null=False, blank=True)

    def __unicode__(self):
        if self.latitude not in (None, '') and self.longitude not in (None, ''):
            return "%s @ %s  (%d, %d)" % (self.ip,
                                          self.domain,
                                          self.latitude,
                                          self.longitude)
        else:
            return "%s @ %s" % (self.ip, self.domain)

    class Meta:
        db_table = u'netinfo'


class Source(models.Model):

    '''
    Stores name and version of the program which submitted the log entry.
    '''
    id = models.AutoField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=16, blank=True, null=False)
    # use CharField for version number because sometimes versions have
    # multiple decimal places or letters (eg 2.3.2rc1)
    version = models.CharField(max_length=64, blank=True, null=False)

    def __unicode__(self):
        if self.version is not None and self.version != '':
            return "%s v%s" % (self.name, self.version)
        else:
            return "%s" % (self.name)

    class Meta:
        db_table = u'sources'
        unique_together = ("name", "version")


class Action(models.Model):

    '''
    Stores the action taken in the log event.
    This could be things like "Started UV-CDAT", "Error (FATAL)",
    or "Build successful"
    '''
    name = models.CharField(
        primary_key=True, max_length=64, blank=False, null=False)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = u'actions'


class Session(models.Model):
    user = models.ForeignKey(User, null=False, blank=True)
    machine = models.ForeignKey(Machine, null=False, blank=True)
    netInfo = models.ForeignKey(NetInfo, null=False, blank=True)
    startDate = models.DateTimeField()
    lastDate = models.DateTimeField()
    token = models.CharField(max_length=32)


def generate_session_token():
    return uuid4()



# log entries. time, user, location, action performed, etc...
class LogEvent(models.Model):

    '''
    The actual log.
    A LogEvent is a relation between users, machines, netInfos, sources, and
    actions that happened on a particular date at a particular time.
    '''
    id = models.AutoField(primary_key=True, null=False, blank=False)
    source = models.ForeignKey(Source, null=False, blank=True)
    action = models.ForeignKey(Action, null=False, blank=True)
    #session = models.ForeignKey(Session, null=True, blank=True, related_name="events")
    frequency = models.PositiveIntegerField()

    def __unicode__(self):
        return "%s by User %s in Session %s" % (self.action.name)
                                              #  self.session.user.hashed_username,
                                              #  self.session.token)

    class Meta:
        db_table = u'logevent'


# log error description, severity, stack trace, user comments, and execution
# log. I have no idea what an "execution log" is, so I'm going to assume it can
# be represented as a string
class Error(models.Model):

    '''
    Stores information related to errors. (severity, description, stack trace,
    etc)
    '''
    id = models.AutoField(primary_key=True, null=False, blank=False)
    logEvent = models.ForeignKey(
        LogEvent, unique=True, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    severity = models.CharField(max_length=8, null=False, blank=False)
    stackTrace = models.TextField(null=False, blank=True)
    userComments = models.TextField(null=False, blank=True)
    executionLog = models.TextField(null=False, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "ERROR: (%s) %s " % (self.severity, self.description[:50])

    class Meta:
        db_table = u'error'


