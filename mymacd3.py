#LAST VERSION
OrgAccount = exchange.GetAccount()

LastProfit = 0
AllProfit = 0
LastTicker = null;
LastType = null
LastPrice = 0
LastAmount=0
BuyBreak=0
SellBreak=0
def StripOrders(exch):  #取消所有未成交挂单

	orders = _C(exch.GetOrders) #取订单确保成功
	for order in orders:
		exch.CancelOrder(order.Id,order,'买单' if order.Type ==ORDER_TYPE_BUY else '卖单')


def updateProfit(e, account, ticker) :

	profit = _N(LastProfit + (((account.Stocks + account.FrozenStocks) - (OrgAccount.Stocks + OrgAccount.FrozenStocks)) * ticker.Last) + ((account.Balance + account.FrozenBalance) - (OrgAccount.Balance + OrgAccount.FrozenBalance)), 4);
	LogProfit(profit, "币数:", _N(account.Stocks + account.FrozenStocks, 4), "钱数:", _N(account.Balance + account.FrozenBalance, 4));
	return profit



def now_buy(exch,money):
	global BuyBreak,SellBreak
	try:
		id=exch.Buy(-1, money)         # 使用市价单， 在参数 Price 传入 -1 , 第二个参数 Amount 回测系统中为 法币。
		# Log("nowAccount:", exchange.GetAccount()) # 显示当前账户信息，用于对比 实际买入的数量。

		order = exch.GetOrder(id)
		Log(order)
		if order['Status'] == 1 :

			LastType='buy'
			LastAmount=order['Amount']	
			LastPrice = money/LastAmount			
			Log('djfw')
			nowAccount=exch.GetAccount(); #显示买入后的  账户信息，对比初始账户信息。可以对比出 买入操作的成交的数量。
			ticker = _C(exch.GetTicker);
			AllProfit = updateProfit(exch, nowAccount, ticker);
			SellBreak=0
			return True
	except Exception, e:
		Log('宝宝你的钱钱不够')
		BuyBreak=1
		return False


def now_sell(exch,coin):
	global BuyBreak,SellBreak
	try:
		id= exch.Sell(-1,coin)          # 使用市价单， 在参数 Price 传入 -1 , 第二个参数 Amount 回测系统中为 法币。
		# Log("nowAccount:", exchange.GetAccount()); # 显示当前账户信息，用于对比 实际买入的数量。
		order = exch.GetOrder(id)	
		if order['Status'] == 1:

			LastType='sell'


			LastAmount=order['Amount']	
			LastPrice = exch.GetTicker().Last

			nowAccount=exch.GetAccount(); #显示买入后的  账户信息，对比初始账户信息。可以对比出 买入操作的成交的数量。
			ticker = _C(exch.GetTicker);
			AllProfit = updateProfit(exch, nowAccount, ticker)
			BuyBreak=0
			return True
	except Exception, e:
		Log('宝宝你没币了！')
		SellBreak=1
		return False

def get_purchase(exch,delta,cash,coin):
	#对冲什么鬼
	# 如果上次是卖 

	if  LastType=='buy':
		#取得当前价
		depth =exch.GetDepth()
		
		#对比LastPrice+delta和nowPrice
		current_price=depth.Bids[0]
		if current_get > LastPrice +delta:
			amount= min(LastAmount,coin)
			exchange.Sell(current_get,amount)
			LastAmount=amount
			LastPrice  = current_get
			LastType = 'Sell'					
			Log('卖出价格%s卖出数量'%(current_get,amount))
	elif LastType=='sell':
		depth =exch.GetDepth()
		current_price = depth.Asks[0]
		if current_price< LastPrice-delta:
			number_of_shares = _N(cash/current_price,3)
			#可购买时下单
			amount= min(number_of_shares,LastAmount)
			exchange.Buy(current_price,amount)
			LastAmount=amount
			LastPrice  = current_price
			LastType = 'Buy'

			Log('买入成交价%s成交量%s'%(current_price,amount))

def get_MACD(exch,dif,dea,cash,coin):
	global BuyBreak,SellBreak


	if dif[-2] > 0 and dea[-2] >0 and dif[-1]<dea[-1] and dif[-2] > dea[-2]:

		if BuyBreak==1:
			return 
		# Log('cash',cash)
		trade = now_buy(exch,cash)
		if trade:
			Log('金叉买入')
		# else:

		# 	BuyBreak=1

		# Log('没买成，不再尝试买')
		return 0
	elif dif[-2] < 0 and dea[-2] <0 and dif[-1] >dea[-1] and dif[-2] <dea[-2] and coin > 0:

		if SellBreak ==1:
			return 
		# now_sell(exch,coin)
		if now_sell(exch,coin):
			Log('死叉卖出')
		# else:
		# 	global SellBreak
		# 	SellBreak=1
		# 	Log('没卖成，不再尝试卖')




def main():

    while True:
        account= exchange.GetAccount()
        money=account['Balance']
        stocks = account['Stocks']
       # Log("初始账户信息：",account );   #  用于对比交易前后账户信息
        ticker = exchange.GetTicker()
        #Log("ticker:", ticker);  # 获取并打印行情
        LastTicker= ticker


        r = exchange.GetRecords()
        while not r or len(r) < 35:
            r = exchange.GetRecords()
        macd = TA.MACD(r,12,26,9)
    

        dif = macd[0]
        dea = macd[1]
        get_MACD(exchange,dif,dea,money,stocks)

        Sleep(Interval)