(function(root){
"use strict";
const OBSERVED={
 route:"Deorali Bazar to Nathu La Pass, NH 310",
 date:"8-9 May 2026",length_km:66.5,
 source:"https://www.pib.gov.in/PressReleasePage.aspx?PRID=2280639&lang=1&reg=3",
 operators:{
  Airtel:{poor:4584,total:13089,dl:41.60,ul:7.51},
  BSNL:{poor:6087,total:14797,dl:6.68,ul:3.34},
  Jio:{poor:1711,total:8802,dl:60.26,ul:7.50},
  Vi:{poor:3597,total:7563,dl:13.79,ul:4.86}
 }
};
function defaults(){
 return {
  guest:"BSNL",monthlyGB:25.51,exposedSubscriberDays:3000,
  corridorUsageShare:0.45,weakToUnusable:0.75,attachSuccess:0.85,
  peakDemandShare:0.35,guestValue:5.25,guestOutsideValue:0.60,
  hostShare:0.50,dependence:"independent",pricePrecision:2,
  hosts:{
   Airtel:{cost:2.0,offScarcity:0.30,peakScarcity:1.0,offCapacity:300,peakCapacity:130,hostFixed:180,guestFixed:70},
   Jio:{cost:1.6,offScarcity:0.30,peakScarcity:2.0,offCapacity:360,peakCapacity:110,hostFixed:220,guestFixed:80},
   Vi:{cost:2.6,offScarcity:0.20,peakScarcity:0.80,offCapacity:220,peakCapacity:80,hostFixed:130,guestFixed:70}
  }
 };
}
const finite=(v,def=0)=>{const n=Number(v);return Number.isFinite(n)?n:def};
function clamp(x,lo,hi){return Math.max(lo,Math.min(hi,x))}
function conditionalEligibility(home,host,model){
 const a=home.poor/home.total,b=host.poor/host.total;
 const joint=model==="lower"?Math.max(0,a-b):
             model==="upper"?Math.min(a,1-b):a*(1-b);
 return a>0?clamp(joint/a,0,1):0;
}
function normalized(cfg){
 const c=Object.assign(defaults(),cfg||{});
 c.hosts=Object.assign({},defaults().hosts,cfg&&cfg.hosts||{});
 for(const j of Object.keys(defaults().hosts))c.hosts[j]=Object.assign({},defaults().hosts[j],c.hosts[j]||{});
 c.peakDemandShare=clamp(finite(c.peakDemandShare,.35),0,1);
 c.corridorUsageShare=clamp(finite(c.corridorUsageShare,.45),0,1);
 c.weakToUnusable=clamp(finite(c.weakToUnusable,.75),0,1);
 c.attachSuccess=clamp(finite(c.attachSuccess,.85),0,1);
 c.hostShare=clamp(finite(c.hostShare,.5),0,1);
 c.exposedSubscriberDays=Math.max(0,finite(c.exposedSubscriberDays,0));
 c.monthlyGB=Math.max(0,finite(c.monthlyGB,0));
 c.guestValue=finite(c.guestValue,0);
 c.guestOutsideValue=finite(c.guestOutsideValue,0);
 if(!OBSERVED.operators[c.guest])throw Error("Unknown guest");
 if(!["lower","independent","upper"].includes(c.dependence))throw Error("Bad overlap scenario");
 for(const j of Object.keys(c.hosts)){
  const h=c.hosts[j];
  for(const k of ["cost","offScarcity","peakScarcity","offCapacity","peakCapacity","hostFixed","guestFixed"]){
   h[k]=Math.max(0,finite(h[k],0));
  }
 }
 return c;
}
function evaluate(input){
 const c=normalized(input),home=OBSERVED.operators[c.guest],bad=home.poor/home.total,hosts=Object.keys(c.hosts).filter(j=>j!==c.guest);
 const baseGB=c.exposedSubscriberDays*c.monthlyGB/30*c.corridorUsageShare*bad*c.weakToUnusable;
 const demand={off:baseGB*(1-c.peakDemandShare),peak:baseGB*c.peakDemandShare};
 const eligible=Object.fromEntries(hosts.map(j=>[j,conditionalEligibility(home,OBSERVED.operators[j],c.dependence)*c.attachSuccess]));
 const choices=[null,...hosts];let candidates=[],best=null;
 for(const off of choices)for(const peak of choices){
  let pairVolumes={},flows=[],variableSurplus=0;
  for(const period of ["off","peak"]){
   const j=period==="off"?off:peak;if(!j)continue;
   const h=c.hosts[j],capacity=h[period+"Capacity"];
   const q=Math.max(0,Math.min(capacity,demand[period]*eligible[j]));
   if(q<=1e-10)continue;
   const unitHostCost=h.cost+h[period==="off"?"offScarcity":"peakScarcity"];
   pairVolumes[j]=(pairVolumes[j]||0)+q;
   flows.push({period,host:j,gb:q,hostUnitCost:unitHostCost});
   variableSurplus+=q*(c.guestValue-c.guestOutsideValue-unitHostCost);
  }
  let agreementFixedCost=0;
  for(const j of Object.keys(pairVolumes))agreementFixedCost+=c.hosts[j].hostFixed+c.hosts[j].guestFixed;
  const pricing=flows.map(flow=>{
   const h=c.hosts[flow.host],q=flow.gb,pairQ=pairVolumes[flow.host];
   const floor=flow.hostUnitCost+h.hostFixed/pairQ;
   const ceiling=c.guestValue-c.guestOutsideValue-h.guestFixed/pairQ;
   const feasible=floor<=ceiling+1e-9;
   const tariff=feasible?floor+c.hostShare*(ceiling-floor):null;
   const hostGain=feasible?q*(tariff-flow.hostUnitCost)-h.hostFixed*q/pairQ:null;
   const guestGain=feasible?q*(c.guestValue-c.guestOutsideValue-tariff)-h.guestFixed*q/pairQ:null;
   return Object.assign({},flow,{floor,ceiling,tariff,feasible,hostGain,guestGain});
  });
  const priceFeasible=pricing.every(p=>p.feasible);
  const surplus=variableSurplus-agreementFixedCost;
  const valid=priceFeasible&&surplus>=-1e-8;
  const result={off:off||"none",peak:peak||"none",flows:pricing,agreementFixedCost,surplus,valid,
   carriedGB:flows.reduce((s,x)=>s+x.gb,0),
   guestGain:pricing.reduce((s,p)=>s+(p.guestGain||0),0),
   hostGains:Object.fromEntries(hosts.map(j=>[j,pricing.filter(p=>p.host===j).reduce((s,p)=>s+(p.hostGain||0),0)]))};
  candidates.push(result);
  if(valid&&(!best||surplus>best.surplus+1e-9))best=result;
 }
 // The all-zero agreement is always available.
 const selected=best||candidates.find(q=>q.off==="none"&&q.peak==="none");
 const bounds=Object.fromEntries(hosts.map(j=>[j,conditionalEligibility(home,OBSERVED.operators[j],c.dependence)]));
 const potential=hosts.map(j=>{
  const fraction=bounds[j],h=c.hosts[j],totalDemand=demand.off+demand.peak;
  return {host:j,conditionalShare:fraction,effectiveEligibility:eligible[j],
    theoreticalGB:totalDemand*fraction,eligibleGB:totalDemand*eligible[j],
    variableCostOff:h.cost+h.offScarcity,variableCostPeak:h.cost+h.peakScarcity};
 });
 const expectedCost=selected.flows.reduce((s,p)=>s+p.gb*p.hostUnitCost,0);
 return {inputs:c,observed:OBSERVED,weakShare:bad,baseCandidateGB:baseGB,periodDemandGB:demand,
  eligibleFractions:bounds,potential,selected,totalCost:expectedCost+selected.agreementFixedCost,
  avoidedOrRecoveredGB:selected.carriedGB,
  maxPossibleGB:baseGB,
  fractionRecovered:baseGB>0?selected.carriedGB/baseGB:0,
  allCandidates:candidates,validCandidates:candidates.filter(x=>x.valid).length,
  accountingResidual:Math.abs(selected.surplus-selected.guestGain-Object.values(selected.hostGains).reduce((a,b)=>a+b,0)),
  inputStatuses:{
   operatorSignal:"OBSERVED_MARGINAL_TRAI",
   benchmarkUsage:"PUBLISHED_NATIONAL_TRAI",
   trafficExposed:"SCENARIO_ASSUMPTION",
   physicalOverlap:"UNOBSERVED_SCENARIO_BOUNDS",
   networkAvailability:"SCENARIO_ASSUMPTION",
   hostCostsAndBenefits:"SCENARIO_ASSUMPTION"
  }};
}
function scenarios(){
 const b=defaults();
 const low=JSON.parse(JSON.stringify(b));low.exposedSubscriberDays=900;low.guestValue=3.0;low.weakToUnusable=.5;low.dependence="lower";
 for(const h of Object.values(low.hosts)){h.cost*=1.4;h.peakScarcity*=1.7;h.offScarcity*=1.4;}
 const high=JSON.parse(JSON.stringify(b));high.exposedSubscriberDays=6500;high.guestValue=7.0;high.dependence="upper";high.weakToUnusable=.9;
 for(const h of Object.values(high.hosts)){h.cost*=.8;h.peakScarcity*=.7;h.offScarcity*=.7;}
 return {conservative:low,central:b,optimistic:high};
}
const api={OBSERVED,defaults,normalized,conditionalEligibility,evaluate,scenarios};
if(typeof module!=="undefined"&&module.exports)module.exports=api;
root.ICR_SIKKIM=api;
})(typeof globalThis!=="undefined"?globalThis:this);
