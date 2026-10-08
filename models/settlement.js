"use strict";

/**
 * ICR-OPT analytical settlement model.
 * Financial flows are incremental to a declared no-agreement baseline.
 * Arrays use operator indices 0..3 and time indices 0=off-peak, 1=peak.
 * Volumes are GB, monetary amounts and rates are consistent arbitrary units.
 *
 * This component prices a FIXED traffic allocation. It does not infer
 * physical network coverage or choose network routing.
 */
function evaluateSettlement(input) {
  const n=4;
  const q=input.volumes;
  const b=input.guestValuePerGB;
  const c=input.hostVariablePerGB;
  const fh=input.hostFixedPerPair;
  const fg=input.guestFixedPerPair;
  const method=input.method||"bilateral_surplus";
  const flat=Number(input.commonRate||0);
  const markup=Number(input.hostCostMarkup||0.2);
  const alpha=Number(input.hostSurplusShare??0.5);
  if(!Array.isArray(q)||q.length!==n)throw Error("Expected 4x4 directed volumes");
  if(!(alpha>=0&&alpha<=1))throw Error("Host bargaining share must be in [0,1]");
  const pairs=[],pay=Array.from({length:n},()=>Array(n).fill(0));
  for(let i=0;i<n;i++)for(let j=0;j<n;j++) {
    const periods=(q[i]||[])[j]||[0,0];
    const volumes=[0,1].map(t=>Number(periods[t]||0));
    if(volumes.some(x=>!Number.isFinite(x)||x<0))throw Error("Invalid traffic");
    const total=volumes[0]+volumes[1];
    if(i===j&&total>1e-9)throw Error("Self-roaming is not a billable agreement");
    if(total<=1e-9)continue;
    const hostCost=volumes.reduce((s,x,t)=>s+x*Number(c[j][t]),0);
    const guestBenefit=volumes.reduce((s,x)=>s+x*Number(b[i]),0);
    const hostFixed=Number(fh[j]),guestFixed=Number(fg[i]);
    const lower=hostCost+hostFixed,upper=guestBenefit-guestFixed;
    const surplus=upper-lower;
    let totalPayment;
    if(method==="bilateral_surplus") totalPayment=lower+alpha*surplus;
    else if(method==="cost_recovery")totalPayment=lower;
    else if(method==="host_cost_plus")totalPayment=(hostCost+hostFixed)*(1+markup);
    else if(method==="uniform"||method==="reciprocal_net")totalPayment=flat*total;
    else throw Error("Unknown settlement method");
    pay[i][j]=totalPayment;
    pairs.push({guest:i,host:j,offpeakGB:volumes[0],peakGB:volumes[1],
      totalGB:total,hostCost,guestBenefit,hostFixed,guestFixed,lower,upper,
      breakEvenRate:lower/total,maxGuestRate:upper/total,
      surplus,feasible:surplus>=-1e-9,
      proposedPayment:totalPayment,proposedRate:totalPayment/total});
  }
  if(method==="reciprocal_net"){
    // Algebraic cash netting retains signed net transfers, not zero economic costs.
    for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
      const d=pay[i][j]-pay[j][i];
      pay[i][j]=Math.max(0,d);pay[j][i]=Math.max(0,-d);
    }
  }
  const profits=Array(n).fill(0),guestProfit=Array(n).fill(0),hostProfit=Array(n).fill(0);
  for(const p of pairs){
    const i=p.guest,j=p.host;
    guestProfit[i]+=p.guestBenefit-p.guestFixed;
    hostProfit[j]-=p.hostCost+p.hostFixed;
  }
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){
    guestProfit[i]-=pay[i][j];hostProfit[j]+=pay[i][j];
  }
  for(let i=0;i<n;i++)profits[i]=guestProfit[i]+hostProfit[i];
  const totalSurplus=pairs.reduce((s,p)=>s+p.surplus,0);
  const paid=pay.flat().reduce((s,x)=>s+x,0);
  const accountingError=Math.abs(profits.reduce((s,v)=>s+v,0)-totalSurplus);
  return {pairs,profits,guestProfit,hostProfit,totalSurplus,accountingError,
    transfers:pay,grossPayments:paid,allWin:profits.every(v=>v>=-1e-7),
    allPairwiseFeasible:pairs.every(p=>p.feasible),method};
}
function coalitionCheck(profits,coalitionValue) {
  if(profits.length!==4)throw Error("Expected four operator gains");
  const blocked=[];
  for(let mask=1;mask<15;mask++){
    const members=Array.from({length:4},(_,i)=>i).filter(i=>(mask>>i)&1);
    const currentlyReceived=members.reduce((s,i)=>s+profits[i],0);
    const couldEarn=Number(coalitionValue[mask]||0);
    if(couldEarn>currentlyReceived+1e-7)
      blocked.push({mask,members,couldEarn,currentlyReceived,gap:couldEarn-currentlyReceived});
  }
  return {coreStable:blocked.length===0,blocked};
}
function emptyInputs(){
  const volume=[[ [0,0],[115,45],[55,25],[0,0] ],
    [[30,15],[0,0],[0,0],[85,35]],
    [[45,12],[80,30],[0,0],[60,18]],
    [[120,40],[0,0],[50,18],[0,0]]];
  return {
    volumes:volume, guestValuePerGB:[7.5,6.2,7.3,8.1],
    hostVariablePerGB:[[2.2,3.3],[2.6,4.5],[1.9,3.1],[3.1,5.1]],
    hostFixedPerPair:[75,120,85,150],guestFixedPerPair:[50,55,45,60],
    hostSurplusShare:0.5,commonRate:4.0,hostCostMarkup:0.2
  };
}
if(typeof module!=="undefined"&&module.exports)module.exports={evaluateSettlement,coalitionCheck,emptyInputs};
