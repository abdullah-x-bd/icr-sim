const assert=require("node:assert/strict");
const {evaluateSettlement,coalitionCheck,emptyInputs}=require("../models/settlement.js");
const close=(x,y)=>assert.ok(Math.abs(x-y)<1e-7,String(x)+" vs "+String(y));
const data=emptyInputs();
for(const mode of ["uniform","reciprocal_net","cost_recovery","host_cost_plus","bilateral_surplus"]){
 const r=evaluateSettlement({...data,method:mode});
 close(r.profits.reduce((a,b)=>a+b,0),r.totalSurplus);
 close(r.accountingError,0);
 assert.ok(r.pairs.every(p=>p.totalGB>0&&p.guest!==p.host));
}
const gross=evaluateSettlement({...data,method:"uniform"});
const netted=evaluateSettlement({...data,method:"reciprocal_net"});
gross.profits.forEach((x,i)=>close(x,netted.profits[i]));
const bargaining=evaluateSettlement({...data,method:"bilateral_surplus"});
assert.ok(bargaining.allWin);
assert.ok(bargaining.pairs.every(p=>p.feasible));
for(const p of bargaining.pairs){
 close(p.proposedPayment,p.lower+.5*p.surplus);
 assert.ok(p.proposedRate>=p.breakEvenRate-1e-7);
 assert.ok(p.proposedRate<=p.maxGuestRate+1e-7);
}
assert.ok(!coalitionCheck(bargaining.profits,{1:99999}).coreStable);
assert.ok(coalitionCheck(bargaining.profits,{}).coreStable);
console.log("Settlement tests passed: tariff bounds, budget balance, reciprocity equivalence and coalition diagnostics.");
