"""Ungraded practice only. No assessed homework cases or instructor solutions."""

def item(id,topic,prompt,choices,hint):
    # First supplied choice is correct. UI shuffles choice indices reproducibly.
    return dict(id=id,topic=topic,prompt=prompt,choices=[x[0] for x in choices],
                explanations=[x[1] for x in choices],answer=0,hint=hint)

QUESTIONS=[
item('parity-01','Replication','Which package replicates a European put when there are no dividends?',[
 ('Long call, long strike bond, short stock','Its payoff is max(S_T − K, 0) + K − S_T = max(K − S_T, 0).'),
 ('Long call, short strike bond, long stock','The signs on the stock and bond produce a different terminal payoff.'),
 ('Short call, long strike bond, long stock','This package caps the stock at K; it does not create the put alone.'),
 ('Long call alone','A call pays in high-price states; a put pays in low-price states.')], 'Rearrange p₀ = c₀ + PV(K) − S₀.'),
item('parity-02','Replication','At S₀ = K = 100, r = 5%, T = 1, and no dividends, what is c₀ − p₀?',[
 ('4.8771','100 − 100exp(−0.05) = 4.8771.'),('0','Equal spot and strike do not remove the timing difference in strike payment.'),
 ('−4.8771','That reverses the parity signs.'),('5.0000','Continuous compounding gives 4.8771; do not use simple interest here.')], 'Discount the strike before subtracting it from spot.'),
item('parity-03','Replication','Which input is unnecessary for put–call parity under its trading assumptions?',[
 ('Volatility','Parity follows from cash-flow replication without a distributional model.'),('Strike','The bond and option payoffs depend on the matching strike.'),
 ('Maturity','Maturity determines the present value of the strike and dividend treatment.'),('Dividend policy','Interim stock cash flows must be accounted for.')], 'Ask whether parity needs a stock-price model.'),
item('parity-04','Replication','A put is overpriced relative to its call-based synthetic equivalent. What is the appropriate trade?',[
 ('Sell the put and buy the synthetic put','Sell the expensive package, buy the identical cheap cash flows.'),('Buy the put and sell the synthetic put','This buys the expensive package and sells the cheap one.'),
 ('Buy both puts','Two long positions do not cancel future risk.'),('Sell the stock alone','A stock short alone retains price risk.')], 'Buy cheap, sell dear, and match every future cash flow.'),
item('parity-05','Replication','What does stock plus a European put pay at expiration, with strike K?',[
 ('max(S_T, K)','The put fills any gap below K; stock retains upside above K.'),('min(S_T, K)','That describes stock minus a call.'),
 ('S_T − K','That is a long forward payoff.'),('K in every state','Stock plus put still rises when S_T exceeds K.')], 'Add S_T and max(K − S_T, 0).'),
item('parity-06','Replication','Two European option packages have the same terminal payoff but different interim cash flows. Can terminal matching alone establish equal prices?',[
 ('No; cash flows must match at every relevant date','A dividend-date obligation can change the value even if terminal payoffs match.'),
 ('Yes; only expiration matters','This ignores interim receipts and obligations.'),('Yes, provided volatility is equal','Volatility does not cancel a missing dated cash flow.'),
 ('No; European contracts never permit replication','European payoff replication is valid when all cash flows and assumptions match.')], 'Consider dividends owed by a short seller.'),
item('div-01','Dividends','A known dividend D is paid at date t_d before expiration T. What is its value today at continuous rate r?',[
 ('D exp(−r t_d)','Discount from the actual payment date to today.'),('D exp(−r T)','This incorrectly moves the dividend to expiration.'),
 ('D exp[−r(T − t_d)]','This discounts over the remaining interval after the dividend, not to today.'),('D exp(r t_d)','That compounds rather than discounts.')], 'Draw today, the payment date, and expiration on a timeline.'),
item('div-02','Dividends','How do known cash dividends enter the prepaid terminal-share value?',[
 ('G₀ = S₀ − sum of dividend present values','Spot includes both terminal ownership and interim distributions.'),('G₀ = S₀ + sum of dividend present values','Adding dividends double counts their value.'),
 ('G₀ = S₀ exp(−rT)','Riskless discounting is not a substitute for dividend stripping.'),('G₀ = S₀ always','That holds only with no interim distributions.')], 'Strip out the dated cash payments from the ordinary share.'),
item('div-03','Dividends','A trader shorts a dividend-paying share in a synthetic put. How is a known dividend obligation neutralized?',[
 ('Buy a bond paying the dividend at its payment date','The bond receipt offsets compensation owed to the stock lender.'),('Ignore it because options are European','Exercise style does not eliminate short-stock dividend compensation.'),
 ('Buy a bond paying at option expiration only','Cash arrives too late to cancel the intermediate obligation.'),('Receive the dividend from the stock lender','The short seller owes rather than receives that compensation.')], 'Check the sign of the short-stock cash flow on the dividend date.'),
item('div-04','Dividends','With continuous yield q, how many reinvesting index units must be bought today to produce one unit at T?',[
 ('exp(−qT)','Continuous reinvestment grows this quantity to exp(−qT)exp(qT) = 1.'),('1','One unit with reinvestment grows to more than one when q > 0.'),
 ('exp(qT)','This grows an already excessive initial holding.'),('exp(−rT)','Use the distribution yield for asset-unit growth, not the funding rate.')], 'Solve Q₀ exp(qT) = 1.'),
item('div-05','Dividends','For K = S₀, continuous yield q > r, and T > 0, which premium is larger?',[
 ('The put','c₀ − p₀ = S₀[exp(−qT) − exp(−rT)] < 0.'),('The call','The no-dividend positive-rate ordering does not survive q > r.'),
 ('They must be equal','Equality at spot strike requires r = q.'),('It depends only on volatility','The parity difference is independent of volatility.')], 'Compare the two exponential discount factors.'),
item('div-06','Dividends','What is exact about the usual known-cash-dividend treatment?',[
 ('Cash-flow parity is exact under the assumptions; the spot-minus-PV Black–Scholes shortcut generally needs a model qualification','The payoff identity and lognormal-dynamics assumption are different claims.'),
 ('Both parity and the shortcut are always exact under any dynamics','Fixed dividend jumps need not leave the assumed diffusion unchanged.'),
 ('Neither parity nor prepaid value can be derived','Known dated dividends can be stripped out by matched borrowing.'),
 ('Using continuous yield is identical to any cash-dividend schedule','A continuous yield and a fixed dated payment are different policies.')], 'Separate a replication identity from a distributional assumption.'),
item('forward-01','Forwards','What is the expiration payoff of one long call and one short put at the same strike and maturity?',[
 ('S_T − K','The positive and negative price states join into one linear payoff.'),('max(S_T − K, 0)','That omits the short-put obligation.'),
 ('K − S_T','That reverses the position directions.'),('Zero in every state','Zero initial premium is not zero terminal payoff.')], 'Evaluate the package below and above K.'),
item('forward-02','Forwards','Which common strike makes the option package cost zero today?',[
 ('K = G₀ exp(rT)','Setting G₀ − Kexp(−rT) = 0 gives this strike.'),('K = S₀ always','Dividend and interest carry generally move the strike away from spot.'),
 ('K = G₀ exp(−rT)','This discounts instead of undoing the strike discount.'),('K = c₀ + p₀','The sum of option premiums does not determine the forward strike.')], 'Set c₀ − p₀ equal to zero in parity.'),
item('forward-03','Forwards','With S₀ = 100, r = 5%, T = 1, and no dividends, what is the fair forward delivery price?',[
 ('105.1271','100exp(0.05) = 105.1271.'),('100.0000','Spot omits financing carry.'),('95.1229','That discounts spot rather than carrying it forward.'),
 ('5.1271','That is only the forward-minus-spot difference.')], 'The no-dividend forward strike is S₀ exp(rT).'),
item('forward-04','Forwards','What does the fair forward price represent?',[
 ('A delivery price consistent with replication and carry','It fixes the exchange price for delivery at T under the trading assumptions.'),
 ('A guaranteed future spot price','Future spot remains uncertain.'),('Automatically the manager’s forecast','A replication price is not automatically a physical expectation.'),
 ('The premium paid to buy a call','A delivery price and an option premium have different roles.')], 'Distinguish the price agreed today from the spot observed later.'),
item('forward-05','Forwards','The long-call/short-put package has zero net initial premium. Which statement is correct?',[
 ('Future losses and collateral needs can still occur','The short put creates a purchase obligation in low-price states.'),('The package is riskless','Its terminal payoff can be negative.'),
 ('Both individual premiums must be zero','They can both be positive and equal.'),('The put seller has only an exercise right','A put seller has an obligation, not the buyer’s exercise right.')], 'Consider S_T below the fair delivery strike.'),
item('forward-06','Forwards','At another strike K, let a = c₀ − p₀. What is financed terminal profit from the long-call/short-put package?',[
 ('S_T − K − a exp(rT) = S_T − F₀(T)','Borrow a positive premium or invest a negative premium; carry it to T.'),('S_T − K − a','This mixes today’s cost with a future cash flow without financing.'),
 ('S_T − K + a exp(rT)','This reverses the sign of the initial cost.'),('max(S_T − K, 0)','That omits the put and funding.')], 'Treat a as a cost today and convert it to date T.'),
item('pricing-01','Pricing','Annual return variance is 0.09. Which volatility should be entered into Black–Scholes?',[
 ('30%','Volatility is sqrt(0.09) = 0.30.'),('9%','Variance is not volatility.'),('90%','This changes both the definition and scale.'),('0.9%','This divides by 100 again.')], 'σ is standard deviation, while σ² is variance.'),
item('pricing-02','Pricing','Which input is not needed for a standard European Black–Scholes price?',[
 ('The stock’s expected physical return','Replication uses the riskless rate rather than a forecast return.'),('Annual volatility','The distributional dispersion enters option valuation.'),
 ('Time in years','Time affects both discounting and uncertainty.'),('The appropriate dividend yield','Yield changes the prepaid asset value.')], 'Distinguish valuation through replication from forecasting.'),
item('pricing-03','Pricing','Holding spot, strike, maturity, rate, and yield fixed in Black–Scholes, what does higher volatility do?',[
 ('Raises both call and put values','Both payoffs are convex; the holder keeps favorable exercise opportunities.'),('Raises only the call','Puts also benefit from dispersion under these fixed inputs.'),
 ('Lowers both premiums','That reverses the model’s volatility sensitivity.'),('Guarantees a larger realized trading profit','A price comparison is not a guarantee about realized returns.')], 'Think about convex payoffs, not a forecast of direction.'),
item('pricing-04','Pricing','For a currency quote in dollars per euro, which inputs go into the continuous-yield model?',[
 ('r = US dollar rate and q = euro rate','Domestic funding uses dollars; foreign balances accrue at the euro rate.'),('r = euro rate and q = dollar rate','That reverses the quotation interpretation.'),
 ('q = 0 regardless of euro interest','Foreign interest is the yield analogue.'),('r = the difference of rates and q = 0 in every part of the formula','Use separate domestic discounting and foreign prepaid factors.')], 'Identify the currency used to pay the strike.'),
item('pricing-05','Pricing','Does more maturity always increase every European option premium?',[
 ('No; dividend carry and delayed strike receipts can offset additional uncertainty','European puts and dividend-paying calls can provide counterexamples.'),
 ('Yes; more time always dominates every other effect','This ignores strike timing and interim distributions.'),('Only volatility matters','Maturity and financing enter the formula directly.'),
 ('No; every option must decrease with maturity','There is no universal decreasing rule either.')], 'An in-the-money put must wait longer to receive the strike.'),
item('pricing-06','Pricing','Why check put–call parity after calculating model prices?',[
 ('It independently checks input consistency and implementation','The price difference must match the prepaid value minus discounted strike.'),
 ('It proves constant volatility describes the market perfectly','Passing an identity does not validate every dynamics assumption.'),('It determines the stock’s expected return','Parity does not forecast physical returns.'),
 ('It proves the model price is an executable market quote','A model output and an executable quote are different objects.')], 'Separate an internal consistency check from market validation.'),
item('bounds-01','Bounds and decisions','Which is the European call lower bound using prepaid value G₀?',[
 ('max(0, G₀ − K exp(−rT))','Drop the nonnegative put from parity and also enforce nonnegativity.'),('G₀ + K exp(−rT)','Adding both values is not a lower-bound argument.'),
 ('Always max(0, S₀ − K)','Immediate exercise is unavailable and dividends matter.'),('Exactly the Black–Scholes premium','A bound restricts values without determining an exact model price.')], 'Start with c₀ = p₀ + G₀ − PV(K).'),
item('bounds-02','Bounds and decisions','For S₀ = 20, K = 30, and PV(K) = 25 with no dividends, what is the put lower bound?',[
 ('5','max(0, 25 − 20) = 5.'),('10','That is spot intrinsic value, not the discounted-strike bound.'),('25','That is the upper bound for a nonnegative underlying.'),('0','The discounted strike exceeds spot by 5.')], 'Compare the discounted strike with spot.'),
item('bounds-03','Bounds and decisions','A European option is priced below spot intrinsic value. What follows?',[
 ('Check its applicable bounds and exercise restriction before diagnosing arbitrage','European puts and dividend-paying calls can be below intrinsic value.'),
 ('It must always be an arbitrage','This applies the immediate-exercise argument to the wrong exercise style.'),('It must always be fairly priced','It may still violate a stronger applicable bound.'),
 ('Its premium must be negative','A positive price can be below a larger intrinsic value.')], 'Immediate exercise and exercise only at T are different rights.'),
item('bounds-04','Bounds and decisions','A lower bound is below intrinsic value. Does that establish that the actual option price is below intrinsic value?',[
 ('No; calculate or observe the actual price','A lower bound permits values above or below intrinsic value.'),('Yes; the premium equals its lower bound','A bound is generally not an exact price.'),
 ('Yes; every European premium is below intrinsic value','That blanket statement is false.'),('No; bounds cannot help check any quote','Bounds can identify violations without giving the exact price.')], 'A permitted range is not a specific premium.'),
item('bounds-05','Bounds and decisions','A firm must buy euros and wants protection while retaining savings if the euro falls. Which position provides that flexibility?',[
 ('A long euro call','It caps the purchase cost before premium and retains favorable lower spot prices.'),('A long synthetic forward alone','It fixes the purchase cost and gives up the favorable lower spot outcome.'),
 ('A short euro call','The written obligation works against protection in rising-price states.'),('A short euro put alone','It can impose an additional purchase obligation when the euro falls.')], 'Identify the firm’s bad outcome and which right offsets it.'),
item('bounds-06','Bounds and decisions','What is the terminal all-in per-euro cost of buying a euro call for c₀ and purchasing euros at T?',[
 ('min(S_T, K) + c₀ exp(r_d T)','The call payoff offsets spot purchase cost, and the initial premium is carried to T.'),('max(S_T, K) + c₀','This reverses the protection and ignores premium financing.'),
 ('K in all states with no premium cost','That describes a fair forward’s fixed cost, not call insurance.'),('S_T + max(S_T − K, 0)','The long-call payoff reduces the firm’s cost rather than adding to it.')], 'Subtract the cash-settled call payoff from the physical purchase cost.')
]

TOPICS=['Replication','Dividends','Forwards','Pricing','Bounds and decisions']
