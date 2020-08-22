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
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')
    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001,
                             open_commission=0.0003,
                             close_commission=0.0003,
                             min_commission=5),
                   type='stock')
    # 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
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


## 开盘前运行函数
def before_market_open(context):
    # 输出运行时间
    log.info('函数运行时间(before_market_open)：' + str(context.current_dt.time()))
    # 给微信发送消息（添加模拟交易，并绑定微信生效）
    send_message('美好的一天~')
    # 要操作的股票：云南白药（g.为全局变量）
    g.security = '000538.XSHE'


## 开盘时运行函数
def market_open(context):
    log.info('函数运行时间(market_open):' + str(context.current_dt.time()))
    security = g.security
    # 获取股票的收盘价
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
    #获得BOLL指标的上轨值、中轨值和下轨值
    upperband, middleband, lowerband = Bollinger_Bands(
        security,
        check_date=context.current_dt,
        timeperiod=20,
        nbdevup=2,
        nbdevdn=2)
    # 取得当前的现金
    cash = context.portfolio.available_cash
    # 如果上一时间点价格高出中轨值, 则全仓买入
    if ma_n1 > ma_n2 and ma_n2 > ma_n3 and current_price > middleband:
        # 记录这次买入
        log.info("收盘价站上BOLL指标中轨, 买入 %s" % (security))
        # 用所有 cash 买入股票
        order_value(security, cash)
    # 如果上一时间点价格低于五天平均价, 则空仓卖出
    elif ma_n1 > ma_n2 and ma_n2 > ma_n3 and current_price > upperband and context.portfolio.positions[
            security].closeable_amount > 0:
        # 记录这次卖出
        log.info("收盘价站上BOLL指标上轨, 卖出 %s" % (security))
        # 卖出所有股票,使这只股票的最终持有量为0
        order_target(security, 0)


## 收盘后运行函数
def after_market_close(context):
    log.info(
        str('函数运行时间(after_market_close):' + str(context.current_dt.time())))
    #得到当天所有成交记录
    trades = get_trades()
    for _trade in trades.values():
        log.info('成交记录：' + str(_trade))
    log.info('一天结束')


log.info('##############################################################')
