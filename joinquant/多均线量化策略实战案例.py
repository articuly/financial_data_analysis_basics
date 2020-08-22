# 导入函数库
import jqdata
from jqlib.technical_analysis import *


def initialize(context):
    # 定义一个全局变量, 保存要操作的股票
    # 000538(股票:云南白药)
    g.security = '000538.XSHE'
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # True为开启动态复权模式，使用真实价格交易
    set_option('use_real_price', True)
    # 设定成交量比例
    set_option('order_volume_ratio', 1)
    # 股票类交易手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
                             open_commission=0.0003, close_commission=0.0003,\
                             close_today_commission=0, min_commission=5), type='stock')
    # 运行函数
    run_daily(trade, 'every_bar')


def trade(context):
    security = g.security
    # 设定均线
    n1 = 5
    n2 = 10
    n3 = 30
    # 获取股票的收盘价
    close_data = attribute_history(security, n3 + 2, '1d', ['close'], df=False)
    # 取得过去 ma_n1 天的平均价格
    ma_n1 = close_data['close'][-n1:].mean()
    # 取得过去 ma_n2 天的平均价格
    ma_n2 = close_data['close'][-n2:].mean()
    # 取得过去 ma_n3 天的平均价格
    ma_n3 = close_data['close'][-n3:].mean()
    # 取得上一时间点价格
    current_price = close_data['close'][-1]
    # 取得当前的现金
    cash = context.portfolio.cash
    # 如果当前有余额，并且n1日均线大于n2日均线,n2日均线大于n3日均线,上一时间点价格高出五天平均价1%, 则全仓买入
    if ma_n1 > ma_n2 and ma_n2 > ma_n3 and current_price > 1.01 * ma_n1:
        # 用所有 cash 买入股票
        order_value(security, cash)
        # 记录这次买入
        log.info("Buying %s" % (security))
    # 如果n1日均线小于n2日均线，n2日均线小于n3日均线, 上一时间点价格低于五天平均价1%，并且目前有头寸
    elif ma_n1 < ma_n2 and ma_n2 < ma_n3 and current_price < 0.99 * ma_n1 and context.portfolio.positions[
            security].closeable_amount > 0:
        # 全部卖出
        order_target(security, 0)
        # 记录这次卖出
        log.info("Selling %s" % (security))
