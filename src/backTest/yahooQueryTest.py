# Yahoo Finance APIで企業分析にチャレンジ
# https://utsu.engineer/?p=185
import matplotlib.pyplot as plt
from yahooquery import Ticker

yq_data = Ticker('3907.T')
# # 取得できそうな情報を確認
all = [i for i in Ticker.__dict__.keys()
 if "_" not in i[:2] and i not in ["option_chain", "history", "symbols"]]
print("all:", all)


all_modules = yq_data.all_modules
get_modules = yq_data.get_modules
asset_profile = yq_data.asset_profile
calendar_events = yq_data.calendar_events
earnings = yq_data.earnings
earnings_trend = yq_data.earnings_trend
esg_scores = yq_data.esg_scores
financial_data = yq_data.financial_data
news = yq_data.news
index_trend = yq_data.index_trend
industry_trend = yq_data.industry_trend
key_stats = yq_data.key_stats
major_holders = yq_data.major_holders
page_views = yq_data.page_views
price = yq_data.price
quote_type = yq_data.quote_type
quotes = yq_data.quotes
recommendations = yq_data.recommendations
share_purchase_activity = yq_data.share_purchase_activity
summary_detail = yq_data.summary_detail
summary_profile = yq_data.summary_profile
technical_insights = yq_data.technical_insights
all_financial_data = yq_data.all_financial_data
get_financial_data = yq_data.get_financial_data
corporate_events = yq_data.corporate_events
corporate_guidance = yq_data.corporate_guidance
valuation_measures = yq_data.valuation_measures
balance_sheet = yq_data.balance_sheet
cash_flow = yq_data.cash_flow
company_officers = yq_data.company_officers
earning_history = yq_data.earning_history
fund_ownership = yq_data.fund_ownership
grading_history = yq_data.grading_history
income_statement = yq_data.income_statement
insider_holders = yq_data.insider_holders
insider_transactions = yq_data.insider_transactions
institution_ownership = yq_data.institution_ownership
recommendation_trend = yq_data.recommendation_trend
sec_filings = yq_data.sec_filings
fund_bond_holdings = yq_data.fund_bond_holdings
fund_category_holdings = yq_data.fund_category_holdings
fund_equity_holdings = yq_data.fund_equity_holdings
fund_performance = yq_data.fund_performance
fund_profile = yq_data.fund_profile
fund_holding_info = yq_data.fund_holding_info
fund_top_holdings = yq_data.fund_top_holdings
fund_bond_ratings = yq_data.fund_bond_ratings
fund_sector_weightings = yq_data.fund_sector_weightings
dividend_history = yq_data.dividend_history

print("all_modules:",all_modules)
print("")
print("get_modules:",get_modules)
print("")
print("asset_profile:",asset_profile)
print("")
print("calendar_events:",calendar_events)
print("")
print("earnings:",earnings)
print("")
print("earnings_trend:",earnings_trend)
print("")
print("esg_scores:",esg_scores)
print("")
print("financial_data:",financial_data)
print("")
print("news:",news)
print("")
print("index_trend:",index_trend)
print("")
print("industry_trend:",industry_trend)
print("")
print("key_stats:",key_stats)
print("")
print("major_holders:",major_holders)
print("")
print("page_views:",page_views)
print("")
print("price:",price)
print("")
print("quote_type:",quote_type)
print("")
print("quotes:",quotes)
print("")
print("recommendations:",recommendations)
print("")
print("share_purchase_activity:",share_purchase_activity)
print("")
print("summary_detail:",summary_detail)
print("")
print("summary_profile:",summary_profile)
print("")
print("technical_insights:",technical_insights)
print("")
print("all_financial_data:",all_financial_data)
print("")
print("get_financial_data:",get_financial_data)
print("")
print("corporate_events:",corporate_events)
print("")
print("corporate_guidance:",corporate_guidance)
print("")
print("valuation_measures:",valuation_measures)
print("")
print("balance_sheet:",balance_sheet)
print("")
print("cash_flow:",cash_flow)
print("")
print("company_officers:",company_officers)
print("")
print("earning_history:",earning_history)
print("")
print("fund_ownership:",fund_ownership)
print("")
print("grading_history:",grading_history)
print("")
print("income_statement:",income_statement)
print("")
print("insider_holders:",insider_holders)
print("")
print("insider_transactions:",insider_transactions)
print("")
print("institution_ownership:",institution_ownership)
print("")
print("recommendation_trend:",recommendation_trend)
print("")
print("sec_filings:",sec_filings)
print("")
print("fund_bond_holdings:",fund_bond_holdings)
print("")
print("fund_category_holdings:",fund_category_holdings)
print("")
print("fund_equity_holdings:",fund_equity_holdings)
print("")
print("fund_performance:",fund_performance)
print("")
print("fund_profile:",fund_profile)
print("")
print("fund_holding_info:",fund_holding_info)
print("")
print("fund_top_holdings:",fund_top_holdings)
print("")
print("fund_bond_ratings:",fund_bond_ratings)
print("")
print("fund_sector_weightings:",fund_sector_weightings)
print("")
print("dividend_history:",dividend_history)
print("")


# # 経営指標
# financial_data = yq_data.financial_data
#
# # 統計情報（企業価値※や帳簿価値）
# # ※会社が生み出す将来のフリーキャッシュフローを割引いた現在価値
# key_stats = yq_data.key_stats

# # 株価情報
# yq_data.price
#
# # 株式の種類
# yq_data.quote_type
#
# # 売買情報
# yq_data.share_purchase_activity
#
# # 株式情報の要約
# yq_data.summary_detail
#
# # 企業情報（株式情報の要約）
# yq_data.summary_profile
#
#
# # 関連する推奨銘柄
# yq_data.recommendations
#
# # テクニカル指標
# """Technical Insights
#         Technical trading information as well as company metrics related
#         to innovativeness, sustainability, and hiring.  Metrics can also
#         be compared against the company's sector
# """
# yq_data.technical_insights
#
# # 指定した銘柄チェッカーの有無
# yq_data.validation
#
# # 取得できる全ての株がを取得
# yq_data.history(period='id')
#
# yq_data.history(period='max')['close'].plot(figsize=(16, 9))




# income_statement = yq_data.income_statement('q')
# income_statement
#
# # 決算日付、売上高、粗利、営業利益のみ抽出
# income_statement = income_statement.query('periodType != "TTM"').sort_values('asOfDate')[['asOfDate', 'TotalRevenue', 'GrossProfit', 'OperatingIncome']]
# income_statement
#
# # 粗利率を算出
# income_statement['GrossProfitMargin'] = (income_statement['GrossProfit'] / income_statement['TotalRevenue']) * 100
# # 営業利益率を算出
# income_statement['OperatingIncomeMargin'] = (income_statement['OperatingIncome'] / income_statement['TotalRevenue']) * 100
# income_statement
#
# # 決算日付、売上高、粗利率、営業利益率をグラフ(3軸)に描画
# fig, ax1 = plt.subplots(figsize=(16, 9))
#
# # 売上高
# ax1.bar(income_statement['asOfDate'], income_statement['TotalRevenue'], align="center", color="lightblue", width=10,
#         label='TotalRevenue')
# ax1.set_ylabel('TotalRevenue')
# # ax1.legend('TotalRevenue')
#
# # 粗利率
# # 折れ線グラフを出力
# ax2 = ax1.twinx()
# ax2.plot(income_statement['asOfDate'], income_statement['GrossProfitMargin'], linewidth=4, color="orange",
#          label='GrossProfitMargin')
# ax2.set_ylabel('GrossProfitMargin')
# # ax2.legend('GrossProfitMargin')
#
# # 営業利益
# # 折れ線グラフを出力
# ax3 = ax1.twinx()
# ax3.plot(income_statement['asOfDate'], income_statement['OperatingIncomeMargin'], linewidth=4, color="red",
#          label='OperatingIncomeMargin')
# ax3.set_ylabel('OperatingIncomeMargin')
# # ax3.legend('OperatingIncomeMargin')
#
# # 凡例
# # グラフの本体設定時に、ラベルを手動で設定する必要があるのは、barplotのみ。plotは自動で設定される＞
# handler1, label1 = ax1.get_legend_handles_labels()
# handler2, label2 = ax2.get_legend_handles_labels()
# handler3, label3 = ax3.get_legend_handles_labels()
# # 凡例をまとめて出力する
# # ax1.legend(handler1 + handler2 + handler3, label1 + label2 + label3, loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0, fontsize=12)
# ax1.legend(handler1 + handler2 + handler3, label1 + label2 + label3, loc='upper left', borderaxespad=1, fontsize=12)
# ax3.spines["right"].set_position(("axes", 1.2))
