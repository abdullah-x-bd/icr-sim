const assert=require("node:assert/strict");
const model=require("../sikkim-model.js");
const near=(a,b,t=1e-7)=>assert.ok(Math.abs(a-b)<t,String(a)+" vs "+String(b));
const obs=model.OBSERVED.operators;
near(obs.BSNL.poor/obs.BSNL.total,6087/14797);
for(const host of ["Airtel","Jio","Vi"]){
 const lower=model.conditionalEligibility(obs.BSNL,obs[host],"lower");
 const middle=model.conditionalEligibility(obs.BSNL,obs[host],"independent");
 const upper=model.conditionalEligibility(obs.BSNL,obs[host],"upper");
 assert.ok(lower<=middle&&middle<=upper);
 assert.ok(lower>=0&&upper<=1);
}
for(const [name,config] of Object.entries(model.scenarios())){
 const r=model.evaluate(config),feasible=r.allCandidates.filter(c=>c.valid);
 assert.equal(r.allCandidates.length,16);
 near(r.selected.surplus,Math.max(...feasible.map(c=>c.surplus)));
 assert.ok(r.selected.surplus>=-1e-8,name);
 near(r.accountingResidual,0);
 for(const f of r.selected.flows){
  assert.ok(f.feasible&&f.gb>=0);
  assert.ok(f.floor<=f.tariff+1e-8&&f.tariff<=f.ceiling+1e-8);
  assert.ok(f.guestGain>=-1e-8&&f.hostGain>=-1e-8);
  assert.ok(f.gb<=config.hosts[f.host][f.period+"Capacity"]+1e-8);
 }
}
const def=model.defaults(),baseline=model.evaluate(def);
assert.equal(baseline.selected.off,"Airtel");
assert.equal(baseline.selected.peak,"Airtel");
near(baseline.selected.carriedGB,195.61431793611655,1e-5);
near(baseline.selected.surplus,161.7681392555254,1e-5);
const noValue=model.defaults();noValue.guestValue=0;
assert.equal(model.evaluate(noValue).selected.flows.length,0);
const noDemand=model.defaults();noDemand.exposedSubscriberDays=0;
assert.equal(model.evaluate(noDemand).selected.flows.length,0);
const noCapacity=model.defaults();for(const h of Object.values(noCapacity.hosts)){h.offCapacity=0;h.peakCapacity=0;}
assert.equal(model.evaluate(noCapacity).selected.flows.length,0);
const prohibitive=model.defaults();for(const h of Object.values(prohibitive.hosts))h.hostFixed=1e6;
assert.equal(model.evaluate(prohibitive).selected.flows.length,0);
const split=model.defaults();split.hostShare=.9;
near(model.evaluate(split).selected.surplus,baseline.selected.surplus);
console.log("Sikkim corridor tests passed: evidence ratios, uncertainty bounds, all scenario optimizations, profit transfers, price ranges, capacity constraints and rejection logic.");
