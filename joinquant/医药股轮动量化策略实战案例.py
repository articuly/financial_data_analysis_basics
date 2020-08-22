# 导入函数库
import jqdata


## 初始化函数，设定要操作的股票、基准等等
def initialize(context):
    # 设定沪深300医药指数作为基准
    set_benchmark('000931.XSHG')
    # True为开启动态复权模式，使用真实价格交易
    set_option('use_real_price', True)
    # 设定成交量比例
    set_option('order_volume_ratio', 1)
    # 股票类交易手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, \
                             open_commission=0.0003, close_commission=0.0003,\
                             close_today_commission=0, min_commission=5), type='stock')
    # 运行函数, 按周运行，在每周第一个交易日运行
    run_weekly(chenk_stocks, weekday=1, time='before_open')  #选股
    run_weekly(trade, weekday=1, time='open')  #交易


def chenk_stocks(context):
    # 得到沪深300医药指数成分股
    g.stocks = get_index_stocks('000931.XSHG')
    # 查询股票的市净率，并按照市净率升序排序
    if len(g.stocks) > 0:
        g.df = get_fundamentals(
            query(valuation.code,
                  valuation.pb_ratio).filter(valuation.code.in_(
                      g.stocks)).order_by(valuation.pb_ratio.asc()))
        # 找出最低市净率的一只股票
        g.code = g.df['code'][0]


def trade(context):
    if len(g.stocks) > 0:
        code = g.code
        # 如持仓股票不是最低市净率的股票，则卖出
        for stock in context.portfolio.positions.keys():
            if stock != code:
                order_target(stock, 0)
        # 持仓该股票
        if len(context.portfolio.positions) > 0:
            return
        else:
            order_value(code, context.portfolio.cash)
