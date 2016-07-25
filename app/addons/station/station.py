# -*- coding:utf-8 -*-

from openerp.osv import fields,osv
from openerp import tools
from openerp.osv.orm import except_orm
from openerp.tools.translate import _

class station_baseinfo(osv.Model):
    _name = 'station.baseinfo'
    _description = 'Phone station base infomation'
    _order = 'create_date desc'

    _columns = {
        'name':fields.char(u'方案名称', size=128, required=True),
        'branch':fields.selection([
            (1,u'城一'),(2,u'城二'),(3,u'城三'),
            (4,u'顺义'),(5,u'怀柔'),(6,u'密云'),
            (7,u'平谷'),(8,u'延庆'),(4,u'昌平'),
            (4,u'大兴'),(4,u'˙通州'),(4,u'房山')
        ],u'分公司',required=True),
        'build_type':fields.selection([
            (1,u'新建2G'),(10,u'已有2G，新建3G、4G'),(11,u'已有3G，新建2G'),
            (12,u'已有3G，新建4G'),(13,u'已有3G，新建2G、4G'),(14,u'已有4G，新建2G'),
            (15,u'已有4G，新建3G'),(16,u'已有4G，新建2G、3G'),(17,u'已有2G、3G，新建4G'),
            (18,u'已有2G、4G，新建3G'),(19,u'已有3G、4G，新建2G'),(2,u'新建3G'),
            (20,u'微蜂窝系统扩容'),(3,u'新建4G'),(4,u'新建2G、3G'),
            (5,u'新建2G、4G'),(6,u'新建3G、4G'),(7,u'新建2G、3G、4G'),
            (8,u'已有2G，新建3G'),(9,u'已有2G，新建4G')
        ],u'建设类型',required=True),
        'design_unit':fields.selection([(1,u'中移北分')],u'设计单位',required=True),
        'designer':fields.char(u'设计人',size=128,required=True),
        'designer_phone':fields.integer(string='设计人电话',required=True),
        'building_name':fields.char(u'小区或建筑物名称', size=512, required=True),
        'building_count':fields.integer(string='楼宇数量',required=True),
        'review_type':fields.selection([(1,'审核方案'),(2,'审核需求')],u'送审类型',required=True),
        'longitude':fields.float(string=u'经度',digits=(12, 6),required=True),
        'latitude':fields.float(string=u'纬度',digits=(12,6),required=True),
        'singleDoubleRoom':fields.selection([(1,u'单支路'),(2,u'双支路')],u'单双路室分',required=True),
        'roomFeedWay':fields.selection([(1,u'新建单支路室分'),(2,u'新建双支路室分'),
                                        (3,u'信源馈入单支路'),(4,u'信源馈入双支路'),
                                        (5,u'单支路改造'),(6,u'双支路改造'),
                                        (7,u'利旧一路，新建一路')],u'室分馈入方式',required=True),
        # 'isExtraRoom':fields.boolean(u'如为居民楼，是否有室分外打',required=True),
        'isExtraRoom':fields.selection([(1,u'否'),(2,u'是')],u'如为居民楼，是否有室分外打',required=True),
        'notExtraRoomReason':fields.char(u'如无室分外打，请说明理由', size=512),
        # 'isModelTest':fields.boolean(u'是否模测',required=True),
        'isModelTest':fields.selection([(1,u'否'),(2,u'是')],u'是否模测',required=True),
        'notModelReason':fields.char(u'未模测原因', size=512),
        # 'isFollowBranch':fields.boolean(u'是否使用随走随分',required=True),
        'isFollowBranch':fields.selection([(1,u'否'),(2,u'是')],u'是否使用随走随分',required=True),
        'antennaCount':fields.integer(string=u'天线数量',required=True),
        # 'isAntennaHome':fields.boolean(u'天线点是否入户覆盖',required=True),
        'isAntennaHome':fields.selection([(1,u'否'),(2,u'是')],u'天线点是否入户覆盖',required=True),
        'coverType':fields.selection([(1,u'MDAS覆盖'),(2,u'室内覆盖'),(3,u'小区覆盖')],u'类型',required=True),
        'coverFunctionType':fields.selection([
            (1,u'办公区'),(10,u'宾馆饭店'),(11,u'商住'),(12,u'住宅楼'),
            (13,u'地下停车场'),(14,u'电梯井道'),(2,u'居民区'),
            (3,u'餐饮场所'),(4,u'娱乐场所'),(5,u'商场'),
            (6,u'医院'),(7,u'学校'),(8,u'体育场馆'),(9,u'展览中心')
        ],u'覆盖功能类型',required=True),
        # 'isSuspendedCeiling':fields.boolean(u'是否有吊顶',required=True),
        'isSuspendedCeiling':fields.selection([(1,u'否'),(2,u'是')],u'是否有吊顶',required=True),
        'coveringArea':fields.float(string='覆盖面积（平米）',required=True),
        'notCoverageAreaExplain':fields.char(u'未覆盖区域说明', size=512, required=True),
        'buildArea':fields.float(string=u'建筑面积（平米）',required=True),
        'casingLength':fields.float(string=u'使用套管长度（米）',required=True),

        'demand2G':fields.char(u'2G需求号', size=128),
        'manufactor2G':fields.selection([(1,u'诺西'),(2,u'华为'),(3,u'中兴')],u'2G厂家'),
        'partitionCount2G':fields.integer(string='2G分区说明'),
        'partitionExplain2G':fields.char(u'2G分区说明', size=512),
        'config2G':fields.char(u'2G配置', size=512),
        'BBUCount2G':fields.integer(string='2G BBU数'),
        'BBUPosition2G':fields.char(u'2G BBU位置', size=512),
        'RRUCount2G':fields.integer(string='2G RRU数'),
        'RRUPosition2G':fields.char(u'2G RRU位置', size=512),

        'demand3G':fields.char(u'3G需求号', size=128),
        'manufactor3G':fields.selection([(1,u'诺西'),(2,u'华为'),(3,u'中兴')],u'3G厂家'),
        'partitionCount3G':fields.integer(string='3G分区说明'),
        'partitionExplain3G':fields.char(u'3G分区说明', size=512),
        'config3G':fields.char(u'3G配置', size=512),
        'BBUCount3G':fields.integer(string='3G BBU数'),
        'BBUPosition3G':fields.char(u'3G BBU位置', size=512),
        'RRUCount3G':fields.integer(string='3G RRU数'),
        'RRUPosition3G':fields.char(u'3G RRU位置', size=512),

        'demand4G':fields.char(u'4G需求号', size=128),
        'manufactor4G':fields.selection([(1,u'诺西'),(2,u'华为'),(3,u'中兴')],u'4G厂家'),
        'partitionCount4G':fields.integer(string='4G分区说明'),
        'partitionExplain4G':fields.char(u'4G分区说明', size=512),
        'config4G':fields.char(u'4G配置', size=512),
        'BBUCount4G':fields.integer(string='4G BBU数'),
        'BBUPosition4G':fields.char(u'4G BBU位置', size=512),
        'RRUCount4G':fields.integer(string='4G RRU数'),
        'RRUPosition4G':fields.char(u'4G RRU位置', size=512),

        'detailedAddress':fields.char(u'详细地址', size=1024, required=True),
        'remarks':fields.text(u'备注')

    }
