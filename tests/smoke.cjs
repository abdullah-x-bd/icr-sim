const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const match = html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match, 'The simulator must include an inline script');
const source = match[1].replace(/init\(\);window\.ICR_OPT_TEST=\{[^;]+;/, '');
const context = vm.createContext({console, Math, Number, Array, Object, JSON, Set, Map, Intl, Date});
vm.runInContext(source, context);
const presets = vm.runInContext('JSON.parse(JSON.stringify(SCENARIOS))', context);
const simulate = config => {
  context.testConfig = JSON.parse(JSON.stringify(config));
  return vm.runInContext('simulate(testConfig)', context);
};
const close = (a, b, tolerance = 1e-6) => assert.ok(Math.abs(a-b) <= tolerance, `${a} is not close to ${b}`);

const exact = simulate(presets.high95);
assert.equal(exact.cells.length, 2000);
assert.equal(exact.ops[0].gap, 100);
assert.equal(exact.coveredGap[0][1], 90);
assert.equal(exact.coveredGap[0][2], 2);
assert.equal(exact.coveredGap[0][3], 0);
assert.equal(exact.unionGap[0], 92);
assert.equal(exact.overallNone, 8);

const baseline = simulate(presets.sparse);
for (const period of baseline.cellResults) {
  for (const cell of period) {
    for (let i = 0; i < 4; i++) {
      assert.ok(cell.served[i] <= cell.demand[i] + 1e-7);
      assert.ok(cell.hostLoad[i] <= cell.spare[i] + 1e-7);
      close(cell.carried[i][i], 0);
    }
  }
}
const totalPosted = baseline.ops.reduce((sum, operator) => sum + operator.posted, 0);
close(totalPosted, baseline.totals.privateBenefit - baseline.totals.hostCost, 1e-4);
const sumPairCost = baseline.pairHostCost.flat().reduce((sum, amount) => sum + amount, 0);
close(sumPairCost, baseline.totals.hostCost, 1e-4);

const disabled = simulate({...presets.sparse, mode:'none'});
close(disabled.totals.served, 0);
const moreReserve = simulate({...presets.sparse, reserve:30});
assert.ok(moreReserve.totals.served <= baseline.totals.served);
const repriced = simulate({...presets.sparse, tariffMult:250});
close(repriced.totals.served, baseline.totals.served);
close(repriced.totals.privateBenefit - repriced.totals.hostCost, baseline.totals.privateBenefit - baseline.totals.hostCost);
const priceAdmission = simulate({...presets.sparse, mode:'tariff', tariffMult:250});
assert.ok(priceAdmission.totals.served <= baseline.totals.served);
const publicInterest = simulate({...presets.sparse, mode:'social', social:12, benefit:[.2,.2,.2,.2]});
assert.ok(publicInterest.subsidy > 0);
assert.ok(publicInterest.ops.every(operator => operator.coop >= -1e-6));
const clearingSum = publicInterest.ops.reduce((sum, operator) => sum + operator.clearing, 0);
close(clearingSum, 0, 1e-4);

console.log('ICR-OPT smoke tests passed: coverage, capacity, allocation, prices, surplus and settlements.');
