import jqdata
from jqlib.technical_analysis import *


def initialize(context):
    # 定义一个全局变量, 保存要操作的股票
    # 000001(股票:平安银行)
    g.security = '000001.XSHE'
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)


def handle_data(context, data):
    #获取初始化中要操作的股票
    security = g.security
    #调用MACD函数，并获取股票的MACD指标的DIF，DEA和MACD的值
    macd_diff, macd_dea, macd_macd = MACD(security,
                                          check_date=context.current_dt,
                                          SHORT=12,
                                          LONG=26,
                                          MID=9)
    # 取得当前的现金
    cash = context.portfolio.cash
    # 如果当前有余额，并且DIFF、DEA均为正，DIFF向上突破DEA
    if macd_diff > 0 and macd_dea > 0 and macd_diff > macd_dea:
        # 用所有 cash 买入股票
        order_value(security, cash)
        # 记录这次买入
        log.info("买入股票 %s" % (security))
    # 如果DIFF、DEA均为负，DIFF向下跌破DEA，并且目前有头寸
    elif macd_diff < 0 and macd_dea < 0 and macd_diff < macd_dea and context.portfolio.positions[
            security].closeable_amount > 0:
        # 全部卖出
        order_target(security, 0)
        # 记录这次卖出
        log.info("卖出股票 %s" % (security))
