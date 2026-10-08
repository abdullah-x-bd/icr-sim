const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, 'Expected a self-contained simulator script');
const source = match[1].replace(/init\(\);window\.ICR_OPT_TEST=\{[^;]+;/, '');
const ctx = vm.createContext({console, Math, Number, Array, Object, JSON, Set, Map, Intl, Date});
vm.runInContext(source, ctx);

const getScenario = name => JSON.parse(vm.runInContext('JSON.stringify(SCENARIOS)', ctx))[name];
const getPreset = name => {
  ctx.preset = name;
  return JSON.parse(vm.runInContext('JSON.stringify(icrEconomicPreset(preset))', ctx));
};
function simulate(config) {
  ctx.config = config;
  return vm.runInContext('simulate(config)', ctx);
}
function price(result, config, economicConfig) {
  ctx.result = result;
  ctx.caseConfig = {...config,econ:economicConfig};
  return vm.runInContext('analyzeTariffs(result,caseConfig)', ctx);
}
function close(actual, expected, tolerance=1e-5) {
  assert.ok(Math.abs(actual-expected) <= tolerance, String(actual)+' differs from '+String(expected));
}
function sum(a) {return a.reduce((v,x)=>v+x,0);}

for (const name of ['sparse','high95','peak','complement','blackspots']) {
  const s = getScenario(name);
  const r = simulate(s);
  const p = price(r,s,getPreset('neutral'));
  close(p.privateSurplus,r.totals.privateBenefit-r.totals.hostCost);
  close(p.privateSurplus,sum(p.posted));
  close(p.privateSurplus,sum(p.cooperative)-p.subsidy);
  close(sum(p.clearing),0);
  assert.ok(p.accountingError < 1e-5);
  if(p.bilateralFeasible) {
    assert.ok(p.quoted.every(x=>x>=-1e-5));
    close(sum(p.quoted),p.privateSurplus);
  }
  for(const pair of p.pairs) {
    close(sum(pair.rows.map(v=>v.units)),pair.units);
    close(sum(pair.rows.map(v=>v.hostFixed)),pair.fixedHost);
    close(sum(pair.rows.map(v=>v.guestFixed)),pair.fixedGuest);
    for(const row of pair.rows) {
      if(row.feasible) {
        assert.ok(row.tariff>=row.floor-1e-8);
        assert.ok(row.tariff<=row.ceiling+1e-8);
      } else {
        assert.equal(row.tariff,null);
      }
    }
  }
  for(const group of p.groups)close(sum(group.ids.map(i=>p.clearing[i])),0);
}

const sparse = getScenario('sparse'), base = simulate(sparse);
const original = price(base,sparse,getPreset('neutral'));
const scarcity = price(base,sparse,getPreset('scarcity'));
const integration = price(base,sparse,getPreset('integration'));
const fallback = price(base,sparse,getPreset('fallback'));
assert.ok(scarcity.privateSurplus<original.privateSurplus);
assert.ok(integration.privateSurplus<original.privateSurplus);
assert.ok(fallback.privateSurplus<0);
assert.ok(scarcity.blocked>0);
assert.ok(integration.blocked>0);
assert.ok(fallback.subsidy>0);

const oldT1T2 = original.byPair[0][1].rows.find(v=>v.time==='peak');
const newT1T2 = scarcity.byPair[0][1].rows.find(v=>v.time==='peak');
assert.ok(newT1T2.floor>oldT1T2.floor);
assert.ok(newT1T2.ceiling<oldT1T2.ceiling);
assert.equal(newT1T2.feasible,false);

const conversion=getPreset('neutral');conversion.gbPerUnit=10;
const changedUnits=price(base,sparse,conversion);
close(original.privateSurplus,changedUnits.privateSurplus);
close(original.byPair[0][1].rows[0].floor/10,changedUnits.byPair[0][1].rows[0].floor);

const split=getPreset('neutral');split.hostSplit=90;
const higherHost=price(base,sparse,split);
close(higherHost.privateSurplus,original.privateSurplus);
assert.ok(higherHost.byPair[0][1].rows[0].tariff>original.byPair[0][1].rows[0].tariff);
close(sum(higherHost.quoted),higherHost.privateSurplus);

const zero=simulate({...sparse,mode:'none'});
const noRoaming=price(zero,sparse,getPreset('neutral'));
assert.equal(noRoaming.pairs.length,0);
assert.equal(noRoaming.quotes,0);
assert.equal(noRoaming.subsidy,0);

console.log('ICR-OPT 1.1 pricing tests passed: bounds, fixed costs, scarcity, surplus, clearing, conversions and zero flow.');
