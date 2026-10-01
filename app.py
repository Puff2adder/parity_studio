"""Six-module chapter studio. Run from this folder: python -m streamlit run app.py."""
from pathlib import Path
import json, math, random, sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from finance import Market, black_scholes, arbitrage, payoff_table, hedge_costs, calculate
from question_bank import QUESTIONS, TOPICS

if not (HERE/'parity_theme_v1.py').exists():
    sys.path.insert(0,str(HERE.parents[3]/'shared/studio_theme'))
from parity_theme_v1 import apply, plot_style
EXAMPLE_FILE=(HERE/'textbook_examples_v1.json') if (HERE/'textbook_examples_v1.json').exists() else HERE.parents[2]/'examples/textbook_examples_v1.json'
EXAMPLES=json.loads(EXAMPLE_FILE.read_text(encoding='utf-8'))['examples']
BY_ID={x['id']:x for x in EXAMPLES}
PAGES={'start':'Start here','parity':'1 · Put–Call Parity and Replication',
       'dividends':'2 · Dividends and Arbitrage','forwards':'3 · Constructing Forward Contracts',
       'pricing':'4 · Black–Scholes Pricing and Investigation','comparisons':'5 · Prices and Bounds Across Stock Prices','practice':'6 · Multiple-Choice Practice'}

from comparisons import render as comparisons

st.set_page_config(page_title='Parity and Black–Scholes Studio',layout='wide')
apply()

def write(text):
    st.markdown(str(text).replace('$', r'\$'))

def invalidate(prefix):
    for suffix in ['walk','feedback','calc_result','table_feedback']:
        st.session_state.pop(prefix+'_'+suffix,None)
    # A prediction relates to the old inputs; do not retain it as an apparent current answer.
    st.session_state.pop(prefix+'_prediction',None)
    st.session_state.pop(prefix+'_expression',None)

def load_case(prefix,example_id):
    ex=BY_ID[example_id]
    for key in list(st.session_state):
        if key.startswith(prefix+'_') and key!=prefix+'_case':del st.session_state[key]
    defaults=dict(s=ex['s'],k=ex['k'],t=ex['t'],r=ex['r']*100,q=ex.get('q',0)*100,
                  mode=ex['mode'],vol=ex.get('vol',.30)*100,call=ex.get('call',0),
                  put=ex.get('put_quote',0),quantity=ex.get('quantity',100000),
                  d1=0.,dt1=ex['t']/3,d2=0.,dt2=2*ex['t']/3)
    for i,(amount,date) in enumerate(ex.get('dividends',[])[:2],1):defaults[f'd{i}']=amount;defaults[f'dt{i}']=date
    for k,v in defaults.items():st.session_state[prefix+'_'+k]=v
    st.session_state[prefix+'_loaded']=example_id

def change_case(prefix):load_case(prefix,st.session_state[prefix+'_case'])

def case_picker(page):
    candidates=[e['id'] for e in EXAMPLES if e['page']==page]
    key=page+'_case'
    if key not in st.session_state:
        requested=st.query_params.get('example')
        st.session_state[key]=requested if requested in candidates else candidates[0]
    chosen=st.selectbox('Textbook example / application',candidates,key=key,
                        format_func=lambda x:BY_ID[x]['label'],on_change=change_case,args=(page,))
    if st.session_state.get(page+'_loaded')!=chosen:load_case(page,chosen)
    st.query_params['example']=chosen
    ex=BY_ID[chosen]
    st.info('**Objective:** '+ex['objective'])
    st.subheader('Textbook problem')
    write(ex['problem'])
    st.caption('Preset facts above reproduce the chapter. Changes below create your own hypothetical experiment.')
    st.button('Reset to textbook example',key=page+'_reset',on_click=load_case,args=(page,chosen))
    return ex

def controls(page,pricing=False,quotes=False):
    with st.expander('Inputs and assumptions',expanded=True):
        cols=st.columns(3)
        settings=[('s','Spot S₀ (per unit)',.0001,100000.,.01),('k','Strike K (per unit)',.0001,100000.,.01),
                  ('t','Maturity T (years)',.0001,10.,.01),('r','Riskless / domestic rate r (%)',-50.,50.,.1)]
        for i,(name,label,low,high,step) in enumerate(settings):
            with cols[i%3]:st.number_input(label,min_value=low,max_value=high,step=step,format='%.6f',key=page+'_'+name,on_change=invalidate,args=(page,))
        with cols[1]:st.selectbox('Dividend policy',['none','cash','yield'],key=page+'_mode',
                                 format_func=lambda x:{'none':'No dividends','cash':'Known cash dividends','yield':'Continuous yield / foreign rate'}[x],on_change=invalidate,args=(page,))
        mode=st.session_state[page+'_mode']
        if mode=='yield':
            with cols[2]:st.number_input('Yield q / foreign rate (%)',min_value=0.,max_value=50.,step=.1,key=page+'_q',on_change=invalidate,args=(page,))
            st.caption('The tradable prepaid position starts with exp(−qT) units and reinvests distributions to deliver one unit at T.')
        elif mode=='cash':
            for i in [1,2]:
                cc=st.columns(2)
                with cc[0]:st.number_input(f'Cash dividend {i} (per unit; 0 = unused)',min_value=0.,max_value=100000.,step=.1,key=f'{page}_d{i}',on_change=invalidate,args=(page,))
                with cc[1]:st.number_input(f'Dividend {i} date (years from today)',min_value=.0001,max_value=10.,step=.01,format='%.6f',key=f'{page}_dt{i}',on_change=invalidate,args=(page,))
        if pricing:
            st.number_input('Annual volatility σ (%) — not variance',min_value=0.,max_value=300.,step=1.,key=page+'_vol',on_change=invalidate,args=(page,))
        if quotes:
            cc=st.columns(2)
            with cc[0]:st.number_input('Observed call premium c₀ (per unit)',min_value=0.,max_value=100000.,step=.01,format='%.6f',key=page+'_call',on_change=invalidate,args=(page,))
            with cc[1]:st.number_input('Observed put premium p₀ (per unit)',min_value=0.,max_value=100000.,step=.01,format='%.6f',key=page+'_put',on_change=invalidate,args=(page,))
        st.caption('European exercise; annual continuous rates; dates in years; positive = cash received. Frictionless matching contracts and feasible borrowing, lending, and short sales are assumed.')
    v=lambda k:st.session_state[page+'_'+k]
    divs=tuple((v(f'd{i}'),v(f'dt{i}')) for i in [1,2] if v(f'd{i}')>0) if v('mode')=='cash' else ()
    m=Market(v('s'),v('k'),v('t'),v('r')/100,v('mode'),v('q')/100,divs)
    m.validate();return m

def show_frame(rows):
    frame=pd.DataFrame(rows)
    frame.index=['']*len(frame)
    st.table(frame.style.format(lambda x:f'{0. if abs(x)<.0000005 else x:,.6f}' if isinstance(x,(float,np.floating)) else x))

def chart(x,lines,title,ylabel,k=None):
    colors=['#142B49','#007F86','#0756A3','#B04700'];dashes=['solid','dash','dot','dashdot']
    fig=go.Figure()
    for i,(name,y) in enumerate(lines.items()):fig.add_trace(go.Scatter(x=x,y=y,name=name,mode='lines',line=dict(color=colors[i%4],dash=dashes[i%4],width=4 if i==0 else 2)))
    fig.update_layout(title=title,xaxis_title='Expiration price S_T (per underlying unit)',yaxis_title=ylabel)
    fig.add_hline(y=0,line_width=1,line_color='#54799B')
    if k is not None:fig.add_vline(x=k,line_width=1,line_dash='dot',annotation_text=f'K = {k:.4f}')
    st.plotly_chart(plot_style(fig),width='stretch')

def attempt(page,prompt,target):
    st.subheader('Predict or attempt')
    write(prompt)
    st.text_input('Your numerical prediction (optional)',key=page+'_prediction',on_change=lambda:st.session_state.pop(page+'_feedback',None))
    if st.button('Check my prediction',key=page+'_check'):
        try:
            answer=float(st.session_state[page+'_prediction']);ok=math.isfinite(answer) and abs(answer-target)<=max(.0001,abs(target)*.00001)
            st.session_state[page+'_feedback']=('success' if ok else 'warning','Your prediction agrees with the calculation.' if ok else 'Revisit the timeline and signs. You can open the hints or full solution at any time.')
        except ValueError:st.session_state[page+'_feedback']=('warning','Enter a finite number or open the walkthrough directly.')
    if page+'_feedback' in st.session_state:
        level,msg=st.session_state[page+'_feedback'];getattr(st,level)(msg)

def reveal(page):
    if st.button('Show complete worked solution',key=page+'_show'):st.session_state[page+'_walk']=True
    return st.session_state.get(page+'_walk',False)

def calculator(page,m,extra=None):
    with st.expander('Formula calculator — optional'):
        variables=dict(S0=m.s,K=m.k,T=m.t,r=m.r,q=m.q if m.mode=='yield' else 0.,G0=m.prepaid(),PVK=m.strike_pv(),I0=m.dividend_pv())
        variables.update(extra or {})
        write('Use +, − (type -), *, /, ^, parentheses, exp, sqrt, ln, N, abs, max, and min. Rates in this calculator are decimals.')
        st.code(', '.join(f'{k}={v:.8g}' for k,v in variables.items()))
        default='c0 + PVK - G0' if 'c0' in variables else 'G0 * exp(r*T)'
        expr=st.text_input('Expression',value=default,key=page+'_expression')
        if st.button('Calculate expression',key=page+'_calc'):
            try:st.session_state[page+'_calc_result']=('success',f'Result: {calculate(expr,variables):,.8f}')
            except ValueError as e:st.session_state[page+'_calc_result']=('warning',str(e))
        if page+'_calc_result' in st.session_state:
            level,msg=st.session_state[page+'_calc_result'];getattr(st,level)(msg)

def export_record(page,m,result):
    st.download_button('Download this experiment record',json.dumps({'example_id':st.session_state[page+'_case'],'inputs':m.__dict__,'results':result,'note':'Hypothetical practice; add your interpretation separately.'},indent=2),file_name='parity_experiment.json',mime='application/json',key=page+'_download')
    st.caption('Record your interpretation alongside these inputs and outputs. Session answers are not saved after closing the studio.')

def replication():
    page='parity';case_picker(page);m=controls(page,quotes=True)
    c=st.session_state[page+'_call'];p=st.session_state[page+'_put'];fair=m.put(c)
    attempt(page,'What should the matching put cost under these inputs?',fair)
    with st.expander('Hint 1 — identify the two packages'):write('Stock plus put and call plus a bond both pay max(S_T, K) when there are no dividends. With dividends, use the prepaid terminal-asset position instead of an ordinary share.')
    with st.expander('Hint 2 — rearrange the identity'):st.latex(r'p_0=c_0+Ke^{-rT}-G_0')
    if reveal(page):
        st.subheader('Worked solution')
        write(f'1. Prepaid value G₀ = {m.prepaid():.6f}. 2. Strike PV = {m.k:.6f}exp(−{m.r:g} × {m.t:g}) = {m.strike_pv():.6f}.')
        write(f'3. Put = {c:.6f} + {m.strike_pv():.6f} − {m.prepaid():.6f} = **{fair:.6f}**.')
        write('Synthetic put: long call, long strike bond, and short prepaid asset. For known dividends this adds dividend-date bonds to compensate the stock lender; for yield it uses the reinvesting short position.')
        write(f'4. Observed put minus implied put = {p-fair:+.6f}. Sell the expensive package and buy its cheap equivalent. The table below uses the quoted premiums as supplied.')
        if abs(p-fair)<1e-10:st.success('The quotes satisfy parity; no parity discrepancy under these assumptions.')
        else:show_frame(arbitrage(m,c,p,[.7*m.k,m.k,1.3*m.k]))
    if fair<0 or not m.bounds()['call_lower']<=c<=m.bounds()['call_upper']:st.warning('The call quote also conflicts with a price bound. Treat the quote set as inconsistent, not as a valid model calibration.')
    st.subheader('Build the payoff table')
    states=[.7*m.k,m.k,1.3*m.k];rows=payoff_table(m.k,states)
    initial=pd.DataFrame({'S_T':states,'Stock + put':[np.nan]*3,'Call + bond':[np.nan]*3,'Synthetic put':[np.nan]*3})
    signature=f'{m.k:.8f}'
    edit=st.data_editor(initial,hide_index=True,disabled=['S_T'],key=page+'_table_'+signature,width='stretch',
        column_config={name:st.column_config.NumberColumn(format='%.6f') for name in initial.columns},
        on_change=lambda:st.session_state.pop(page+'_table_feedback',None))
    if st.button('Check payoff table',key=page+'_table_check'):
        try:ok=all(abs(float(edit.iloc[i][name])-rows[i][name])<.001 for i in range(3) for name in ['Stock + put','Call + bond','Synthetic put'])
        except (ValueError,TypeError):ok=False
        st.session_state[page+'_table_feedback']=ok
    if page+'_table_feedback' in st.session_state:
        (st.success if st.session_state[page+'_table_feedback'] else st.warning)('The table matches the payoffs.' if st.session_state[page+'_table_feedback'] else 'Check each state. Empty cells can be completed or you can reveal the table below.')
    with st.expander('Reveal component payoff table'):show_frame(rows)
    x=np.linspace(0,2*m.k,101)
    chart(x,{'Stock + put = call + bond':np.maximum(x,m.k),'Stock':x,'Put payoff':np.maximum(m.k-x,0)},'Equivalent terminal packages','Terminal payoff (per unit)',m.k)
    with st.expander('Application — why are spot at-the-money calls more expensive?'):
        st.latex(r'K=S_0,\ q=0\quad\Rightarrow\quad c_0-p_0=S_0(1-e^{-rT})')
        write(f'At your spot and maturity with no dividends, the gap would be {m.s*(1-math.exp(-m.r*m.t)):.6f}. It is positive at positive rates, zero at zero rates, and negative at negative rates. The call delays paying K; the put delays receiving K.')
    calculator(page,m,{'c0':c});export_record(page,m,{'implied_put':fair,'quote_gap':p-fair})
    st.subheader('What we learned')
    write('Matching every dated cash flow establishes a price relationship without a volatility forecast. Equal spot and strike do not generally mean equal premiums. Actual trading also requires executable prices and feasible financing.')

def dividends():
    page='dividends';case_picker(page);m=controls(page,quotes=True)
    c=st.session_state[page+'_call'];p=st.session_state[page+'_put'];fair=m.put(c)
    attempt(page,'Include the dividend policy: what is the matching put value?',fair)
    with st.expander('Hint 1 — strip out the interim payments'):write('For known cash payments, G₀ = S₀ − ΣDᵢ exp(−rtᵢ). For continuous yield, G₀ = S₀ exp(−qT).')
    with st.expander('Hint 2 — make the arbitrage cash flows cancel'):write('An overpriced put calls for a long synthetic put and short observed put. Short stock owes dividends, so lend their present values. Reverse every trade if the put is underpriced.')
    if reveal(page):
        st.subheader('Worked solution')
        write(f'1. Cash dividend PV = {m.dividend_pv():.6f}. 2. Prepaid asset G₀ = {m.prepaid():.6f}. 3. Strike PV = {m.strike_pv():.6f}.')
        write(f'4. p₀ = {c:.6f} + {m.strike_pv():.6f} − {m.prepaid():.6f} = **{fair:.6f}**. Quote discrepancy = {p-fair:+.6f}.')
        if abs(p-fair)<1e-10:st.success('Parity holds for the current quotes.')
        else:
            show_frame(arbitrage(m,c,p,[.75*m.k,m.k,1.25*m.k]))
            write('The Total row has a positive initial receipt and zero later net cash flows. Rounding displayed numbers can leave tiny apparent residuals; calculations retain full precision.')
        if m.mode=='yield':write(f'The initial quantity of the reinvesting underlying position is exp(−qT) = {math.exp(-m.q*m.t):.6f}. Its absolute terminal quantity is one. Dividend compensation on the short is financed within that position.')
    if not m.bounds()['call_lower']<=c<=m.bounds()['call_upper']:st.warning('The call quote violates a bound under these inputs. The quoted market is internally inconsistent.')
    st.subheader('Application — vary the dividend policy')
    write('Predict what happens to the implied put when you increase a dividend. Change the amount or yield above and check the result. For cash dividends, change the payment date as a separate experiment.')
    comparison=[]
    for mode in ['none','cash','yield']:
        alt=Market(m.s,m.k,m.t,m.r,mode,m.q,m.dividends)
        comparison.append({'Policy':mode,'G₀':alt.prepaid(),'Implied put':alt.put(c),'Fair forward strike':alt.forward()})
    with st.expander('Compare policies at the same supplied call premium'):
        st.caption('The cash comparison uses the active cash schedule; the yield comparison uses the yield field. A zero cash schedule or zero yield reproduces the no-dividend case. Holding the call quote fixed isolates the parity relation, not a full model repricing.')
        show_frame(comparison)
    calculator(page,m,{'c0':c});export_record(page,m,{'implied_put':fair,'dividend_pv':m.dividend_pv(),'arbitrage_initial_receipt':abs(p-fair)})
    st.subheader('What we learned')
    write('Dividends change the prepaid terminal asset. A valid arbitrage must cover each dividend date, not just expiration. Known dividend amounts and a tradable reinvesting position are substantive assumptions.')

def forwards():
    page='forwards';case_picker(page);m=controls(page)
    attempt(page,'Which strike would make c₀ − p₀ equal to zero?',m.forward())
    with st.expander('Hint 1 — join the call right and put obligation'):st.latex(r'\max(S_T-K,0)-\max(K-S_T,0)=S_T-K')
    with st.expander('Hint 2 — impose zero net initial premium'):st.latex(r'0=G_0-Ke^{-rT}\quad\Rightarrow\quad K=G_0e^{rT}')
    if st.button('Use the zero-cost strike',key=page+'_use_forward',on_click=lambda:use_forward()):pass
    # callback runs before the next script evaluation, so the strike widget stays consistent.
    if reveal(page):
        st.subheader('Worked solution')
        write(f'Prepaid value G₀ = {m.prepaid():.6f}; fair delivery strike K* = G₀exp(rT) = **{m.forward():.6f}**.')
        write(f'At the currently selected strike {m.k:.6f}, the net premium c₀ − p₀ is {m.gap():+.6f}. At K* it is zero. Buy one call and sell one put with identical strike and maturity.')
        show_frame([{'S_T':s,'Long call':max(s-m.k,0),'Short put':-max(m.k-s,0),'Combined payoff':s-m.k,'Financed profit':s-m.k-m.gap()*math.exp(m.r*m.t)} for s in [90.,m.k,120.]])
        write('At an arbitrary strike, financing the net premium gives S_T − F₀(T). At the fair strike no premium financing is needed. Neither construction eliminates future price risk.')
    st.subheader('Explore the strike')
    kgrid=np.linspace(.7*m.s,1.3*m.s,121)
    fig=go.Figure(go.Scatter(x=kgrid,y=[m.prepaid()-k*math.exp(-m.r*m.t) for k in kgrid],name='c₀ − p₀',line=dict(color='#142B49',width=4)))
    fig.add_hline(y=0);fig.add_vline(x=m.forward(),line_dash='dot',annotation_text='Zero-cost strike')
    fig.update_layout(title='Select the strike where premiums are equal',xaxis_title='Common strike K (per underlying unit)',yaxis_title='Net initial option premium c₀ − p₀ (per unit)')
    st.plotly_chart(plot_style(fig),width='stretch')
    x=np.linspace(0,2*m.k,121)
    chart(x,{'Combined option payoff':x-m.k,'Long call':np.maximum(x-m.k,0),'Short put':-np.maximum(m.k-x,0)},'A right plus an obligation creates a forward payoff','Terminal payoff (per unit)',m.k)
    with st.expander('Textbook comparison — three dividend policies'):
        show_frame([{'Policy':BY_ID[id]['label'],'Fair strike':Market(BY_ID[id]['s'],100,1,.05,BY_ID[id]['mode'],BY_ID[id].get('q',0),tuple(map(tuple,BY_ID[id].get('dividends',[])))).forward()} for id in ['pbs-forward-none','pbs-forward-cash','pbs-forward-yield']])
        st.caption('These are the fixed textbook comparison inputs: S₀ = 100, T = 1, r = 5%; cash dividend $4 at t = 0.5 or yield 4%.')
    calculator(page,m);export_record(page,m,{'fair_forward':m.forward(),'net_premium_at_selected_strike':m.gap()})
    st.subheader('What we learned')
    write('The fair forward delivery price is recovered by selecting the strike where c₀ − p₀ = 0. It follows from replication and carry, not from a volatility estimate or a forecast of future spot. Equal premiums can still require collateral and create losses.')

def use_forward():
    p='forwards';v=lambda k:st.session_state[p+'_'+k]
    ds=tuple((v(f'd{i}'),v(f'dt{i}')) for i in [1,2] if v(f'd{i}')>0) if v('mode')=='cash' else ()
    try:
        m=Market(v('s'),v('k'),v('t'),v('r')/100,v('mode'),v('q')/100,ds)
        st.session_state[p+'_k']=m.forward();invalidate(p)
    except ValueError:pass  # The normal page validation provides the visible error.

def pricing():
    page='pricing';ex=case_picker(page);m=controls(page,pricing=True);vol=st.session_state[page+'_vol']/100
    result=black_scholes(m,vol);bounds=m.bounds()
    attempt(page,'Before calculating: what is the call premium per underlying unit?',result['call'])
    with st.expander('Hint 1 — distinguish spot from prepaid value'):write('Select G₀ using the dividend policy. Currency options use the foreign interest rate as q and the domestic rate for strike discounting.')
    with st.expander('Hint 2 — use the model and check it'):
        st.latex(r'd_1=\frac{\ln(G_0/K)+(r+\sigma^2/2)T}{\sigma\sqrt T},\quad d_2=d_1-\sigma\sqrt T')
        st.latex(r'c_0=G_0N(d_1)-Ke^{-rT}N(d_2),\quad p_0=Ke^{-rT}N(-d_2)-G_0N(-d_1)')
    if m.mode=='cash':st.warning('Cash-dividend model qualification: parity is exact under the trading assumptions. Pricing with spot minus dividend PV is generally an approximation under fixed dividend jumps; it is exact only under an appropriate lognormal prepaid-asset model.')
    if reveal(page):
        st.subheader('Worked solution')
        write(f'1. G₀ = {result["g"]:.6f}; PV(K) = {result["b"]:.6f}.')
        if vol>0:write(f'2. d₁ = {result["d1"]:.6f}; d₂ = {result["d2"]:.6f}; N(d₁) = {result["nd1"]:.6f}; N(d₂) = {result["nd2"]:.6f}.')
        else:write('2. At zero volatility use the deterministic discounted payoff limit; d₁ and d₂ are not defined.')
        write(f'3. Call = **{result["call"]:.6f}**; put = **{result["put"]:.6f}**, per unit.')
        write(f'4. Parity check: c₀ − p₀ = {result["call"]-result["put"]:.6f}; G₀ − PV(K) = {m.gap():.6f}.')
    st.subheader('Calculator outputs and price checks')
    show_frame([{'Contract':'Call','Model price':result['call'],'Spot intrinsic':max(m.s-m.k,0),'Lower bound':bounds['call_lower'],'Upper bound':bounds['call_upper']},
                {'Contract':'Put','Model price':result['put'],'Spot intrinsic':max(m.k-m.s,0),'Lower bound':bounds['put_lower'],'Upper bound':bounds['put_upper']}])
    st.caption('A bound is a restriction, not an exact price. European exercise occurs at T; a price below spot intrinsic value is not automatically an arbitrage. Model outputs are not executable market quotes.')
    if vol>0:calculator(page,m,{'sigma':vol,'d1':result['d1'],'d2':result['d2'],'c0':result['call'],'p0':result['put']})
    else:calculator(page,m,{'sigma':vol,'c0':result['call'],'p0':result['put']})
    st.subheader('Application portfolio')
    application=st.selectbox('Which business question would you like to investigate?',
        ['Cost of flexibility: volatility and maturity','Price versus intrinsic value and bounds','Currency purchase: forward versus call insurance'],key=page+'_application')
    if application=='Cost of flexibility: volatility and maturity':
        write('Predict how price changes before running the comparison. Hold all other inputs fixed. More volatility increases both premiums; more maturity need not increase every European premium.')
        runs=[]
        for v in [.15,.30,.45]:
            res=black_scholes(m,v);runs.append({'Experiment':'Volatility','T (years)':m.t,'σ (decimal)':v,'Call':res['call'],'Put':res['put']})
        # Cash schedules must precede each expiration. Omit invalid horizons explicitly.
        for t in [.25,.5,1.]:
            alt=Market(m.s,m.k,t,m.r,m.mode,m.q,m.dividends)
            try:res=black_scholes(alt,vol)
            except ValueError:st.caption(f'Maturity T={t:g} omitted: an active cash dividend would occur at or after expiration.');continue
            runs.append({'Experiment':'Maturity','T (years)':t,'σ (decimal)':vol,'Call':res['call'],'Put':res['put']})
        show_frame(runs)
        fig=go.Figure()
        for name,param in [('Call','call'),('Put','put')]:
            values=[black_scholes(m,float(v))[param] for v in np.linspace(0,1,41)]
            fig.add_trace(go.Scatter(x=np.linspace(0,100,41),y=values,name=name,mode='lines',line=dict(color='#142B49' if param=='call' else '#007F86',dash='solid' if param=='call' else 'dash')))
        fig.update_layout(title='Insurance value as annual volatility changes',xaxis_title='Annual volatility σ (%)',yaxis_title='Model premium (per underlying unit)')
        st.plotly_chart(plot_style(fig),width='stretch')
        if ex['id']=='pbs-put-maturity':st.info('Textbook counterexample: with all other preset inputs fixed, the one-year European put is cheaper than the three-month put because strike-receipt delay dominates extra uncertainty.')
    elif application=='Price versus intrinsic value and bounds':
        low=max(.05*m.k, m.dividend_pv()+.01) if m.mode=='cash' else .05*m.k
        spots=np.linspace(low,max(1.7*m.k,m.s*1.3),101)
        contract=st.radio('Contract to plot',['Call','Put'],horizontal=True,key=page+'_plot_contract')
        key='call' if contract=='Call' else 'put';vals=[];lbs=[];ivs=[]
        for s in spots:
            alt=Market(float(s),m.k,m.t,m.r,m.mode,m.q,m.dividends)
            vals.append(black_scholes(alt,vol)[key]);lbs.append(alt.bounds()[key+'_lower']);ivs.append(max(s-m.k,0) if key=='call' else max(m.k-s,0))
        fig=go.Figure()
        for name,y,color,dash in [('Model price',vals,'#142B49','solid'),('Spot intrinsic',ivs,'#007F86','dash'),('Lower bound',lbs,'#B04700','dot')]:fig.add_trace(go.Scatter(x=spots,y=y,name=name,line=dict(color=color,dash=dash,width=3)))
        fig.update_layout(title=f'European {contract.lower()} price, intrinsic value, and bound',xaxis_title='Spot S₀ (per underlying unit)',yaxis_title='Value today (per underlying unit)')
        fig.add_vline(x=m.k,line_dash='dot',annotation_text='Strike');fig.add_hline(y=0)
        st.plotly_chart(plot_style(fig),width='stretch')
    else:
        fx=BY_ID['pbs-bs-fx'];base=Market(fx['s'],fx['k'],fx['t'],fx['r'],'yield',fx['q'])
        write('Textbook currency application: buy 100,000 euros in six months; $1.10/euro spot; domestic 5%, foreign 3%, volatility 12%. Both hedges below use the fair forward strike. These are public practice inputs.')
        hedge=hedge_costs(base,fx['vol'],fx['quantity'],[.90,1.10,1.30]);show_frame(hedge['rows'])
        write(f'Fair strike = ${hedge["k"]:.6f}/euro. Matching call and put premiums = ${hedge["call"]:.6f}/euro. Call-only premium today = ${hedge["premium"]:,.2f}; terminal financed premium = ${hedge["carried_premium"]:,.2f}. Synthetic forward net premium = zero.')
        write('Buy 100,000 calls and sell 100,000 matching puts to fix purchase cost. Buy 100,000 calls alone to preserve savings if the euro falls, paying a premium for that flexibility. Recommend one under a stated risk objective; consider cash availability, collateral, settlement timing, and model assumptions.')
        x=np.linspace(.7,1.5,81);h=hedge_costs(base,fx['vol'],fx['quantity'],x)
        chart(x,{'Synthetic forward + purchase':[r['Synthetic forward + purchase'] for r in h['rows']],
                 'Call + purchase, financed premium':[r['Long call + purchase, premium financed'] for r in h['rows']],
                 'Unhedged purchase':[r['Unhedged purchase'] for r in h['rows']]},'Terminal cost of purchasing 100,000 euros','Total terminal US dollar cost',hedge['k'])
        st.caption('Horizontal axis: expiration exchange rate, US dollars per euro. Long option cash settlements reduce the purchase cost; the short put can add an obligation. The call-only ceiling includes premium financing.')
    export_record(page,m,{'volatility':vol,'model':result,'bounds':bounds})
    st.subheader('What we learned')
    write('Black–Scholes supplies prices under extra dynamics assumptions. Use the correct units and dividend treatment, then check parity and bounds. Choose a hedge by the business exposure and desired flexibility, not by a model premium alone.')

def quiz_reset():
    for key in list(st.session_state):
        if key.startswith('quiz_') and key not in ['quiz_mode','quiz_topic','quiz_round']:del st.session_state[key]

def new_review():
    st.session_state['quiz_round']=st.session_state.get('quiz_round',0)+1;quiz_reset()

def retry_question(qid):
    for suffix in ['answer','checked','show']:st.session_state.pop('quiz_'+qid+'_'+suffix,None)

def practice():
    st.info('**Objective:** explain replication, carry, pricing, bounds, and hedge decisions. This is ungraded practice with hints, walkthroughs, and unrestricted navigation.')
    mode=st.radio('Practice route',['Topic practice','Mixed 10-question review'],horizontal=True,key='quiz_mode',on_change=quiz_reset)
    if mode=='Topic practice':
        topic=st.selectbox('Topic',TOPICS,key='quiz_topic',on_change=quiz_reset);bank=[q for q in QUESTIONS if q['topic']==topic]
    else:
        rng=random.Random(710+st.session_state.get('quiz_round',0));bank=[]
        for topic in TOPICS:bank+=rng.sample([q for q in QUESTIONS if q['topic']==topic],2)
        rng.shuffle(bank);st.button('Start a new mixed review',on_click=new_review)
        st.caption('Two questions from each topic. A new review changes the selection; no answers are transmitted or graded.')
    choices=[q['id'] for q in bank]
    if st.session_state.get('quiz_current') not in choices:st.session_state['quiz_current']=choices[0]
    qid=st.selectbox('Go directly to a question',choices,key='quiz_current',format_func=lambda x:f'{choices.index(x)+1} · '+next(q['topic'] for q in bank if q['id']==x))
    q=next(q for q in bank if q['id']==qid);st.subheader(f'Question {choices.index(qid)+1} of {len(bank)}')
    write(q['prompt'])
    order=list(range(4));random.Random(qid+str(st.session_state.get('quiz_round',0))).shuffle(order)
    st.radio('Choose an answer',order,index=None,format_func=lambda x:q['choices'][x],key='quiz_'+qid+'_answer',on_change=lambda:st.session_state.pop('quiz_'+qid+'_checked',None))
    cols=st.columns(3)
    with cols[0]:
        if st.button('Check answer'):
            selected=st.session_state.get('quiz_'+qid+'_answer')
            if selected is None:st.warning('Choose an answer, or reveal the explanation directly.')
            else:st.session_state['quiz_'+qid+'_checked']=selected;st.session_state.setdefault('quiz_results',{})[qid]=(selected==q['answer'])
    with cols[1]:st.button('Retry this question',on_click=retry_question,args=(qid,))
    with cols[2]:
        if st.button('Reveal full explanation'):st.session_state['quiz_'+qid+'_show']=True
    checked=st.session_state.get('quiz_'+qid+'_checked')
    if checked is not None:
        (st.success if checked==q['answer'] else st.warning)(('Correct. ' if checked==q['answer'] else 'Try again. ')+q['explanations'][checked])
    with st.expander('Hint'):write(q['hint'])
    if st.session_state.get('quiz_'+qid+'_show'):
        for ix in order:write(('**Correct:** ' if ix==q['answer'] else '**Why this distractor is wrong:** ')+q['choices'][ix]+' — '+q['explanations'][ix])
    results=st.session_state.get('quiz_results',{});attempted=[q for q in choices if q in results];correct=sum(results[q] for q in attempted)
    st.caption(f'In this route: {len(attempted)} questions checked; {correct} correct on the latest checked attempt. Revealing an explanation does not count as a checked answer. Results last only for this session.')
    st.subheader('What we learned')
    write('Can you identify the dated cash flows, reproduce them, and explain which claims require a pricing model? Return to any module for further investigation; no correct-answer gate blocks your progress.')

def orientation():
    write('A manager wants to insure a position or lock the cost of a future purchase. Can calls, puts, stock, and funding create the same protection? This studio links those business decisions to payoff replication and model valuation.')
    st.info('**Prerequisites:** European call and put payoffs, long and short positions, and present value. All examples are hypothetical.')
    st.subheader('Your learning route')
    show_frame([{'Module':PAGES[p],'Core minutes':minutes,'Deliverable':goal} for p,minutes,goal in [
        ('parity',15,'Build a synthetic put and verify its payoff'),('dividends',20,'Cancel arbitrage cash flows at each dividend date'),('forwards',15,'Recover the strike where c₀ − p₀ = 0'),('pricing',15,'Check model prices and justify a hedge'),('comparisons',10,'Compare three maturities or volatilities against bounds'),('practice',10,'Explain the core ideas through a mixed review')]])
    write('Allow 5 minutes for this orientation, making a 90-minute core route. Additional applications and extensions are optional; the studio need not be completed in one sitting.')
    st.subheader('How to work')
    write('Start with the exposure and predict a result. Enter a numerical attempt if useful, request progressively stronger hints, or reveal the complete walkthrough immediately. Explore new inputs and explain what changed. Reset returns every module to its textbook preset. Module 6 ends the route with multiple-choice practice.')
    write('Use the application menu in Module 4 for volatility and maturity experiments, price-bound comparisons, and a euro purchase hedge. Its extension example shows why a longer European put can be cheaper.')
    st.subheader('Conventions')
    st.latex(r'c_0-p_0=G_0-Ke^{-rT},\qquad F_0(T)=G_0e^{rT}')
    write('Rates in input controls are percentages; the formula calculator uses decimals. T and dividend dates are years. Values are per underlying unit unless a total amount is explicitly labeled. Positive cash flows are received, negative cash flows paid. Financed terminal results carry today’s premiums to expiration.')
    st.caption('Ungraded practice only. Session work is temporary; download experiment records if you need them. The studio collects no identity or grades. Assessed homework is completed through the course submission workflow.')

requested=st.query_params.get('page','start')
if 'navigation' not in st.session_state:st.session_state['navigation']=requested if requested in PAGES else 'start'
def navigate():
    st.query_params.clear();st.query_params['page']=st.session_state['navigation']
st.sidebar.title('Parity and Black–Scholes')
page=st.sidebar.radio('Studio modules',list(PAGES),format_func=lambda x:PAGES[x],key='navigation',on_change=navigate)
st.query_params['page']=page
st.sidebar.caption('European options · hypothetical examples · ungraded practice')
st.title('Parity and Black–Scholes Learning Studio' if page=='start' else PAGES[page])
try:{'start':orientation,'parity':replication,'dividends':dividends,'forwards':forwards,'pricing':pricing,'comparisons':comparisons,'practice':practice}[page]()
except ValueError as e:st.warning(str(e));write('Correct the inputs above or reset to the textbook example. Other modules remain available.')
