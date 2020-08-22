# 导入函数库
import jqdata
from jqlib.technical_analysis import *


# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001,
                             open_commission=0.0003,
                             close_commission=0.0003,
                             min_commission=5),
                   type='stock')
    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
    # 开盘前运行
    run_daily(before_market_open,
              time='before_open',
              reference_security='000300.XSHG')
    # 开盘时运行
    run_daily(market_open, time='open', reference_security='000300.XSHG')
    # 收盘后运行
    run_daily(after_market_close,
              time='after_close',
              reference_security='000300.XSHG')


def before_market_open(context):
    # 输出运行时间
    log.info('函数运行时间(before_market_open)：' + str(context.current_dt.time()))
    # 给微信发送消息
    send_message('美好的一天，祝您交易顺利！')
    # 要操作的股票：云南白药（g.为全局变量）
    g.security = '000538.XSHE'


def market_open(context):
    log.info('函数运行时间(market_open):' + str(context.current_dt.time()))
    security = g.security
    #调用KD函数，获取该函数的K值和D值
    K1, D1 = KD(security, check_date=context.current_dt, N=9, M1=3, M2=3)
    # 取得当前的现金
    cash = context.portfolio.available_cash
    # 如果K在20左右向上交叉D时, 则全仓买入
    if K1 >= 20 and K1 > D1:
        # 记录这次买入
        log.info("买入股票 %s" % (security))
        # 用所有 cash 买入股票
        order_value(security, cash)
    # 如果K在80左右向下交叉D，并且目前有头寸, 则全仓卖出
    elif K1 <= 80 and K1 < D1 and context.portfolio.positions[
            security].closeable_amount > 0:
        # 记录这次卖出
        log.info("卖出股票 %s" % (security))
        # 卖出所有股票,使这只股票的最终持有量为0
        order_target(security, 0)


def after_market_close(context):
    log.info(
        str('函数运行时间(after_market_close):' + str(context.current_dt.time())))
    #得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：' + str(_trade))
    log.info('一天的交易结束，祝你心情愉快！')
