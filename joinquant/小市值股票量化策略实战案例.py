# 导入函数库
import jqdata


## 初始化函数，设定要操作的股票、基准等等
def initialize(context):
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
    # 持仓数量
    g.stocknum = 3
    # 交易日计时器
    g.days = 0
    # 调仓频率
    g.refresh_rate = 5
    # 运行函数
    run_daily(trade, 'every_bar')


def check_stocks(context):
    # 设定查询条件
    q = query(valuation.code, valuation.market_cap).filter(
        valuation.market_cap.between(20,
                                     30)).order_by(valuation.market_cap.asc())
    # 选出低市值的股票，构成buylist
    df = get_fundamentals(q)
    buylist = list(df['code'])
    # 过滤停牌股票
    buylist = filter_paused_stock(buylist)
    return buylist[:g.stocknum]


过滤停牌股票函数


def filter_paused_stock(stock_list):
    current_data = get_current_data()
    return [stock for stock in stock_list if not current_data[stock].paused]


交易函数


def trade(context):
    if g.days % g.refresh_rate == 0:
        ## 获取持仓列表
        sell_list = list(context.portfolio.positions.keys())
        # 如果有持仓，则卖出
        if len(sell_list) > 0:
            for stock in sell_list:
                order_target_value(stock, 0)
        ## 分配资金
        if len(context.portfolio.positions) < g.stocknum:
            Num = g.stocknum - len(context.portfolio.positions)
            Cash = context.portfolio.cash / Num
        else:
            Cash = 0
        ## 选股
        stock_list = check_stocks(context)
        ## 买入股票
        for stock in stock_list:
            if len(context.portfolio.positions.keys()) < g.stocknum:
                order_value(stock, Cash)
        # 天计数加一
        g.days = 1
    else:
        g.days += 1
