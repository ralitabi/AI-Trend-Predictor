/* ══════════════════════════════════════════════════════════════════
   AI Trend Predictor — Frontend v4
   Multi-currency · Multi-unit · RSI · Bollinger Bands · MACD · ATR
   ══════════════════════════════════════════════════════════════════ */

/* ══ CONSTANTS ══════════════════════════════════════════════════════ */

const CURRENCIES = {
  USD: { symbol:'$',   name:'US Dollar',     decimals:2 },
  EUR: { symbol:'€',   name:'Euro',           decimals:2 },
  GBP: { symbol:'£',   name:'Pound',          decimals:2 },
  PKR: { symbol:'₨',   name:'Pakistani Rupee',decimals:0 },
  SAR: { symbol:'SR',  name:'Saudi Riyal',    decimals:2 },
  AED: { symbol:'AED ',name:'UAE Dirham',     decimals:2 },
  INR: { symbol:'₹',   name:'Indian Rupee',   decimals:0 },
  CNY: { symbol:'¥',   name:'Chinese Yuan',   decimals:2 },
  JPY: { symbol:'¥',   name:'Japanese Yen',   decimals:0 },
  KWD: { symbol:'KD',  name:'Kuwaiti Dinar',  decimals:3 },
  QAR: { symbol:'QR',  name:'Qatari Riyal',   decimals:2 },
  OMR: { symbol:'OMR ',name:'Omani Rial',      decimals:3 },
  BHD: { symbol:'BD',  name:'Bahraini Dinar', decimals:3 },
  EGP: { symbol:'E£',  name:'Egyptian Pound', decimals:2 },
  BDT: { symbol:'৳',   name:'Bangladeshi Taka',decimals:0 },
  MYR: { symbol:'RM',  name:'Malaysian Ringgit',decimals:2 },
  TRY: { symbol:'₺',   name:'Turkish Lira',   decimals:2 },
};

// All sizes relative to 1 troy ounce (for gold) or natural unit
const UNITS = {
  gold: [
    { id:'oz',      label:'Troy Ounce',         factor:1,          desc:'31.10 grams — standard global unit' },
    { id:'gram',    label:'Gram (g)',            factor:1/31.1035,  desc:'1 gram of gold' },
    { id:'10g',     label:'10 Gram Bar',         factor:10/31.1035, desc:'Common retail bar — 10g' },
    { id:'tola',    label:'Tola (11.66g) 🇵🇰🇮🇳', factor:11.6638/31.1035, desc:'South Asian standard — 11.66 grams' },
    { id:'mithqal', label:'Mithqal (4.25g) 🇸🇦',  factor:4.25/31.1035,    desc:'Middle Eastern unit — 4.25 grams' },
    { id:'tael',    label:'Tael HK (37.43g) 🇭🇰', factor:37.429/31.1035,  desc:'Chinese/SE Asian — 37.43 grams' },
    { id:'kg',      label:'Kilogram (1000g)',    factor:32.1507,    desc:'1 kilogram = 32.15 troy ounces' },
    { id:'100g',    label:'100 Gram Bar',        factor:100/31.1035,desc:'Standard investment bar — 100g' },
  ],
  sp500: [
    { id:'index',  label:'Index Points',   factor:1,     desc:'S&P 500 index level' },
    { id:'spy',    label:'SPY ETF (≈1/10)',factor:0.1,   desc:'SPDR S&P 500 ETF — roughly 1/10 index' },
    { id:'mini',   label:'E-mini Contract',factor:50,    desc:'E-mini futures = 50× the index' },
    { id:'micro',  label:'Micro E-mini',   factor:5,     desc:'Micro E-mini = 5× the index' },
  ],
  bitcoin: [
    { id:'btc',    label:'Bitcoin (BTC)',   factor:1,          desc:'1 whole Bitcoin' },
    { id:'mbtc',   label:'mBTC (0.001 BTC)',factor:0.001,       desc:'1 millibitcoin = 0.001 BTC' },
    { id:'ksat',   label:'1,000 Satoshi',  factor:1/100000,    desc:'1,000 satoshi = 0.00001 BTC' },
    { id:'sat',    label:'Satoshi',        factor:1/100000000, desc:'Smallest Bitcoin unit — 0.00000001 BTC' },
  ],
};

const ASSET_INFO = {
  gold:    { name:'Gold',    pair:'XAU/USD', baseUnit:'oz' },
  sp500:   { name:'S&P 500', pair:'INDEX',   baseUnit:'index' },
  bitcoin: { name:'Bitcoin', pair:'BTC/USD', baseUnit:'btc' },
};

/* ══ THEME UTILITIES ════════════════════════════════════════════════ */
function isDark() { return document.documentElement.dataset.theme === 'dark'; }
function C(key) {
  const D = { green:'#10B981',red:'#EF4444',gold:'#F59E0B',blue:'#3B82F6',purple:'#8B5CF6',teal:'#14B8A6',text:'#EEF2FF',muted:'#7C95C8' };
  const L = { green:'#059669',red:'#DC2626',gold:'#D97706',blue:'#2563EB',purple:'#7C3AED',teal:'#0F766E',text:'#0F172A',muted:'#64748B' };
  return (isDark()?D:L)[key]||'#888';
}
const ASSET_COLORS = {
  gold:    ()=>isDark()?'#F59E0B':'#D97706',
  sp500:   ()=>isDark()?'#3B82F6':'#2563EB',
  bitcoin: ()=>isDark()?'#8B5CF6':'#7C3AED',
};

/* ══ CHART LAYOUT ═══════════════════════════════════════════════════ */
function CL(extra={}) {
  const dark=isDark();
  return {
    paper_bgcolor:'rgba(0,0,0,0)',
    plot_bgcolor:dark?'rgba(13,22,48,0.9)':'rgba(248,250,252,0.95)',
    font:{family:"'Inter','Segoe UI',system-ui,sans-serif",color:dark?'#EEF2FF':'#0F172A',size:12},
    xaxis:{gridcolor:dark?'rgba(255,255,255,0.04)':'rgba(15,23,42,0.05)',linecolor:dark?'rgba(255,255,255,0.08)':'rgba(15,23,42,0.1)',zeroline:false,tickfont:{color:dark?'#7C95C8':'#64748B',size:11}},
    yaxis:{gridcolor:dark?'rgba(255,255,255,0.04)':'rgba(15,23,42,0.05)',linecolor:dark?'rgba(255,255,255,0.08)':'rgba(15,23,42,0.1)',zeroline:false,tickfont:{color:dark?'#7C95C8':'#64748B',size:11}},
    margin:{l:62,r:18,t:30,b:44},
    legend:{bgcolor:'rgba(0,0,0,0)',bordercolor:'rgba(0,0,0,0)',orientation:'h',yanchor:'bottom',y:1.01,xanchor:'right',x:1,font:{size:11,color:dark?'#7C95C8':'#64748B'}},
    hoverlabel:{bgcolor:dark?'#111E3A':'#FFFFFF',bordercolor:dark?'rgba(56,114,255,0.2)':'rgba(15,23,42,0.1)',font:{size:12,color:dark?'#EEF2FF':'#0F172A'}},
    ...extra,
  };
}

/* ══ PURE UTILITIES ═════════════════════════════════════════════════ */
function hexRgb(h){const r=/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(h);return r?`${parseInt(r[1],16)},${parseInt(r[2],16)},${parseInt(r[3],16)}`:'200,200,200';}
function pct(v,d=1){if(v==null)return'—';return v>=0?`+${v.toFixed(d)}%`:`${v.toFixed(d)}%`;}
function linspace(a,b,n){return Array.from({length:n},(_,i)=>a+(b-a)*i/(n-1));}
function pearson(a,b){const n=Math.min(a.length,b.length);if(!n)return 0;const ma=a.slice(-n).reduce((s,v)=>s+v,0)/n,mb=b.slice(-n).reduce((s,v)=>s+v,0)/n;let num=0,da2=0,db2=0;for(let i=0;i<n;i++){const ai=a[a.length-n+i]-ma,bi=b[b.length-n+i]-mb;num+=ai*bi;da2+=ai*ai;db2+=bi*bi;}return da2&&db2?num/Math.sqrt(da2*db2):0;}
function evaluate(metric,value){
  const R={
    sharpe:   [{t:1.5,g:'green',i:'🟢',l:'Strong'},{t:0.5,g:'gold',i:'🟡',l:'Fair'},{t:-99,g:'red',i:'🔴',l:'Weak'}],
    volatility:[{t:12,g:'green',i:'🟢',l:'Calm'},{t:20,g:'gold',i:'🟡',l:'Moderate'},{t:999,g:'red',i:'🔴',l:'Volatile'}],
    drawdown: [{t:-8,g:'green',i:'🟢',l:'Mild'},{t:-20,g:'gold',i:'🟡',l:'Moderate'},{t:-999,g:'red',i:'🔴',l:'Severe'}],
    return:   [{t:10,g:'green',i:'🟢',l:'Strong'},{t:0,g:'gold',i:'🟡',l:'Neutral'},{t:-999,g:'red',i:'🔴',l:'Negative'}],
    rsi:      [{t:30,g:'green',i:'🟢',l:'Oversold — Buy Zone'},{t:70,g:'gold',i:'🟡',l:'Neutral'},{t:999,g:'red',i:'🔴',l:'Overbought — Sell Zone'}],
  };
  const set=R[metric];if(!set)return{g:'blue',i:'⚪',l:''};
  if(metric==='volatility'||metric==='rsi')return set.find(r=>value<r.t)||set[set.length-1];
  if(metric==='drawdown')return set.find(r=>value>r.t)||set[set.length-1];
  return set.find(r=>value>=r.t)||set[set.length-1];
}
function kpiCard({lbl,val,sub,icon,color,statusIcon='',statusLbl='',statusColor=''}){
  const sHtml=statusLbl?`<span class="kpi-status" style="background:${statusColor}18;color:${statusColor};border:1px solid ${statusColor}33">${statusIcon} ${statusLbl}</span>`:'';
  return`<div class="kpi-card"><div class="kpi-top-bar" style="background:${color}55"></div><div class="kpi-icon-row"><div class="kpi-icon-box" style="background:${color}18">${icon}</div><span class="kpi-lbl">${lbl}</span></div><div class="kpi-val" style="color:${color}">${val}</div><div class="kpi-sub">${sub}</div>${sHtml}</div>`;
}
function plot(id,traces,layout){Plotly.react(id,traces,layout,{responsive:true,displayModeBar:false});}

/* ══ APP CONTROLLER ═════════════════════════════════════════════════ */
const App = {
  currentAsset: 'gold',
  riskProfile:  'Moderate',
  forecastDays:  7,
  apiKey:        '',
  currency:      'USD',
  sizeUnit:      'oz',
  exchangeRates: { USD:1 },
  _cache:        {},
  _showBB:       true,
  _showMA:       true,

  /* ── Initialise ── */
  async init() {
    const saved=localStorage.getItem('ai-theme');
    const sys=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
    this._applyTheme(saved||sys);
    this._showLoader(true);
    await this.loadExchangeRates();
    await this.loadTicker();
    await this.switchAsset('gold',true);
    this._showLoader(false);
    setInterval(()=>this.loadTicker(),60000);
    setInterval(()=>this.loadExchangeRates(),3600000); // refresh rates hourly
  },

  /* ── Exchange rates ── */
  async loadExchangeRates() {
    try {
      const rates=await fetch('/api/exchange-rates').then(r=>r.json());
      this.exchangeRates={USD:1,...rates};
      this._updateConvBar();
    } catch(e){ console.warn('FX rates error',e); }
  },

  /* ── PRICE CONVERSION ENGINE ── */
  getPriceConversion() {
    const fxRate = this.exchangeRates[this.currency] ?? 1;
    const units  = UNITS[this.currentAsset] || UNITS.gold;
    const unit   = units.find(u=>u.id===this.sizeUnit) || units[0];
    return fxRate * unit.factor;
  },
  getCurrencySymbol() { return CURRENCIES[this.currency]?.symbol ?? '$'; },
  getCurrencyDecimals() {
    const base = CURRENCIES[this.currency]?.decimals ?? 2;
    // For very small units (Satoshi) always show 4+ decimals
    if (this.sizeUnit==='sat') return 6;
    if (this.sizeUnit==='ksat') return 4;
    return base;
  },
  getSizeLabel() {
    const units=UNITS[this.currentAsset]||UNITS.gold;
    return (units.find(u=>u.id===this.sizeUnit)||units[0]).label;
  },
  /* Convert a USD price to the current currency + size */
  cvt(usdPrice) {
    if (usdPrice==null||isNaN(usdPrice)) return null;
    return usdPrice * this.getPriceConversion();
  },
  /* Format a converted price */
  fmt(usdPrice) {
    const v=this.cvt(usdPrice);
    if (v==null) return '—';
    const sym=this.getCurrencySymbol();
    const dec=this.getCurrencyDecimals();
    if (Math.abs(v)>=1e9)  return `${sym}${(v/1e9).toFixed(2)}B`;
    if (Math.abs(v)>=1e6)  return `${sym}${(v/1e6).toFixed(2)}M`;
    if (Math.abs(v)>=1000) return `${sym}${v.toLocaleString('en',{maximumFractionDigits:dec<2?0:dec})}`;
    if (Math.abs(v)>=1)    return `${sym}${v.toFixed(Math.max(dec,2))}`;
    return `${sym}${v.toFixed(6)}`;
  },
  /* Apply conversion to a whole array of USD prices */
  cvtArr(arr) {
    const k=this.getPriceConversion();
    return (arr||[]).map(v=>v==null||isNaN(v)?null:v*k);
  },
  /* Y-axis tick prefix */
  yAxisFmt() {
    const sym=this.getCurrencySymbol();
    const dec=this.getCurrencyDecimals();
    return { tickprefix:sym, tickformat:`,.${Math.max(0,dec-1)}f` };
  },

  /* ── Currency & Size change handlers ── */
  changeCurrency(c) {
    this.currency=c;
    localStorage.setItem('ai-currency',c);
    this._updateConvBar();
    this._reRenderAll();
  },
  changeSize(s) {
    this.sizeUnit=s;
    this._updateConvBar();
    this._reRenderAll();
  },
  _updateConvBar() {
    const rate=this.exchangeRates[this.currency]??1;
    const sym=this.getCurrencySymbol();
    const fxRate=this.currency==='USD'?'1:1':`1 USD = ${sym}${rate.toLocaleString('en',{maximumFractionDigits:4})}`;
    const unitInfo=UNITS[this.currentAsset]?.find(u=>u.id===this.sizeUnit);
    const unitDesc=unitInfo?` · ${unitInfo.desc}`:'';
    const keyStatus=this.apiKey?'✓ GPT-4o active':'No AI key';
    document.getElementById('convBar').innerHTML=
      `<span class="conv-chip">💱 ${this.currency}</span>
       <span>${fxRate}</span>
       <span class="conv-sep">·</span>
       <span class="conv-chip">📏 ${this.getSizeLabel()}</span>
       <span>${unitDesc}</span>
       <span class="conv-sep">·</span>
       <span style="color:var(--text3)">${keyStatus}</span>`;
  },
  _updateSizeOptions(asset) {
    const sel=document.getElementById('sizeSelect');
    if(!sel)return;
    const units=UNITS[asset]||UNITS.gold;
    sel.innerHTML=units.map(u=>`<option value="${u.id}">${u.label}</option>`).join('');
    // Restore default for this asset
    const defaults={gold:'oz',sp500:'index',bitcoin:'btc'};
    const def=defaults[asset]||'oz';
    sel.value=this._cache[`size_${asset}`]||def;
    this.sizeUnit=sel.value;
  },

  /* ── Theme ── */
  toggleTheme(){
    const next=isDark()?'light':'dark';
    this._applyTheme(next);
    localStorage.setItem('ai-theme',next);
    setTimeout(()=>this._reRenderAll(),60);
  },
  _applyTheme(t){
    document.documentElement.setAttribute('data-theme',t);
    const btn=document.getElementById('themeIcon');
    if(btn) btn.textContent=t==='dark'?'☀️':'🌙';
  },
  _reRenderAll(){
    const a=this.currentAsset, cd=this._cache;
    if(cd[`data_${a}`])               this._buildOverviewCharts(cd[`data_${a}`],a);
    if(cd[`pred_${a}_${this.forecastDays}`]) this._buildForecastChart(cd[`pred_${a}_${this.forecastDays}`],a);
    if(cd[`risk_${a}`])               this._buildRiskCharts(cd[`risk_${a}`],a);
    if(cd['compare'])                 this._buildCompareCharts(cd['compare']);
    // Re-render text prices
    if(cd[`data_${a}`])               this._renderHero(cd[`data_${a}`],a);
    if(cd[`data_${a}`])               this._renderTopKpis(cd[`data_${a}`],a);
    if(cd[`risk_${a}`])               this._renderRiskKpis(cd[`risk_${a}`]);
    if(cd[`sug_${a}`])                this._renderTargets(cd[`sug_${a}`]);
    this._updateConvBar();
  },
  _showLoader(on){const el=document.getElementById('pageLoader');if(el)el.style.display=on?'flex':'none';},

  /* ── Toggles ── */
  toggleBollinger(){this._showBB=document.getElementById('toggleBB')?.checked??true;const d=this._cache[`data_${this.currentAsset}`];if(d)this._buildOverviewCharts(d,this.currentAsset);},
  toggleMA(){this._showMA=document.getElementById('toggleMA')?.checked??true;const d=this._cache[`data_${this.currentAsset}`];if(d)this._buildOverviewCharts(d,this.currentAsset);},

  /* ── Asset/Tab switching ── */
  async switchAsset(asset,initial=false){
    this.currentAsset=asset;
    document.querySelectorAll('.chip').forEach(c=>c.classList.toggle('active',c.dataset.asset===asset));
    this._updateSizeOptions(asset);
    this._updateConvBar();
    if(!initial){['risk_','pred_','sug_'].forEach(p=>Object.keys(this._cache).filter(k=>k.startsWith(p+asset)).forEach(k=>delete this._cache[k]));}
    await Promise.all([this.loadData(asset),this.loadRisk(asset)]);
    await this.loadForecast();
    await this.loadSuggestion();
  },
  switchTab(tab){
    this._activeTab=tab;
    document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
    document.getElementById(`tab-${tab}`)?.classList.add('active');
    document.querySelector(`.tab-btn[data-tab="${tab}"]`)?.classList.add('active');
    if(tab==='compare')this.loadCompare();
  },

  /* ── API ── */
  async _get(url){if(this._cache[url])return this._cache[url];const r=await fetch(url);if(!r.ok)throw new Error(`API ${r.status}: ${url}`);const d=await r.json();this._cache[url]=d;return d;},

  /* ── TICKER ── */
  async loadTicker(){
    try{
      const data=await fetch('/api/ticker').then(r=>r.json());
      const SYMS={gold:'GOLD',sp500:'SPX',bitcoin:'BTC'};
      let html='';
      for(let i=0;i<4;i++) Object.entries(data).forEach(([key,d])=>{
        const chg=d.change1d,arr=chg>=0?'▲':'▼',clr=chg>=0?C('green'):C('red');
        const price=this.fmt(d.price);
        html+=`<div class="ticker-item"><span class="ticker-sym">${SYMS[key]||key.toUpperCase()}</span><span class="ticker-price">${price}</span><span class="ticker-chg" style="color:${clr}">${arr} ${Math.abs(chg).toFixed(2)}%</span></div>`;
      });
      document.getElementById('tickerTrack').innerHTML=html;
    }catch(e){console.warn('Ticker error',e);}
  },

  /* ══ DATA + OVERVIEW ════════════════════════════════════════════ */
  async loadData(asset){
    try{
      const d=await this._get(`/api/data/${asset}`);
      this._cache[`data_${asset}`]=d;
      this._renderHero(d,asset);
      this._renderSentiment(d,asset);
      this._renderTopKpis(d,asset);
      this._buildOverviewCharts(d,asset);
    }catch(e){console.error('Data error',e);}
  },

  _renderHero(d,asset){
    const aclr=ASSET_COLORS[asset]();
    const info=ASSET_INFO[asset];
    const chg1d=d.chg1d||0,chg5=d.chg5d||0;
    const pos=Math.max(0,Math.min(100,(d.current-d.lo52)/(d.hi52-d.lo52)*100));
    const posLbl=pos<25?'lower quarter':pos<50?'lower half':pos<75?'upper half':'upper quarter';
    let vClass='verdict-neut',vTxt='⚪ Neutral';
    if(chg5>2){vClass='verdict-bull';vTxt='📈 Uptrend';}
    else if(chg5<-2){vClass='verdict-bear';vTxt='📉 Downtrend';}
    document.getElementById('heroBadge').textContent=`${info.pair} · ${this.getSizeLabel()}`;
    document.getElementById('heroVerdict').textContent=vTxt;
    document.getElementById('heroVerdict').className=`hero-verdict ${vClass}`;
    document.getElementById('heroName').textContent=info.name;
    // Main price in selected currency/size
    document.getElementById('heroPrice').textContent=this.fmt(d.current);
    document.getElementById('heroPrice').style.color=aclr;
    // Also show USD price in smaller text inside change row
    const usdPriceSmall=d.current!==this.cvt(d.current)?` <span style="color:var(--text3);font-size:0.7rem">$${d.current.toLocaleString('en',{maximumFractionDigits:2})}</span>`:'';
    const c1Clr=chg1d>=0?'chip-green':'chip-red';
    const c5Clr=chg5>=0?'chip-green':'chip-red';
    document.getElementById('heroChange1d').className=`hero-chip ${c1Clr}`;
    document.getElementById('heroChange1d').innerHTML=`${chg1d>=0?'▲':'▼'} ${Math.abs(chg1d).toFixed(2)}% today${usdPriceSmall}`;
    document.getElementById('heroChange5d').className=`hero-chip hero-chip-sm ${c5Clr}`;
    document.getElementById('heroChange5d').textContent=`5d: ${pct(chg5)}`;
    document.getElementById('rangeLo').textContent=this.fmt(d.lo52);
    document.getElementById('rangeHi').textContent=this.fmt(d.hi52);
    document.getElementById('rangeBarFill').style.width=`${pos}%`;
    document.getElementById('rangeBarThumb').style.left=`${pos}%`;
    document.getElementById('rangePosText').textContent=posLbl;
  },

  _renderSentiment(d,asset){
    const tech=d.tech||{};
    const rsiNow=tech.rsi_now||50,rsiEv=evaluate('rsi',rsiNow);
    const macdBull=tech.macd_signal_now==='Bullish';
    const vol=d.volatility||0;
    const sentData=[
      {icon:d.chg30d>=0?'📈':'📉',title:d.chg30d>=0?'Positive 30-Day Trend':'Negative 30-Day Trend',desc:`${pct(d.chg30d)} over the past month`},
      {icon:rsiEv.i,title:`RSI: ${rsiNow.toFixed(0)} — ${tech.rsi_signal||'Neutral'}`,desc:rsiNow<30?'Potentially undervalued':rsiNow>70?'Potentially overvalued':'No extreme signal'},
      {icon:macdBull?'🟢':'🔴',title:`MACD: ${tech.macd_signal_now||'Neutral'}`,desc:macdBull?'Upward momentum building':'Downward pressure'},
      {icon:vol<12?'😴':vol<20?'😐':'🌪️',title:`Volatility: ${vol.toFixed(1)}%`,desc:vol<12?'Very calm':vol<20?'Normal swings':'Elevated uncertainty'},
    ];
    sentData.forEach((s,i)=>{const el=document.getElementById(`sent${i}`);if(el)el.innerHTML=`<span class="sent-icon">${s.icon}</span><span class="sent-text"><strong>${s.title}</strong>${s.desc}</span>`;});
  },

  _renderTopKpis(d,asset){
    const aclr=ASSET_COLORS[asset]();
    const vol=d.volatility||0,volEv=evaluate('volatility',vol);
    const tech=d.tech||{};
    const rsiNow=tech.rsi_now||50,rsiEv=evaluate('rsi',rsiNow);
    const sym=this.getCurrencySymbol(), unit=this.getSizeLabel();
    document.getElementById('kpiStrip').innerHTML=[
      {lbl:`Price / ${unit}`,       val:this.fmt(d.current),    sub:`52-wk: ${this.fmt(d.lo52)} – ${this.fmt(d.hi52)}`, icon:'💰',color:aclr},
      {lbl:'Today',                  val:pct(d.chg1d),           sub:`Change vs yesterday (USD: $${d.current?.toFixed(2)})`, icon:'📅',color:(d.chg1d||0)>=0?C('green'):C('red')},
      {lbl:'5-Day Change',           val:pct(d.chg5d),           sub:'This week', icon:'📊',color:(d.chg5d||0)>=0?C('green'):C('red')},
      {lbl:'30-Day Change',          val:pct(d.chg30d),          sub:'This month', icon:'📆',color:(d.chg30d||0)>=0?C('blue'):C('red')},
      {lbl:'RSI Momentum',           val:rsiNow.toFixed(0),      sub:tech.rsi_signal||'Neutral', icon:'📡',color:C(rsiEv.g),statusIcon:rsiEv.i,statusLbl:rsiEv.l,statusColor:C(rsiEv.g)},
    ].map(c=>kpiCard(c)).join('');
  },

  /* ── Build all overview charts ── */
  _buildOverviewCharts(d,asset){
    const aclr=ASSET_COLORS[asset]();
    const rgb=hexRgb(aclr);
    const tech=d.tech||{};
    const dates=d.dates;
    const yf=this.yAxisFmt();

    // ── Price + Bollinger Bands + MA ────────────────────────────
    const prices=this.cvtArr(d.prices),ma20=this.cvtArr(d.ma20),ma50=this.cvtArr(d.ma50);
    const bbU=this.cvtArr(tech.bb_upper),bbL=this.cvtArr(tech.bb_lower);
    const traces=[{x:dates,y:prices,name:'Price',type:'scatter',mode:'lines',
      fill:'tozeroy',fillcolor:`rgba(${rgb},0.07)`,line:{color:aclr,width:2.5},
      hovertemplate:`<b>%{x}</b><br>${this.getCurrencySymbol()}%{y:,.${this.getCurrencyDecimals()}f}<extra></extra>`}];
    if(this._showBB&&bbU){
      const bbRgb=hexRgb(C('teal'));
      traces.push(
        {x:dates,y:bbU,name:'BB Upper',type:'scatter',mode:'lines',line:{color:`rgba(${bbRgb},0.5)`,width:1,dash:'dot'},hoverinfo:'skip',showlegend:false},
        {x:dates,y:bbL,name:'BB Lower',type:'scatter',mode:'lines',fill:'tonexty',fillcolor:`rgba(${bbRgb},0.06)`,line:{color:`rgba(${bbRgb},0.5)`,width:1,dash:'dot'},hoverinfo:'skip',legendgroup:'bb',showlegend:false},
        {x:[dates[0]],y:[null],name:'Bollinger Bands',type:'scatter',line:{color:C('teal'),width:1,dash:'dot'},legendgroup:'bb'}
      );
    }
    if(this._showMA){
      if(ma20?.some(v=>v))traces.push({x:dates,y:ma20,name:'MA 20',type:'scatter',mode:'lines',line:{color:C('teal')+'BB',width:1.5,dash:'dot'},hoverinfo:'skip'});
      if(ma50?.some(v=>v))traces.push({x:dates,y:ma50,name:'MA 50',type:'scatter',mode:'lines',line:{color:C('purple')+'BB',width:1.5,dash:'dot'},hoverinfo:'skip'});
    }
    plot('chartPrice',traces,CL({height:380,...yf}));

    // ── RSI ──────────────────────────────────────────────────────
    const rsiNow=tech.rsi_now||50,rsiEv=evaluate('rsi',rsiNow);
    const rsiEl=document.getElementById('rsiGaugeBadge');
    if(rsiEl){const cls=rsiNow<30?'badge-buy':rsiNow>70?'badge-sell':'badge-hold';rsiEl.className=`tech-badge ${cls}`;rsiEl.textContent=`${rsiEv.i} RSI ${rsiNow.toFixed(0)} — ${tech.rsi_signal||'Neutral'}`;}
    if(tech.rsi){
      const rrgb=hexRgb(C(rsiEv.g));
      plot('chartRSI',[{x:dates,y:tech.rsi,name:'RSI (14)',type:'scatter',mode:'lines',
        line:{color:C(rsiEv.g),width:2},hovertemplate:'<b>%{x}</b><br>RSI %{y:.1f}<extra></extra>'}],
        CL({height:220,
          shapes:[
            {type:'rect',x0:dates[0],x1:dates[dates.length-1],y0:70,y1:100,fillcolor:`rgba(${hexRgb(C('red'))},0.06)`,line:{width:0}},
            {type:'rect',x0:dates[0],x1:dates[dates.length-1],y0:0,y1:30,fillcolor:`rgba(${hexRgb(C('green'))},0.06)`,line:{width:0}},
            {type:'line',x0:dates[0],x1:dates[dates.length-1],y0:70,y1:70,line:{color:C('red')+'66',dash:'dot',width:1}},
            {type:'line',x0:dates[0],x1:dates[dates.length-1],y0:30,y1:30,line:{color:C('green')+'66',dash:'dot',width:1}},
          ],
          yaxis:{...CL().yaxis,range:[0,100],tickvals:[30,50,70],ticktext:['30 Oversold','50','70 Overbought'],tickfont:{size:10,color:isDark()?'#7C95C8':'#64748B'}},
        }));
    }

    // ── MACD ─────────────────────────────────────────────────────
    const macdBull=tech.macd_signal_now==='Bullish';
    const macdEl=document.getElementById('macdBadge');
    if(macdEl){macdEl.className=`tech-badge ${macdBull?'badge-buy':'badge-sell'}`;macdEl.textContent=macdBull?'🟢 Bullish momentum':'🔴 Bearish momentum';}
    if(tech.macd){
      const histColors=(tech.macd_hist||[]).map(v=>v>=0?`rgba(${hexRgb(C('green'))},0.8)`:`rgba(${hexRgb(C('red'))},0.8)`);
      plot('chartMACD',[
        {x:dates,y:tech.macd_hist,name:'Histogram',type:'bar',marker:{color:histColors,line:{color:histColors.map(c=>c.replace('0.8','0.4')),width:0.5}},hovertemplate:'<b>%{x}</b><br>Hist %{y:.3f}<extra></extra>'},
        {x:dates,y:tech.macd,name:'MACD',type:'scatter',mode:'lines',line:{color:C('blue'),width:1.5},hovertemplate:'<b>%{x}</b><br>MACD %{y:.3f}<extra></extra>'},
        {x:dates,y:tech.macd_signal,name:'Signal',type:'scatter',mode:'lines',line:{color:C('red'),width:1.5,dash:'dot'},hoverinfo:'skip'},
      ],CL({height:220,shapes:[{type:'line',x0:dates[0],x1:dates[dates.length-1],y0:0,y1:0,line:{color:'rgba(128,128,128,0.35)',width:1}}]}));
    }

    // ── Volatility ────────────────────────────────────────────────
    const rrgb=hexRgb(C('red'));
    plot('chartVol',[{x:d.vol_series?.dates,y:d.vol_series?.values,name:'Ann. Vol %',type:'scatter',mode:'lines',fill:'tozeroy',fillcolor:`rgba(${rrgb},0.10)`,line:{color:C('red'),width:2},hovertemplate:'<b>%{x}</b><br>%{y:.1f}%<extra></extra>'}],
      CL({height:280,yaxis:{...CL().yaxis,ticksuffix:'%'},shapes:[12,20,30].map(l=>({type:'line',x0:0,x1:1,xref:'paper',y0:l,y1:l,line:{color:'rgba(128,128,128,0.3)',dash:'dot',width:1}}))}));

    // ── Returns distribution ──────────────────────────────────────
    const rets=d.returns?.values||[];
    const mu=rets.reduce((a,b)=>a+b,0)/(rets.length||1);
    const sig=Math.sqrt(rets.map(v=>(v-mu)**2).reduce((a,b)=>a+b,0)/(rets.length||1));
    const xs=linspace(Math.min(...rets,-3),Math.max(...rets,3),150);
    const ys=xs.map(v=>(1/(sig*Math.sqrt(2*Math.PI)))*Math.exp(-0.5*((v-mu)/sig)**2));
    const scale=rets.length*(Math.max(...rets,3)-Math.min(...rets,-3))/55;
    const brgb=hexRgb(C('blue'));
    plot('chartRet',[
      {x:rets,type:'histogram',nbinsx:55,name:'Daily Returns',marker:{color:`rgba(${brgb},0.75)`,line:{color:'rgba(128,128,128,0.1)',width:0.5}},hovertemplate:'Return %{x:.2f}%<br>Count %{y}<extra></extra>'},
      {x:xs,y:ys.map(v=>v*scale),type:'scatter',mode:'lines',name:'Normal curve',line:{color:C('gold'),width:2.5},hoverinfo:'skip'},
    ],CL({height:280,bargap:0.06}));

    // ── Monthly bars ──────────────────────────────────────────────
    const mvals=d.monthly?.values||[],mdates=d.monthly?.dates||[];
    const mclrs=mvals.map(v=>v>=0?`rgba(${hexRgb(C('green'))},0.8)`:`rgba(${hexRgb(C('red'))},0.8)`);
    plot('chartMonthly',[{x:mdates,y:mvals,type:'bar',name:'Monthly Return',marker:{color:mclrs,line:{color:mclrs.map(c=>c.replace('0.8','0.4')),width:1}},hovertemplate:'<b>%{x}</b><br>%{y:.2f}%<extra></extra>'}],
      CL({height:240,yaxis:{...CL().yaxis,ticksuffix:'%'},shapes:[{type:'line',x0:0,x1:1,xref:'paper',y0:0,y1:0,line:{color:'rgba(128,128,128,0.4)',width:1}}]}));
  },

  /* ══ FORECAST ════════════════════════════════════════════════════ */
  async loadForecast(){
    const asset=this.currentAsset,days=this.forecastDays;
    try{
      const d=await this._get(`/api/predict/${asset}?days=${days}&use_lstm=false`);
      this._cache[`pred_${asset}_${days}`]=d;
      this._renderForecastKpis(d,days);
      this._buildForecastChart(d,asset);
      this._renderModelTable(d,days);
    }catch(e){console.error('Forecast error',e);}
  },
  _renderForecastKpis(d,days){
    const ens=d.ensemble||[],last=ens[ens.length-1]||d.current,cur=d.current;
    const pchg=(last-cur)/cur*100,pclr=pchg>=0?C('green'):C('red');
    const ciHi=d.ci_upper?.[d.ci_upper.length-1],ciLo=d.ci_lower?.[d.ci_lower.length-1];
    document.getElementById('forecastKpis').innerHTML=[
      {lbl:`Predicted in ${days} Days`,val:this.fmt(last),sub:`Expected: ${pct(pchg)} from today`,icon:'🔮',color:pclr,statusIcon:pchg>=0?'📈':'📉',statusLbl:pchg>=0?'Upward forecast':'Downward forecast',statusColor:pclr},
      {lbl:'Best Case (Top 5%)',       val:this.fmt(ciHi),sub:'Optimistic upper bound',icon:'⬆️',color:C('green')},
      {lbl:'Worst Case (Bottom 5%)',   val:this.fmt(ciLo),sub:'Pessimistic lower bound',icon:'⬇️',color:C('red')},
    ].map(c=>kpiCard(c)).join('');
  },
  _buildForecastChart(d,asset){
    const grgb=hexRgb(C('gold')),yf=this.yAxisFmt();
    const histP=this.cvtArr(d.hist_prices),ensP=this.cvtArr(d.ensemble);
    const ciU=this.cvtArr(d.ci_upper),ciL=this.cvtArr(d.ci_lower);
    const arimP=this.cvtArr(d.arima),propP=this.cvtArr(d.prophet);
    const traces=[{x:d.hist_dates,y:histP,name:'Actual Price',type:'scatter',mode:'lines',line:{color:C('blue'),width:2.5},hovertemplate:`<b>%{x}</b><br>${this.getCurrencySymbol()}%{y:,.0f}<extra></extra>`}];
    if(ciU?.length)traces.push({x:[...d.dates,...[...d.dates].reverse()],y:[...ciU,...[...ciL].reverse()],fill:'toself',fillcolor:`rgba(${grgb},0.12)`,line:{color:'rgba(0,0,0,0)'},name:'90% Confidence Band',hoverinfo:'skip'});
    if(arimP?.length)traces.push({x:d.dates,y:arimP,name:'ARIMA',type:'scatter',mode:'lines',line:{color:C('blue')+'88',width:1.5,dash:'dot'},hoverinfo:'skip'});
    if(propP?.length)traces.push({x:d.dates,y:propP,name:'Prophet',type:'scatter',mode:'lines',line:{color:C('purple')+'88',width:1.5,dash:'dot'},hoverinfo:'skip'});
    traces.push({x:d.dates,y:ensP,name:'AI Forecast',type:'scatter',mode:'lines+markers',line:{color:C('gold'),width:3},marker:{color:C('gold'),size:5},hovertemplate:`<b>%{x}</b><br>${this.getCurrencySymbol()}%{y:,.0f}<extra></extra>`});
    plot('chartForecast',traces,CL({height:420,...yf}));
  },
  _renderModelTable(d,days){
    const cur=d.current||0;
    const models=[{n:'ENSEMBLE (combined)',a:d.ensemble,hl:true},{n:'ARIMA (statistical)',a:d.arima},{n:'Prophet (trend + seasonality)',a:d.prophet}].filter(m=>m.a?.length);
    document.getElementById('modelTable').innerHTML=`<table class="data-table">
      <thead><tr><th>Model</th><th>Tomorrow</th><th>In ${days} Days</th><th>Change %</th><th>Direction</th></tr></thead>
      <tbody>${models.map(m=>{const first=m.a[0],last=m.a[m.a.length-1],delta=(last-cur)/cur*100,clr=delta>=0?C('green'):C('red');
        return`<tr class="${m.hl?'hl':''}"><td><strong style="color:${m.hl?C('gold'):'inherit'}">${m.n}</strong></td>
          <td>${this.fmt(first)}</td><td>${this.fmt(last)}</td>
          <td style="color:${clr};font-weight:700">${delta>=0?'▲':'▼'} ${Math.abs(delta).toFixed(2)}%</td>
          <td style="color:${clr}">${delta>0?'📈 Higher':'📉 Lower'}</td></tr>`;
      }).join('')}</tbody></table>`;
  },

  /* ══ RISK ════════════════════════════════════════════════════════ */
  async loadRisk(asset){
    try{const d=await this._get(`/api/risk/${asset}`);this._cache[`risk_${asset}`]=d;this._renderRiskKpis(d);this._buildRiskCharts(d,asset);this._renderRiskInsight(d);}catch(e){console.error('Risk error',e);}
  },
  _renderRiskKpis(d){
    const shEv=evaluate('sharpe',d.sharpe_ratio||0),vEv=evaluate('volatility',d.volatility_pct||0);
    const ddEv=evaluate('drawdown',d.max_drawdown_pct||0),retEv=evaluate('return',d.annual_return||0);
    document.getElementById('riskKpis').innerHTML=[
      {lbl:'Yearly Return',    val:pct(d.annual_return),                  sub:"YoY performance",                    icon:'📈',color:C(retEv.g),statusIcon:retEv.i,statusLbl:retEv.l,statusColor:C(retEv.g)},
      {lbl:'Price Volatility', val:`${(d.volatility_pct||0).toFixed(1)}%`,sub:d.volatility_classification,          icon:'🌊',color:C(vEv.g), statusIcon:vEv.i, statusLbl:vEv.l, statusColor:C(vEv.g)},
      {lbl:'Quality Score',    val:(d.sharpe_ratio||0).toFixed(2),        sub:'Return vs risk (>1.0 = good)',       icon:'⭐',color:C(shEv.g),statusIcon:shEv.i,statusLbl:shEv.l,statusColor:C(shEv.g)},
      {lbl:'Biggest Drop',     val:`${(d.max_drawdown_pct||0).toFixed(1)}%`,sub:`Worst fall from peak · ${d.max_drawdown_duration_days||0}d`,icon:'📉',color:C(ddEv.g),statusIcon:ddEv.i,statusLbl:ddEv.l,statusColor:C(ddEv.g)},
    ].map(c=>kpiCard(c)).join('');
    document.getElementById('riskKpis2').innerHTML=[
      {lbl:'Daily Risk Limit', val:`${(d.var_95_pct||0).toFixed(2)}%`, sub:'Typical worst-day loss (95% of time)', icon:'🛡️',color:C('purple')},
      {lbl:'Extreme Risk',     val:`${(d.cvar_95_pct||0).toFixed(2)}%`,sub:'Average of worst 5% days',            icon:'⚡',color:C('red')},
      {lbl:'Skewness',         val:(d.skewness||0).toFixed(2),          sub:(d.skewness||0)<0?'Bigger losses possible':'Bigger gains possible',icon:'📐',color:C('gold')},
      {lbl:'ATR / Stop Guide', val:this.fmt(d.atr),                     sub:`${(d.atr_pct||0).toFixed(1)}% of price · used for stops`,icon:'📏',color:C('teal')},
    ].map(c=>kpiCard(c)).join('');
  },
  _buildRiskCharts(d,asset){
    const rrgb=hexRgb(C('red'));
    plot('chartDD',[{x:d.drawdown?.dates,y:d.drawdown?.values,name:'Drawdown %',type:'scatter',mode:'lines',fill:'tozeroy',fillcolor:`rgba(${rrgb},0.15)`,line:{color:C('red'),width:1.5},hovertemplate:'<b>%{x}</b><br>%{y:.2f}%<extra></extra>'}],CL({height:260,yaxis:{...CL().yaxis,ticksuffix:'%'}}));
    plot('chartRiskVol',[{x:d.vol_series?.dates,y:d.vol_series?.values,name:'Volatility %',type:'scatter',mode:'lines',fill:'tozeroy',fillcolor:`rgba(${rrgb},0.10)`,line:{color:C('red'),width:2},hovertemplate:'<b>%{x}</b><br>%{y:.1f}%<extra></extra>'}],CL({height:260}));
  },
  _renderRiskInsight(d){
    const shEv=evaluate('sharpe',d.sharpe_ratio||0);
    document.getElementById('riskInsight').innerHTML=
      `📊 <strong>Plain-English Summary:</strong>
      Quality Score <strong>${(d.sharpe_ratio||0).toFixed(2)}</strong> ${shEv.i} ${shEv.l} —
      ${d.sharpe_ratio>1.5?'excellent return for the risk.':d.sharpe_ratio>0.5?'acceptable return.':'poor risk-adjusted return.'}
      ATR is <strong>${this.fmt(d.atr)}</strong> (${(d.atr_pct||0).toFixed(1)}% of price) — this drives the stop-loss calculation.
      Skewness <strong>${(d.skewness||0).toFixed(2)}</strong>:
      ${(d.skewness||0)<0?'larger losses are statistically more likely than large gains.':'upside surprises slightly more probable.'}`;
  },

  /* ══ SUGGESTIONS ════════════════════════════════════════════════ */
  async loadSuggestion(){
    const asset=this.currentAsset;
    try{
      const d=await this._get(`/api/suggest/${asset}?risk_profile=${encodeURIComponent(this.riskProfile)}&days=${this.forecastDays}`);
      this._cache[`sug_${asset}`]=d;
      this._renderAction(d);this._renderTargets(d);this._renderRationale(d);
    }catch(e){console.error('Suggestion error',e);}
  },
  _renderAction(d){
    const cfg={
      Buy:        {clr:C('green'), bg:'rgba(16,185,129,0.1)',bdr:'rgba(16,185,129,0.4)',label:'▲ BUY',       hint:'Models indicate upside potential'},
      Accumulate: {clr:C('teal'),  bg:'rgba(20,184,166,0.1)',bdr:'rgba(20,184,166,0.4)',label:'◆ ACCUMULATE',hint:'Build position gradually'},
      Hold:       {clr:C('gold'),  bg:'rgba(245,158,11,0.1)',bdr:'rgba(245,158,11,0.4)',label:'● HOLD',       hint:'No strong directional signal'},
      Sell:       {clr:C('red'),   bg:'rgba(239,68,68,0.1)', bdr:'rgba(239,68,68,0.4)', label:'▼ SELL',       hint:'Bearish signal — reduce exposure'},
    };
    const c=cfg[d.action]||cfg.Hold,rClr=d.risk_level==='Low'?C('green'):d.risk_level==='Medium'?C('gold'):C('red');
    document.getElementById('actionCard').innerHTML=`<div class="action-card">
      <div class="action-badge" style="background:${c.bg};border-color:${c.bdr};box-shadow:0 0 40px ${c.clr}22">
        <div class="action-label" style="color:${c.clr}">${c.label}</div><div class="action-hint">${c.hint}</div>
      </div>
      <div class="action-meta">
        <div class="action-meta-item"><span class="action-meta-lbl">Confidence</span><div class="action-meta-val" style="color:${c.clr}">${Math.round((d.confidence||0.65)*100)}%</div></div>
        <div class="action-meta-item"><span class="action-meta-lbl">Risk Level</span><div class="action-meta-val" style="color:${rClr}">${d.risk_level}</div></div>
        <div class="action-meta-item"><span class="action-meta-lbl">Hold Period</span><div class="action-meta-val">${d.holding_period}</div></div>
        <div class="action-meta-item"><span class="action-meta-lbl">Risk/Reward</span><div class="action-meta-val" style="color:${C('gold')}">${(d.risk_reward||0).toFixed(2)}×</div></div>
      </div></div>`;
  },
  _renderTargets(d){
    document.getElementById('priceTargets').innerHTML=[
      {lbl:'Entry Price',   val:this.fmt(d.entry_price), sub:'Current market price',                        c:C('blue'),  hint:'Where you would enter today',                   border:''},
      {lbl:'Price Target',  val:this.fmt(d.target_price),sub:`▲ ${(d.upside_pct||0).toFixed(2)}% upside`,  c:C('green'), hint:`ATR-based · ${(d.risk_reward||0).toFixed(2)}× risk/reward`,border:`1px solid ${C('green')}44`},
      {lbl:'Stop Loss',     val:this.fmt(d.stop_loss),   sub:`▼ ${Math.abs(d.downside_pct||0).toFixed(2)}% below`,c:C('red'), hint:'ATR-based exit to limit losses',       border:`1px solid ${C('red')}44`},
      {lbl:'Risk / Reward', val:`${(d.risk_reward||0).toFixed(2)}×`,sub:'Potential gain ÷ loss',              c:C('gold'),  hint:'>1.5× is generally a good trade setup',        border:''},
    ].map(c=>`<div class="pt-card" style="${c.border?`border:${c.border};`:''}">
      <div class="pt-label">${c.lbl}</div><div class="pt-val" style="color:${c.c}">${c.val}</div>
      <div class="pt-sub" style="color:${c.c}99">${c.sub}</div><div class="pt-rr">${c.hint}</div>
    </div>`).join('');
  },
  _renderRationale(d){document.getElementById('rationale').innerHTML=`<div class="rat-label">Why this suggestion?</div><div class="rat-text">${d.rationale||'—'}</div>`;},

  /* ══ AI REPORT ══════════════════════════════════════════════════ */
  async generateReport(){
    const btn=document.getElementById('genReportBtn');
    btn.disabled=true;btn.innerHTML='<span class="spinner"></span> Writing…';
    document.getElementById('reportContent').innerHTML=`<div class="empty-state"><div class="empty-icon"><span class="spinner" style="width:40px;height:40px;border-width:3px"></span></div><div class="empty-title">GPT-4o is writing your report…</div><div class="empty-sub">10–30 seconds.</div></div>`;
    try{
      const r=await fetch(`/api/report/${this.currentAsset}?risk_profile=${encodeURIComponent(this.riskProfile)}&days=${this.forecastDays}`,{method:'POST'});
      if(!r.ok)throw new Error(await r.text());
      const d=await r.json();
      document.getElementById('reportContent').innerHTML=`
        <div class="report-sec-title">📊 Market Analysis — ${ASSET_INFO[this.currentAsset].name}</div>
        ${marked.parse(d.report)}
        <hr style="border:none;border-top:1px solid var(--border);margin:24px 0">
        <div class="report-sec-title">💡 Personalised Recommendation (${this.riskProfile})</div>
        ${marked.parse(d.recommendation)}`;
    }catch(e){
      document.getElementById('reportContent').innerHTML=`<div class="empty-state"><div class="empty-icon">⚠️</div><div class="empty-title">Report failed</div><div class="empty-sub">${e.message}</div></div>`;
    }finally{btn.disabled=false;btn.innerHTML='✨ Generate Report';}
  },

  /* ══ COMPARE ════════════════════════════════════════════════════ */
  async loadCompare(){
    try{const d=await this._get('/api/compare');this._cache['compare']=d;this._buildCompareCharts(d);this._renderCompareTable(d);}
    catch(e){console.error('Compare error',e);}
  },
  _buildCompareCharts(d){
    const traces=Object.entries(d).map(([key,info])=>({x:info.dates,y:info.normalized,name:info.name,type:'scatter',mode:'lines',line:{color:ASSET_COLORS[key]?.(),width:2.5},hovertemplate:`<b>${info.name}</b><br>%{x}<br>Index: %{y:.1f}<extra></extra>`}));
    plot('chartCompare',traces,CL({height:380,shapes:[{type:'line',x0:0,x1:1,xref:'paper',y0:100,y1:100,line:{color:'rgba(128,128,128,0.35)',dash:'dot',width:1}}]}));
    const names=Object.values(d).map(x=>x.name),rets=Object.values(d).map(x=>x.rets||[]),n=names.length;
    const corr=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>pearson(rets[i],rets[j])));
    plot('chartCorr',[{z:corr,x:names,y:names,type:'heatmap',colorscale:[[0,C('red')],[0.5,isDark()?'#172444':'#F1F5F9'],[1,C('blue')]],zmin:-1,zmax:1,showscale:true,text:corr.map(r=>r.map(v=>v.toFixed(2))),texttemplate:'<b>%{text}</b>',hovertemplate:'%{y} vs %{x}<br>%{z:.3f}<extra></extra>'}],CL({height:280,margin:{l:90,r:20,t:20,b:70}}));
  },
  _renderCompareTable(d){
    const F=[
      {key:'annual_return',   lbl:'Yearly Return',   f:v=>pct(v,1),       hi:'good'},
      {key:'volatility_pct',  lbl:'Volatility',      f:v=>`${v?.toFixed(1)}%`, hi:'bad'},
      {key:'sharpe_ratio',    lbl:'Quality Score',   f:v=>v?.toFixed(2),  hi:'good'},
      {key:'max_drawdown_pct',lbl:'Biggest Drop',    f:v=>`${v?.toFixed(1)}%`, hi:'bad'},
      {key:'var_95_pct',      lbl:'Daily Risk',      f:v=>`${v?.toFixed(2)}%`, hi:'bad'},
      {key:'volatility_classification',lbl:'Risk Level',f:v=>v,hi:null},
    ];
    const entries=Object.entries(d).map(([k,v])=>({key:k,...v}));
    const hdr=`<tr><th>Metric</th>${entries.map(e=>`<th style="color:${ASSET_COLORS[e.key]?.()}">${e.name}</th>`).join('')}</tr>`;
    const rows=F.map(f=>{const vals=entries.map(e=>e.metrics?.[f.key]);let best=null;if(f.hi==='good')best=vals.indexOf(Math.max(...vals.map(v=>v??-Infinity)));if(f.hi==='bad')best=vals.indexOf(Math.min(...vals.map(v=>v??Infinity)));
      return`<tr><td style="color:var(--text2);font-weight:600">${f.lbl}</td>${vals.map((v,i)=>`<td style="${i===best?`color:${C('green')};font-weight:700`:''}">${v!=null?f.f(v):'—'}</td>`).join('')}</tr>`;
    });
    document.getElementById('compareTableBody').innerHTML=`<table class="data-table"><thead>${hdr}</thead><tbody>${rows.join('')}</tbody></table>`;
  },
};

window.addEventListener('DOMContentLoaded', ()=>App.init());
