import streamlit as st  
import pandas as pd 
import json
import os
import plotly.express as px

def load_data():
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
    
    return data,consolidated_data

data,consolidated_data=load_data()

st.set_page_config(
    page_title="PortFolio",
    page_icon="💸",
    layout="wide"
)

st.header("My Portfolio")
row1=st.columns(3)
row1[0].metric('Investment',consolidated_data['investment'])
row1[1].metric('Current Value',consolidated_data['current_value'])
row1[2].metric('P/L Amt',consolidated_data['pl_amt'],consolidated_data['pl_pct'])
row2=st.columns(3)
row2[1].metric('Number of Stocks',consolidated_data['num_stocks'])
st.divider()

df = pd.DataFrame.from_dict(data)

sector_investments=df.groupby('sector').agg(investment=('investment', 'sum'), current_value=('current_value', 'sum'),num_stocks=('sector','count')).reset_index()
sector_investments['investment_pct']=round(sector_investments['investment']*100/consolidated_data['investment'],2)
sector_investments['current_value_pct']=round(sector_investments['current_value']*100/consolidated_data['current_value'],2)
sector_investments['pl_amt']=round(sector_investments['current_value']-sector_investments['investment'],2)  
sector_investments['pl_amt_pct']=round(sector_investments['pl_amt']*100/sector_investments['investment'],2) 
st.header("Sector Wise Investments")
st.write("No of sectors:",sector_investments.shape[0])
tab1, tab2, tab3 = st.tabs(["Tabular", "Bar Chart", "Pie Chart"])
with tab1:
    st.dataframe(sector_investments,hide_index=True)
with tab2:
    fig = px.bar(sector_investments, x="sector", y=["investment", "current_value"], barmode="group")
    st.plotly_chart(fig)
with tab3:
    fig = px.pie(sector_investments, values='investment', names='sector',
                title='Investmenst by Sector')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig)

st.divider()

mcap_investments=df.groupby('mcap').agg(investment=('investment', 'sum'), current_value=('current_value', 'sum'),num_stocks=('mcap','count')).reset_index()
mcap_investments['investment_pct']=round(mcap_investments['investment']*100/consolidated_data['investment'],2)
mcap_investments['current_value_pct']=round(mcap_investments['current_value']*100/consolidated_data['current_value'],2) 
mcap_investments['pl_amt']=round(mcap_investments['current_value']-mcap_investments['investment'],2)
mcap_investments['pl_amt_pct']=round(mcap_investments['pl_amt']*100/mcap_investments['investment'],2)
st.header("Market Cap Wise Investments")
tab1, tab2, tab3 = st.tabs(["Tabular", "Bar Chart", "Pie Chart"])
with tab1:
    st.dataframe(mcap_investments,hide_index=True)
with tab2:
    fig = px.bar(mcap_investments, x="mcap", y=["investment", "current_value"], barmode="group")
    st.plotly_chart(fig)
with tab3:
    fig = px.pie(mcap_investments, values='investment', names='mcap',
             title='Investmenst by Market Cap')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig)

st.divider()

if st.checkbox('Show Portfolio'):
    tab1, tab2 = st.tabs(["Tabular", "Pie Chart"])
    with tab1:
        df['investment_pct']=df['investment']/consolidated_data['investment']*100
        df['current_value_pct']=df['current_value']/consolidated_data['current_value']*100
        df['pl_amt_pct']=df['pl_amt']/consolidated_data['pl_amt']*100
        st.dataframe(df,hide_index=True)
    with tab2:
        fig = px.pie(df, values='investment', names='display_name',
             title='Investmenst by company')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig)
