"""Comparison module revision 1.1: financial calculations use the shared engine."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from finance import Market, black_scholes
from parity_theme_v1 import plot_style

def curve_rows(spots,k,r,mode,q,dividends,vary,values,fixed):
    rows=[]
    for value in sorted(values):
        t=value if vary=='Maturity' else fixed
        vol=fixed if vary=='Maturity' else value
        ds=tuple((d,date) for d,date in dividends if 0<date<t) if mode=='cash' else ()
        for s in spots:
            m=Market(float(s),k,t,r,mode,q,ds);m.validate()
            prices=black_scholes(m,vol);bounds=m.bounds()
            rows.append(dict(stock=float(s),maturity=t,volatility=vol,series=value,
                             call=prices['call'],put=prices['put'],**bounds))
    return pd.DataFrame(rows)

def reset():
    for key in list(st.session_state):
        if key.startswith('compare_'):del st.session_state[key]

def render():
    st.info('Objective: decide how much insurance costs when the remaining life or uncertainty changes. Compare three contracts at the same stock price, strike, financing rate, and dividend policy.')
    st.write('Predict first: will more time or more volatility always make both contracts more expensive? The solid curves give model values; dashed curves give lower bounds.')
    st.button('Reset comparison inputs',on_click=reset)
    a,b=st.columns(2)
    with a:
        vary=st.radio('Compare three','Maturity Volatility'.split(),horizontal=True,key='compare_vary')
        mode=st.selectbox('Dividend assumption',['none','cash','yield'],format_func=lambda x:{'none':'No dividends','cash':'Discrete cash dividend','yield':'Continuous dividend yield'}[x],key='compare_mode')
        k=st.number_input('Strike K',min_value=.01,value=100.,key='compare_k')
        r=st.number_input('Annual continuous rate r (%)',min_value=-50.,max_value=50.,value=5.,key='compare_r')/100
    with b:
        fixed=st.number_input('Fixed volatility (%)' if vary=='Maturity' else 'Fixed maturity (years)',min_value=0. if vary=='Maturity' else .001,max_value=300. if vary=='Maturity' else 10.,value=30. if vary=='Maturity' else .5,key='compare_fixed_'+vary)
        if vary=='Maturity':fixed/=100
        values=[]
        for i,value in enumerate([.25,.5,1.] if vary=='Maturity' else [15.,30.,45.]):
            val=st.number_input(f'{vary} {i+1}'+(' (years)' if vary=='Maturity' else ' (%)'),min_value=.001 if vary=='Maturity' else 0.,max_value=10. if vary=='Maturity' else 300.,value=value,key=f'compare_{vary}_{i}')
            values.append(val if vary=='Maturity' else val/100)
    if len(set(values))!=3:raise ValueError('Choose three distinct maturities or volatilities.')
    q=0.;dividends=()
    if mode=='yield':q=st.number_input('Annual continuous yield q (%)',min_value=0.,max_value=50.,value=8.,key='compare_q')/100
    if mode=='cash':
        cc=st.columns(2)
        with cc[0]:d=st.number_input('Known cash dividend per share',min_value=0.,value=10.,key='compare_d')
        with cc[1]:date=st.number_input('Dividend date (years from valuation)',min_value=.001,value=.125,key='compare_date')
        dividends=((d,date),)
        st.caption('The same dated payment is used for all contracts. Only payments strictly before each expiration are included. A payment exactly at expiration is excluded here; change the date if the option expires after the ex-dividend event.')
        st.warning('Discrete-dividend prices use spot minus dividend present value: an approximation for stock dynamics with fixed cash jumps. The parity bounds remain exact under the stated trading assumptions.')
    axis=st.radio('Stock-price date',['Future valuation date — remaining maturity T','Today — maturity T'],key='compare_axis')
    st.caption('A future valuation is a scenario: the horizontal axis is stock price S at that future date, and T is time remaining from that date. Rates, volatility, and dividend dates are measured from the same valuation date. These are option values before expiration, not realized expiration payoffs S_T.')
    cc=st.columns(2)
    with cc[0]:low=st.number_input('Minimum stock price',min_value=.001,value=20.,key='compare_low')
    with cc[1]:high=st.number_input('Maximum stock price',min_value=.002,value=180.,key='compare_high')
    if high<=low:raise ValueError('Maximum stock price must exceed minimum stock price.')
    upper=st.checkbox('Also show upper bounds',key='compare_upper')
    frame=curve_rows(np.linspace(low,high,161),k,r,mode,q,dividends,vary,values,fixed)
    xlabel='Stock price S at the future valuation date (per share)' if axis.startswith('Future') else 'Current stock price S₀ (per share)'
    colors=['#142B49','#007F86','#B04700']
    for contract in ['call','put']:
        st.subheader(('1. Calls' if contract=='call' else '2. Puts')+' — model values and bounds')
        fig=go.Figure()
        for i,value in enumerate(sorted(values)):
            sub=frame[frame.series==value];label=f'T = {value:g} years' if vary=='Maturity' else f'σ = {value*100:g}%'
            fig.add_trace(go.Scatter(x=sub.stock,y=sub[contract],name=label+' · model',line=dict(color=colors[i],width=3),legendgroup=str(i),hovertemplate='Stock %{x:.2f}<br>Value %{y:.4f}<extra>%{fullData.name}</extra>'))
            if vary=='Maturity' or i==0:
                boundlabel=label if vary=='Maturity' else 'All three volatilities'
                fig.add_trace(go.Scatter(x=sub.stock,y=sub[contract+'_lower'],name=boundlabel+' · lower bound',line=dict(color=colors[i],width=2,dash='dash'),legendgroup=str(i)))
                if upper:fig.add_trace(go.Scatter(x=sub.stock,y=sub[contract+'_upper'],name=boundlabel+' · upper bound',line=dict(color=colors[i],width=1.5,dash='dot'),legendgroup=str(i)))
        fig.update_layout(title=f'European {contract} — three {"maturities" if vary=="Maturity" else "volatilities"}',xaxis_title=xlabel,yaxis_title='Option value at the valuation date (per share)',height=520)
        fig.add_vline(x=k,line_dash='dot',annotation_text='Strike K')
        st.plotly_chart(plot_style(fig),width='stretch',key='compare_chart_'+contract)
        ordered=[frame[frame.series==v][contract].to_numpy() for v in sorted(values)]
        difference=ordered[-1]-ordered[0]
        st.caption(f'Largest minus smallest {vary.lower()}: from {difference.min():+.4f} to {difference.max():+.4f} per share across the plotted stock prices.')
    st.subheader('Inspect one stock-price scenario')
    spot=st.number_input('Stock price for the comparison table',min_value=.001,value=100.,key='compare_spot')
    table=curve_rows([spot],k,r,mode,q,dividends,vary,values,fixed)
    st.dataframe(table.drop(columns=['series']).rename(columns={'stock':'Stock price','maturity':'Remaining years','volatility':'Volatility (decimal)','call':'Call value','put':'Put value','call_lower':'Call lower bound','call_upper':'Call upper bound','put_lower':'Put lower bound','put_upper':'Put upper bound'}).style.format('{:.6f}'),hide_index=True,width='stretch')
    with st.expander('Hints and interpretation',expanded=True):
        st.write('Volatility: both calls and puts increase as uncertainty expands; their bounds do not depend on volatility. At zero volatility, the model equals the lower bound.')
        st.write('Maturity: a no-dividend call increases with remaining maturity when rates are nonnegative. European puts can become cheaper as receipt of the strike is delayed. Dividend-paying calls can also become cheaper; the graph may change ordering across stock prices.')
        st.write('Try the put counterexample: no dividends, K = 100, r = 5%, fixed volatility = 10%, stock price = 50, maturities 0.25, 0.5, and 1. Then try continuous yield 8% with rate 5% and inspect deep-in-the-money calls.')
        st.latex(r'c \geq \max(G-Ke^{-rT},0),\quad p \geq \max(Ke^{-rT}-G,0)')
        st.latex(r'G=S\quad\text{or}\quad S-\sum D_i e^{-rt_i}\quad\text{or}\quad Se^{-qT}')
    with st.expander('Expiration payoffs — future stock price S_T'):
        st.write('At expiration, calls pay max(S_T − K, 0) and puts pay max(K − S_T, 0). These curves coincide across all three maturities and volatilities: uncertainty changes the premium before expiration, not the contractual payoff formula.')
        fig=go.Figure()
        spots=np.linspace(low,high,161)
        for name,y,dash in [('Call payoff',np.maximum(spots-k,0),'solid'),('Put payoff',np.maximum(k-spots,0),'dash')]:fig.add_trace(go.Scatter(x=spots,y=y,name=name,line=dict(width=3,dash=dash)))
        fig.update_layout(xaxis_title='Future expiration stock price S_T (per share)',yaxis_title='Expiration payoff (per share)')
        st.plotly_chart(plot_style(fig),width='stretch',key='compare_payoff')
    st.download_button('Download graph data (CSV)',frame.to_csv(index=False),file_name='option_bound_comparisons.csv',mime='text/csv')
    st.subheader('What we learned')
    st.write('More uncertainty raises insurance value. More time has competing effects: uncertainty, delayed strike payment or receipt, and distributions. Bounds constrain prices; they do not determine the premium. Always distinguish a future valuation scenario from the expiration payoff.')
