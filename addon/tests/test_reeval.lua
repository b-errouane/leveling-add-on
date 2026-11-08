-- Offline tests for the live re-evaluation (run from the repo root: luajit addon/tests/test_reeval.lua)
dofile("addon/ForeverLeveler/Plans/elwynn.lua")
ForeverLevelerPlan = ForeverLevelerPlans.elwynn
dofile("addon/ForeverLeveler/Reeval.lua")
local Plan, R = ForeverLevelerPlan, ForeverLevelerReeval
local params, steps = Plan.meta.params, Plan.steps

local function near(a, b, eps) return math.abs(a - b) <= (eps or 1e-3) end
local function check(cond, msg) if not cond then error("FAIL: " .. msg, 2) end end

-- 1) parity with the Python formula (values computed by pipeline.derive.derive.mob_base_xp)
local parity = { { 5, 5, 70.5 }, { 10, 12, 105.0 }, { 10, 8, 67.8571 }, { 16, 10, 0.0 }, { 30, 20, 0.0 }, { 3, 1, 36.0 }, { 10, 5, 27.1429 } }
for _, p in ipairs(parity) do
    check(near(R.mobBaseXP(p[1], p[2]), p[3], 1e-3), string.format("mobBaseXP(%d,%d)=%s expected %s", p[1], p[2], R.mobBaseXP(p[1], p[2]), p[3]))
end

-- 2) quest XP drops when the player outlevels the quest
local turnin
for _, s in ipairs(steps) do if s.type == "turnin" and s.qlevel and s.qxp > 0 then turnin = s break end end
check(turnin, "no turnin step found")
local atLevel = R.stepXP(params, turnin, turnin.qlevel)
local outleveled = R.stepXP(params, turnin, turnin.qlevel + 8)
check(atLevel > 0 and outleveled < atLevel, "quest xp should drop when outleveled")

-- 3) two independent accept steps far apart: the recommendation follows the player's position
local function dist(a, b)
    local dx, dy = (a.x - b.x) * params.mapW / 100, (a.y - b.y) * params.mapH / 100
    return math.sqrt(dx * dx + dy * dy)
end
local A, B
for i, s in ipairs(steps) do
    if s.type == "accept" and #(s.preAll or {}) == 0 and #(s.preAny or {}) == 0 and #(s.deps or {}) == 0 then
        if not A then A = i
        elseif dist(steps[i], steps[A]) > 500 then B = i break end
    end
end
check(A and B, "need two far apart independent accept steps")
local function ctxAt(step, unsat)
    local u = {}
    for _, i in ipairs(unsat) do u[i] = true end
    return { level = 1, x = step.x, y = step.y, satisfied = function(i) return not u[i] end,
        isDone = function() return false end, openCount = 0, hearthReady = false }
end
local rA = R.recommend(Plan, ctxAt(steps[A], { A, B }))
local rB = R.recommend(Plan, ctxAt(steps[B], { A, B }))
check(rA == A, "standing at A should recommend A, got " .. tostring(rA))
check(rB == B, "standing at B should recommend B, got " .. tostring(rB))

-- 4) a step whose dependencies are unsatisfied is never recommended first
local gated
for i, s in ipairs(steps) do if s.type == "turnin" and #(s.deps or {}) > 0 then gated = i break end end
check(gated, "need a turnin step with dependencies")
local unsat = { gated }
for _, d in ipairs(steps[gated].deps) do unsat[#unsat + 1] = d end
local rGated = R.recommend(Plan, ctxAt(steps[gated], unsat))
check(rGated ~= gated, "turnin must not be recommended while its dependencies are open")

-- 5) hearthstone: faster travel is used only when it is ready
if params.home then
    local far = { x = 5, y = 5 }
    local target = steps[gated]
    local t1, used1 = R.travel(params, target, far.x, far.y, true)
    local t2, used2 = R.travel(params, target, far.x, far.y, false)
    check(t1 <= t2, "hearth should never be slower")
    check(used2 == false, "hearth must not be used when not ready")
end

-- 6) steps with value computed offline keep plan order
for i, s in ipairs(steps) do
    if s.type == "sethome" then
        local unsatAll = {}
        for j = i, #steps do unsatAll[#unsatAll + 1] = j end
        local idx, info = R.recommend(Plan, ctxAt(steps[i], unsatAll))
        check(idx == i and info.reason == "plan-order", "sethome should stay in plan order")
        break
    end
end

-- 7) quest log full: accepting is impossible, so nothing is eligible -> fallback to the first unsatisfied step
local full = ctxAt(steps[A], { A, B })
full.openCount = params.questLogSlots
local idx, info = R.recommend(Plan, full)
check(idx == A and info.reason == "fallback", "fallback expected with a full quest log, got " .. tostring(info.reason))

-- 8) all steps satisfied -> done
local none, doneInfo = R.recommend(Plan, { level = 1, x = 0, y = 0, satisfied = function() return true end, isDone = function() return true end })
check(none == nil and doneInfo.reason == "done", "done expected")

print("test_reeval: OK")
