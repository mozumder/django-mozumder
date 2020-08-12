from django.utils.translation import gettext_lazy as _
from django.db import models

default_app_config = 'mozumder.apps.MozumderAppConfig'

UNKNOWN = '0'
GET = '1'
HEAD = '2'
POST = '3'
PUT = '4'
DELETE = '5'
CONNECT = '6'
OPTIONS = '7'
TRACE = '8'
PATCH = '9'
METHOD_CHOICES = (
    (UNKNOWN, 'UNKNOWN'),
    (GET, 'GET'),
    (HEAD, 'HEAD'),
    (POST, 'POST'),
    (PUT, 'PUT'),
    (DELETE, 'DELETE'),
    (CONNECT, 'CONNECT'),
    (OPTIONS, 'OPTIONS'),
    (TRACE, 'TRACE'),
    (PATCH, 'PATCH'),
)
METHOD_CHOICES_LOOKUP = dict([i[1],i[0]] for i in METHOD_CHOICES)
METHOD_CHOICES_DICT = dict(METHOD_CHOICES)

UNCOMPRESSED = '0'
GZIP = '1'
SDCH = '2'
BROTLI = '3'
DEFLATE = '4'
ZSTD = '5'
COMPRESSION_CHOICES = (
    (UNCOMPRESSED, 'None'),
    (GZIP, 'gzip'),
    (SDCH, 'SDCH'),
    (BROTLI, 'Brotli'),
    (DEFLATE, 'deflate'),
    (ZSTD, 'Zstd'),
)
COMPRESSION_CHOICES_LOOKUP = dict([i[1],i[0]] for i in COMPRESSION_CHOICES)
COMPRESSION_CHOICES_DICT = dict(COMPRESSION_CHOICES)

HTTP09 = '9'
HTTP1 = '1'
HTTP11 = '2'
HTTP2 = '3'
HTTP3 = '3'
PROTOCOL_CHOICES = (
    (UNKNOWN, 'Unknown'),
    (HTTP09, 'HTTP/1.0'),
    (HTTP1, 'HTTP/1.0'),
    (HTTP11, 'HTTP/1.1'),
    (HTTP2, 'HTTP/2'),
    (HTTP3, 'HTTP/3'),
)
PROTOCOL_CHOICES_LOOKUP = dict([i[1],i[0]] for i in PROTOCOL_CHOICES)
PROTOCOL_CHOICES_DICT = dict(PROTOCOL_CHOICES)

BLACK = '#000'
RED = '#dd4646'
GREEN = '#70bf2b'
BLUE = '#1C00CF'
YELLOW = '#D3CB51'
PURPLE = '#AA0D91'
ORANGE = '#FBAC4C'
GRAY = '#7E7E7E'
LIGHTGRAY = '#A8A8A8'

class FieldTypes(models.TextChoices):
    AUTOFIELD = '01', _('AutoField')
    BIGAUTOFIELD = '02', _('BigAutoField')
    BIGINTEGERFIELD = '03', _('BigIntegerField')
    BINARYFIELD = '04', _('BinaryField')
    BOOLEANFIELD = '05', _('BooleanField')
    CHARFIELD = '06', _('CharField')
    DATEFIELD = '07', _('DateField')
    DATETIMEFIELD = '08', _('DateTimeField')
    DECIMALFIELD = '09', _('DecimalField')
    DURATIONFIELD = '10', _('DurationField')
    EMAILFIELD = '11', _('EmailField')
    FILEFIELD = '12', _('FileField')
    FILEPATHFIELD = '13', _('FilePathField')
    FLOATFIELD = '14', _('FloatField')
    IMAGEFIELD = '15', _('ImageField')
    INTEGERFIELD = '16', _('IntegerField')
    GENERICIPADDRESSFIELD = '17', _('GenericIpAddressField')
    NULLBOOLEANFIELD = '18', _('NullBooleanField')
    POSITIVEINTEGERFIELD = '19', _('PositiveIntegerField')
    POSITIVESMALLINTEGERFIELD = '20', _('PositiveSmallIntegerField')
    SLUGFIELD = '21', _('SlugField')
    SMALLAUTOFIELD = '22', _('SmallAutoField')
    SMALLINTEGERFIELD = '23', _('SmallIntegerField')
    TEXTFIELD = '24', _('TextField')
    URLFIELD = '25', _('URLField')
    UUIDFIELD = '26', _('UUIDField')
    FOREIGNKEY = '27', _('ForeignKey')
    MANYTOMANYFIELD = '28', _('ManyToManyField')
    ONETOONEFIELD = '29', _('OneToOneField')
    ARRAYFIELD = '30', _('ArrayField')
    CITEXTFIELD = '31', _('CIText')
    HSTOREFIELD = '32', _('HStoreField')
    JSONFIELD = '33', _('JSONField')
    INTEGERRANGEFIELD = '34', _('IntegerRangeField')
    BIGINTEGERRANGEFIELD = '35', _('BigIntegerRangeField')
    DECIMALRANGEFIELD = '36', _('DecimalRangeField')
    FLOATRANGEFIELD = '37', _('FloatRangeField')
    DATETIMERANGEFIELD = '38', _('DateTimeRangeField')
    DATERANGEFIELD = '39', _('DateRangeField')

class OnDelete(models.TextChoices):
    CASCADE = '01', _('CASCADE')
    PROTECT = '02', _('PROTECT')
    SETNULL = '03', _('SET_NULL')
    SETDEFAULT = '04', _('SET_DEFAULT')
    SET = '05', _('SET')
    DO_NOTHING = '06', _('DO_NOTHING')

class ConstraintType(models.TextChoices):
    CHECKCONSTRAINT = '01', _('CheckConstraint')
    UNIQUECONSTRAINT = '02', _('UniqueContraint')

class IPAddressProtocol(models.TextChoices):
    BOTH = '01', _('both')
    IPV4 = '02', _('IPv4')
    IPV6 = '03', _('IPv6')

class ViewBaseClass(models.TextChoices):
    FUNCTION = '00', _('None')
    VIEW = '01', _('View')
    TEMPLATEVIEW = '02', _('TempalateView')
    REDIRECTVIEW = '03', _('RedirectView')
    DETAILVIEW = '04', _('DetailView')
    BASEDETAILVIEW = '05', _('BaseDetailView')
    LISTVIEW = '06', _('ListView')
    BASELISTVIEW = '07', _('BaseListView')
    FORMVIEW = '08', _('FormView')
    BASEFORMVIEW = '09', _('BaseFormView')
    PROCESSFORMVIEW = '10', _('ProcessFormView')
    CREATEVIEW = '11', _('CreateView')
    BASECREATEVIEW = '12', _('BaseCreateView')
    UPDATEVIEW = '13', _('UpdateView')
    BASEUPDATEVIEW = '14', _('BaseUpdateView')
    DELETEVIEW = '15', _('DeleteView')
    BASEDELETEVIEW = '16', _('BaseDeleteView')
    ARCHIVEINDEXVIEW = '17', _('ArchiveIndexView')
    BASEARCHIVEINDEXVIEW = '18', _('BaseArchiveIndexView')
    BASEDATELISTVIEW = '19', _('BaseDateListView')
    YEARARCHIVEVIEW = '20', _('YearArchiveView')
    BASEYEARARCHIVEVIEW = '21', _('BaseYearArchiveView')
    MONTHARCHIVEVIEW = '22', _('MonthArchiveView')
    BASEMONTHARCHIVEVIEW = '23', _('BaseMonthArchiveView')
    WEEKARCHIVEVIEW = '24', _('WeekArchiveView')
    BASEWEEKARCHIVEVIEW = '25', _('BaseWeekArchiveView')
    DAYARCHIVEVIEW = '26', _('DayArchiveView')
    BASEDAYARCHIVEVIEW = '27', _('BaseDayArchiveView')
    TODAYARCHIVEVIEW = '28', _('TodayArchiveView')
    BASETODAYARCHIVEVIEW = '29', _('BaseTodayArchiveView')
    DATEDETAILVIEW = '30', _('DateDetailView')
    BASEDATEDETAILVIEW = '31', _('BaseDateDetailView')

class DefaultMixins(models.TextChoices):
    CONTEXTMIXIN = '01', _('ContextMixin')
    TEMPLATERESPONSEMIXIN = '02', _('TemplateResponseMixin')
    SINGLEOBJECTMIXIN = '03', _('SingleObjectMixin')
    SINGLEOBJECTTEMPLATERESPONSEMIXIN = '04', _('SingleObjectTemplateResponseMixin')
    MULTIPLEOBJECTMIXIN = '05', _('MultipleObjectMixin')
    MULTIPLEOBJECTTEMPLATERESPONSEMIXIN = '06', _('MultipleObjectTemplateResponseMixin')
    FORMMIXIN = '07', _('FormMixin')
    MODELFORMMIXIN = '08', _('ModelFormMixin')
    DELETIONMIXIN = '09', _('DeletionMixin')
    YEARMIXIN = '10', _('YearMixin')
    MONTHMIXIN = '11', _('MonthMixin')
    DAYMIXIN = '12', _('DayMixin')
    WEEKMIXIN = '13', _('WeekMixin')
    DATEMIXIN = '14', _('DateMixin')
