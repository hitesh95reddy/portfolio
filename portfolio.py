import streamlit as st  
import pandas as pd 
import json
import os
import plotly.express as px

def load_data():
    # equities
    data=json.load(open("data.json"))
    data=data['data']['results']
    data=[
            {
            'isin_code':i['isin_code'],
            'display_name':i['display_name'],
            'quantity' : int(i['quantity']),
            'purchase_price' : round(float(i['cost_price']),2),
            'cmp' : round(float(i['last_traded_price']),2),
            'investment' : round(int(i['quantity'])*float(i['cost_price']),2),
            'current_value' : round(int(i['quantity'])*float(i['last_traded_price']),2),
            'pl_amt' : round(int(i['quantity'])*(float(i['last_traded_price'])-float(i['cost_price'])),2),
            'pl_pct' : round((float(i['last_traded_price'])-float(i['cost_price']))*100/float(i['cost_price']),2),
            'sector':i['sector'],
            'mcap':i['mcap_type']
        } 
            for i in data
        ]
    consolidated_data={'investment':0,'current_value':0,'pl_amt':0,'pl_pct':0,'num_stocks':0}
    for i in data:
        consolidated_data['investment']+=i['investment']
        consolidated_data['current_value']+=i['current_value']
        consolidated_data['pl_amt']+=i['pl_amt']
        consolidated_data['num_stocks']+=1
    consolidated_data['pl_pct']=round(consolidated_data['pl_amt']*100/consolidated_data['investment'],2)   
    consolidated_data={k:round(v,2) for k,v in consolidated_data.items()}
    
    mf_data=json.load(open("mf_data.json"))
    mf_consolidated_data={
        'investment':round(mf_data['portfolioDetails']['totalInvestedAmount'],2),
        'current_value':round(mf_data['portfolioDetails']['totalCurrentValue'],2),
        'pl_amt':round(mf_data['portfolioDetails']['totalReturns'],2),
        'pl_pct':round(mf_data['portfolioDetails']['totalReturns']*100/mf_data['portfolioDetails']['totalInvestedAmount'],2),
        'xirr':round(mf_data['portfolioDetails']['xirr'],2),
        }
    mf_data=[
                {
                    'isin_code':i['schemeDetails']['isin'],
                    'display_name':i['schemeDetails']['name'],
                    'cmp':round(i['schemeDetails']['navVal'],2),
                    'purchase_price':round(i['investmentDetails']['averageCostNav'],2),
                    'investment':round(i['investmentDetails']['totalInvestedAmount'],2),
                    'current_value':round(i['investmentDetails']['totalCurrentValue'],2),
                    'quantity':i['investmentDetails']['totalAllocatedUnits'],
                    'pl_amt':round(i['investmentDetails']['totalReturns'],2),
                    'pl_pct':round(i['investmentDetails']['totalReturns']*100/i['investmentDetails']['totalInvestedAmount'],2),
                    
                } 
                for i in mf_data['schemeView']['results']
            ]
    return data,consolidated_data,mf_data,mf_consolidated_data

data,consolidated_data,mf_data,mf_consolidated_data=load_data()

st.set_page_config(
    page_title="PortFolio",
    page_icon="💸",
    layout="wide"
)

st.header("Portfolio")
row1=st.columns(3)
row1[0].metric('Investment',consolidated_data['investment']+mf_consolidated_data['investment'])
row1[1].metric('Current Value',consolidated_data['current_value']+mf_consolidated_data['current_value'])    
row1[2].metric('P/L Amt',consolidated_data['pl_amt']+mf_consolidated_data['pl_amt'],round((consolidated_data['pl_amt']+mf_consolidated_data['pl_amt'])*100/(consolidated_data['investment']+mf_consolidated_data['investment']),2))
st.divider()

eq_tb,mf_tab=st.tabs(["Equity Portfolio", "Mutual Fund Portfolio"])

df = pd.DataFrame.from_dict(data)
eq_tb.header("Equity Portfolio")
row1=eq_tb.columns(3)
row1[0].metric('Investment',consolidated_data['investment'])
row1[1].metric('Current Value',consolidated_data['current_value'])
row1[2].metric('P/L Amt',consolidated_data['pl_amt'],consolidated_data['pl_pct'])
row2=eq_tb.columns(3)
row2[1].metric('Number of Stocks',consolidated_data['num_stocks'])
eq_tb.divider()

if eq_tb.checkbox('Equity Portfolio details',value=True):
    tab1, tab2 = eq_tb.tabs(["Tabular", "Pie Chart"])
    with tab1:
        df['investment_pct']=df['investment']/consolidated_data['investment']*100
        df['current_value_pct']=df['current_value']/consolidated_data['current_value']*100
        df['pl_amt_pct']=df['pl_amt']/consolidated_data['pl_amt']*100
        tab1.dataframe(df,hide_index=True)
    with tab2:
        fig = px.pie(df, values='investment', names='display_name',
            title='Investments by company')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        tab2.plotly_chart(fig)
    
    sector_investments=df.groupby('sector').agg(investment=('investment', 'sum'), current_value=('current_value', 'sum'),num_stocks=('sector','count')).reset_index()
    sector_investments['investment_pct']=round(sector_investments['investment']*100/consolidated_data['investment'],2)
    sector_investments['current_value_pct']=round(sector_investments['current_value']*100/consolidated_data['current_value'],2)
    sector_investments['pl_amt']=round(sector_investments['current_value']-sector_investments['investment'],2)  
    sector_investments['pl_amt_pct']=round(sector_investments['pl_amt']*100/sector_investments['investment'],2) 
    eq_tb.header("Sector Wise Investments")
    eq_tb.text(f"No of sectors:{sector_investments.shape[0]}")
    tab1, tab2, tab3 = eq_tb.tabs(["Tabular", "Bar Chart", "Pie Chart"])
    with tab1:
        tab1.dataframe(sector_investments,hide_index=True)
    with tab2:
        fig = px.bar(sector_investments, x="sector", y=["investment", "current_value"], barmode="group")
        tab2.plotly_chart(fig)
    with tab3:
        fig = px.pie(sector_investments, values='investment', names='sector',
                    title='Investments by Sector')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        tab3.plotly_chart(fig)

    eq_tb.divider()

    mcap_investments=df.groupby('mcap').agg(investment=('investment', 'sum'), current_value=('current_value', 'sum'),num_stocks=('mcap','count')).reset_index()
    mcap_investments['investment_pct']=round(mcap_investments['investment']*100/consolidated_data['investment'],2)
    mcap_investments['current_value_pct']=round(mcap_investments['current_value']*100/consolidated_data['current_value'],2) 
    mcap_investments['pl_amt']=round(mcap_investments['current_value']-mcap_investments['investment'],2)
    mcap_investments['pl_amt_pct']=round(mcap_investments['pl_amt']*100/mcap_investments['investment'],2)
    eq_tb.header("Market Cap Wise Investments")
    
    tab1, tab2, tab3 = eq_tb.tabs(["Tabular", "Bar Chart", "Pie Chart"])
    with tab1:
        tab1.dataframe(mcap_investments,hide_index=True)
    with tab2:
        fig = px.bar(mcap_investments, x="mcap", y=["investment", "current_value"], barmode="group")
        tab2.plotly_chart(fig)
    with tab3:
        fig = px.pie(mcap_investments, values='investment', names='mcap',
                title='Investments by Market Cap')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        tab3.plotly_chart(fig)
    eq_tb.divider()
    

mf_tab.header("Mutual Fund Portfolio")
row1=mf_tab.columns(3)
row1[0].metric('Investment',mf_consolidated_data['investment'])
row1[1].metric('Current Value',mf_consolidated_data['current_value'])
row1[2].metric('P/L Amt',mf_consolidated_data['pl_amt'],mf_consolidated_data['pl_pct'])
row2=mf_tab.columns(4)
row2[1].metric('XIRR',f"{mf_consolidated_data['xirr']}%")
row2[2].metric('Number of Funds',len(mf_data))
mf_tab.divider()

mf_df=pd.DataFrame.from_dict(mf_data)
tab1,tab2,tab3=mf_tab.tabs(["Tabular", "Bar Chart","Pie Chart"])
with tab1:
    tab1.dataframe(mf_df,hide_index=True)
with tab2:
    fig = px.bar(mf_df, x="display_name", y=["investment", "current_value"], barmode="group")
    tab2.plotly_chart(fig)
with tab3:
    fig = px.pie(mf_df, values='investment', names='display_name',
            title='Investments by MF House')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    tab3.plotly_chart(fig)
