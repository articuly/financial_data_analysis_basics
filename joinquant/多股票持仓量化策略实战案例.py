# 导入函数库
import jqdata
from jqlib.technical_analysis import *


def initialize(context):
    # 设置我们要操作的股票池
    g.stocks = ['000001.XSHE', '000002.XSHE', '000004.XSHE', '000005.XSHE']
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)


def handle_data(context, data):
    # 循环每只股票
    for security in g.stocks:
        # 得到股票之前5天的平均价
        vwap = data[security].vwap(5)
        # 得到上一时间点股票平均价
        price = data[security].close
        # 得到当前资金余额
        cash = context.portfolio.cash
        # 如果上一时间点价格小于5天平均价×0.996，并且持有该股票，卖出
        if price < vwap * 0.996 and context.portfolio.positions[
                security].closeable_amount > 0:
            # 下入卖出单
            order(security, -500)
            # 记录这次卖出
            log.info("卖出股票 %s" % (security))
        # 如果上一时间点价格大于5天平均价×1.008，并且有现金余额，买入
        elif price > vwap * 1.008 and cash > 0:
            # 下入买入单
            order(security, 500)
            # 记录这次买入
            log.info("买入股票 %s" % (security))
