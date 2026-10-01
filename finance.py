"""Pure financial functions. All rates are decimals, dates years, prices per unit."""
import ast
import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Market:
    s: float
    k: float
    t: float
    r: float
    mode: str = 'none'
    q: float = 0.0
    dividends: tuple = ()

    def validate(self):
        if not all(math.isfinite(x) for x in [self.s,self.k,self.t,self.r,self.q]):
            raise ValueError('Inputs must be finite numbers.')
        if self.s<=0 or self.k<=0 or self.t<=0:
            raise ValueError('Spot, strike, and maturity must be positive.')
        if self.mode not in ['none','cash','yield']:
            raise ValueError('Choose a valid dividend policy.')
        if not -.5<=self.r<=.5 or not 0<=self.q<=.5:
            raise ValueError('Use a rate between −50% and 50% and a yield between 0% and 50%.')
        if self.mode=='cash':
            for amount,date in self.dividends:
                if not math.isfinite(amount) or not math.isfinite(date) or amount<0 or not 0<date<self.t:
                    raise ValueError('Each cash dividend needs a nonnegative amount and a date strictly before expiration.')
        if self.prepaid_unchecked()<=0:
            raise ValueError('The prepaid value must be positive; lower dividends or raise spot.')

    def dividend_pv(self):
        return sum(a*math.exp(-self.r*d) for a,d in self.dividends) if self.mode=='cash' else 0.0

    def prepaid_unchecked(self):
        return self.s*math.exp(-self.q*self.t) if self.mode=='yield' else self.s-self.dividend_pv()

    def prepaid(self):
        self.validate();return self.prepaid_unchecked()

    def strike_pv(self):return self.k*math.exp(-self.r*self.t)
    def forward(self):return self.prepaid()*math.exp(self.r*self.t)
    def gap(self):return self.prepaid()-self.strike_pv()
    def put(self,call):return call-self.gap()
    def bounds(self):
        g=self.prepaid();b=self.strike_pv()
        return {'call_lower':max(0,g-b),'call_upper':g,'put_lower':max(0,b-g),'put_upper':b}

def normal(x):return .5*(1+math.erf(x/math.sqrt(2)))

def black_scholes(m,vol):
    m.validate()
    if not math.isfinite(vol) or not 0<=vol<=3:
        raise ValueError('Volatility must be between 0% and 300%; enter volatility rather than variance.')
    g=m.prepaid();b=m.strike_pv()
    if vol==0:
        return dict(call=max(0,g-b),put=max(0,b-g),d1=None,d2=None,nd1=None,nd2=None,g=g,b=b)
    d1=(math.log(g/m.k)+(m.r+.5*vol*vol)*m.t)/(vol*math.sqrt(m.t));d2=d1-vol*math.sqrt(m.t)
    c=g*normal(d1)-b*normal(d2);p=b*normal(-d2)-g*normal(-d1)
    return dict(call=c,put=p,d1=d1,d2=d2,nd1=normal(d1),nd2=normal(d2),g=g,b=b)

def payoff_table(k,states):
    return [{'S_T':s,'Stock':s,'Long put':max(k-s,0),'Stock + put':max(k,s),
             'Long call':max(s-k,0),'Bond':k,'Call + bond':max(k,s),
             'Synthetic put':max(s-k,0)+k-s,'Long call − put':s-k} for s in states]

def arbitrage(m,call,put,states):
    """Buy cheap package, sell dear one; full dividend-date cancellation."""
    fair=m.put(call);direction=1 if put>fair else -1
    if abs(put-fair)<1e-10:return []
    columns=['Today']+([f'Dividend {i+1} at t={d:g}' for i,(a,d) in enumerate(m.dividends)] if m.mode=='cash' else [])+[f'S_T = {s:g}' for s in states]
    interim=len(columns)-1-len(states)
    rows=[]
    def add(name,today,at_div,terminal):rows.append(dict(Position=name,**dict(zip(columns,[today]+at_div+terminal))))
    add(('Buy' if direction==1 else 'Sell')+' call',-direction*call,[0.]*interim,[direction*max(s-m.k,0) for s in states])
    add(('Sell' if direction==1 else 'Buy')+' put',direction*put,[0.]*interim,[-direction*max(m.k-s,0) for s in states])
    stock='reinvesting position' if m.mode=='yield' else 'stock'
    add(('Short' if direction==1 else 'Buy')+' '+stock,direction*(m.prepaid() if m.mode=='yield' else m.s),[-direction*a for a,d in m.dividends] if m.mode=='cash' else [],[-direction*s for s in states])
    add(('Lend' if direction==1 else 'Borrow')+' strike PV',-direction*m.strike_pv(),[0.]*interim,[direction*m.k]*len(states))
    if m.mode=='cash':
        for i,(a,date) in enumerate(m.dividends):
            at=[0.]*interim;at[i]=direction*a
            add(('Lend' if direction==1 else 'Borrow')+f' dividend {i+1} PV',-direction*a*math.exp(-m.r*date),at,[0.]*len(states))
    rows.append(dict(Position='Total',**{col:sum(row[col] for row in rows) for col in columns}))
    return rows

def hedge_costs(m,vol,quantity,states):
    """Call at fair forward strike; cash settlement offsets physical purchase."""
    k=m.forward();matched=Market(m.s,k,m.t,m.r,m.mode,m.q,m.dividends)
    price=black_scholes(matched,vol);carry=quantity*price['call']*math.exp(m.r*m.t)
    rows=[{'S_T':s,'Unhedged purchase':quantity*s,'Synthetic forward + purchase':quantity*k,
           'Long call + purchase, premium financed':quantity*min(s,k)+carry} for s in states]
    return dict(k=k,call=price['call'],put=price['put'],premium=quantity*price['call'],carried_premium=carry,rows=rows)

def calculate(expression,variables):
    """Bounded arithmetic AST; no eval, imports, attributes, or Python execution."""
    if len(expression)>300:raise ValueError('Keep the expression under 300 characters.')
    try:tree=ast.parse(expression.replace('^','**'),mode='eval')
    except SyntaxError:raise ValueError('Check the expression syntax.') from None
    if sum(1 for _ in ast.walk(tree))>100:raise ValueError('The expression is too complex.')
    functions={'exp':math.exp,'sqrt':math.sqrt,'ln':math.log,'log':math.log,'N':normal,'abs':abs,'max':max,'min':min}
    def visit(node):
        if isinstance(node,ast.Constant) and type(node.value) in [int,float]:value=float(node.value)
        elif isinstance(node,ast.Name) and node.id in variables:value=float(variables[node.id])
        elif isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
            value=visit(node.operand)*(1 if isinstance(node.op,ast.UAdd) else -1)
        elif isinstance(node,ast.BinOp):
            a,b=visit(node.left),visit(node.right)
            if isinstance(node.op,ast.Add):value=a+b
            elif isinstance(node.op,ast.Sub):value=a-b
            elif isinstance(node.op,ast.Mult):value=a*b
            elif isinstance(node.op,ast.Div):value=a/b
            elif isinstance(node.op,ast.Pow):
                if abs(b)>100 or (a<0 and not b.is_integer()):raise ValueError('Use a modest real-valued exponent.')
                value=a**b
            else:raise ValueError('Only arithmetic operators are supported.')
        elif isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in functions and not node.keywords:
            if len(node.args)>5:raise ValueError('Too many function arguments.')
            value=functions[node.func.id](*[visit(x) for x in node.args])
        else:raise ValueError('Use the listed variable names and arithmetic functions only.')
        if not isinstance(value,(int,float)) or not math.isfinite(value) or abs(value)>1e100:raise ValueError('Result is outside the calculator range.')
        return value
    try:return visit(tree.body)
    except (ArithmeticError,TypeError):raise ValueError('Check division, function arguments, and numerical range.') from None
