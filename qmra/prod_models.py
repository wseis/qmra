from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    action_flag = models.PositiveSmallIntegerField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Comparison(models.Model):

    class Meta:
        managed = False
        db_table = 'comparison'


class ComparisonRiskAssessment(models.Model):
    comparison = models.ForeignKey(Comparison, models.DO_NOTHING)
    riskassessment = models.ForeignKey('Riskassessment', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'comparison_risk_assessment'
        unique_together = (('comparison', 'riskassessment'),)


class Doseresponse(models.Model):
    bestfitmodel = models.CharField(max_length=250)
    k = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    alpha = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    n50 = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    hosttype = models.CharField(max_length=250)
    doseunits = models.CharField(max_length=250)
    route = models.CharField(max_length=250)
    response = models.CharField(max_length=250)
    pathogen = models.ForeignKey('Pathogen', models.DO_NOTHING)
    reference = models.ForeignKey('Reference', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'doseresponse'


class Exposure(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250)
    events_per_year = models.IntegerField()
    reference = models.ForeignKey('Reference', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    volume_per_event = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float

    class Meta:
        managed = False
        db_table = 'exposure'


class Guideline(models.Model):
    name = models.CharField(max_length=250)
    description = models.CharField(max_length=250)
    reference = models.ForeignKey('Reference', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'guideline'


class Health(models.Model):
    infection_to_illness = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    dalys_per_case = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    pathogen = models.ForeignKey('Pathogen', models.DO_NOTHING)
    reference = models.ForeignKey('Reference', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'health'


class Inflow(models.Model):
    min = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    max = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    mean = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    alpha = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    beta = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    distribution = models.CharField(max_length=64)
    pathogen_in_ref = models.CharField(max_length=200)
    notes = models.CharField(max_length=200)
    pathogen = models.ForeignKey('Pathogen', models.DO_NOTHING)
    reference = models.ForeignKey('Reference', models.DO_NOTHING)
    water_source = models.ForeignKey('Sourcewater', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'inflow'


class Logremoval(models.Model):
    min = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    max = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    mean = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    alpha = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    beta = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    distribution = models.CharField(max_length=64)
    pathogen_group = models.ForeignKey('Pathogengroup', models.DO_NOTHING)
    reference = models.ForeignKey('Reference', models.DO_NOTHING)
    treatment = models.ForeignKey('Treatment', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'logremoval'


class Pathogen(models.Model):
    pathogen = models.CharField(max_length=64)
    description = models.TextField()
    pathogen_group = models.ForeignKey('Pathogengroup', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'pathogen'


class Pathogengroup(models.Model):
    pathogen_group = models.CharField(max_length=64)
    description = models.TextField()

    class Meta:
        managed = False
        db_table = 'pathogengroup'


class Qa(models.Model):
    question = models.CharField(max_length=120)
    answer = models.TextField()

    class Meta:
        managed = False
        db_table = 'qa'


class Reference(models.Model):
    name = models.CharField(max_length=50)
    link = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'reference'


class Riskassessment(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    exposure = models.ForeignKey(Exposure, models.DO_NOTHING, blank=True, null=True)
    source = models.ForeignKey('Sourcewater', models.DO_NOTHING)
    user = models.ForeignKey('User', models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'riskassessment'


class RiskassessmentTreatment(models.Model):
    riskassessment = models.ForeignKey(Riskassessment, models.DO_NOTHING)
    treatment = models.ForeignKey('Treatment', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'riskassessment_treatment'
        unique_together = (('riskassessment', 'treatment'),)


class Sourcewater(models.Model):
    water_source_name = models.CharField(max_length=64)
    water_source_description = models.CharField(max_length=2000)
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'sourcewater'


class Text(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField()

    class Meta:
        managed = False
        db_table = 'text'


class Treatment(models.Model):
    name = models.CharField(max_length=64)
    group = models.CharField(max_length=64)
    category = models.CharField(max_length=64)
    description = models.TextField()
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'treatment'


class User(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user'


class UserGroups(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_groups'
        unique_together = (('user', 'group'),)


class UserUserPermissions(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_user_permissions'
        unique_together = (('user', 'permission'),)