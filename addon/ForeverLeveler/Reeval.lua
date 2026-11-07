-- Live re-evaluation for Forever Leveler.
--
-- Pure logic, no WoW API calls: everything it needs comes in through `ctx`, so it can be tested offline.
--
-- Idea: the reference plan is computed offline. In game, the real state differs (position, level, quests
-- done earlier or skipped, hearthstone cooldown). A small look-ahead search over the remaining steps rates
-- sequences by  score = XP gained - lambda * seconds  (lambda = XP/s of the reference plan, i.e. the opportunity
-- cost of time). The recommendation is the first step of the best sequence. There are no fixed thresholds:
-- a step is "skipped" or "reordered" only because another sequence scores better in the current state.
--
-- Steps without XP of their own whose value was computed offline (set home, trainer, flight point) are kept
-- in plan order.

ForeverLevelerReeval = {}
local R = ForeverLevelerReeval

local PLAN_ORDER_TYPES = { sethome = true, errand = true, discover = true }

-- Port of pipeline/derive/derive.py:mob_base_xp (Classic formula; the level-difference part is unverified).
function R.mobBaseXP(player, mob)
    local base = player * 5 + 45
    if mob >= player then
        return (base * (20 + math.min(mob - player, 4)) / 10 + 1) / 2
    end
    local gray
    if player <= 5 then gray = 0
    elseif player < 40 then gray = player - 5 - math.floor(player / 10)
    elseif player < 60 then gray = player - 1 - math.floor(player / 5)
    else gray = 51 end
    if mob <= gray then return 0 end
    local zd
    if player <= 7 then zd = 5 elseif player <= 9 then zd = 6 elseif player <= 11 then zd = 7
    elseif player <= 15 then zd = 8 elseif player <= 19 then zd = 9 elseif player <= 29 then zd = 11
    elseif player <= 39 then zd = 12 elseif player <= 44 then zd = 13 elseif player <= 49 then zd = 14
    elseif player <= 54 then zd = 15 elseif player <= 59 then zd = 16 else zd = 17 end
    return base * (1 - (player - mob) / zd)
end

function R.questXP(params, step, level)
    local diff = math.max(0, level - (step.qlevel or level))
    local f = params.xpFactor[math.min(diff, 9) + 1] or 1
    return (step.qxp or 0) * f
end

function R.stepXP(params, step, level)
    if step.type == "kill" or step.type == "grind" then
        local x = (step.count or 0) * R.mobBaseXP(level, step.mobLevel or level)
        if step.elite then x = x * params.eliteMult end
        return x
    elseif step.type == "turnin" then
        return R.questXP(params, step, level)
    end
    return 0
end

local function dist(params, x1, y1, x2, y2)
    local dx = (x1 - x2) * params.mapW / 100
    local dy = (y1 - y2) * params.mapH / 100
    return math.sqrt(dx * dx + dy * dy)
end

R.dist = dist

-- Seconds to get from (x, y) to the step's location. Uses the hearthstone if it is ready and faster.
function R.travel(params, step, x, y, hearthReady)
    local walk = dist(params, x, y, step.x, step.y) / params.runSpeed
    if hearthReady and params.home then
        local alt = params.hearthCast + dist(params, params.home.x, params.home.y, step.x, step.y) / params.runSpeed
        if alt < walk then return alt, true end
    end
    return walk, false
end

local function copy(t)
    local n = {}
    for k, v in pairs(t) do n[k] = v end
    return n
end

-- ctx: level, x, y, satisfied(i) -> bool, isDone(questID) -> bool, openCount, hearthReady, beam, horizon
-- Returns: index of the recommended step (or nil), info table.
function R.recommend(plan, ctx)
    local steps, params = plan.steps, plan.meta.params
    local sat, rem = {}, {}
    for i = 1, #steps do
        sat[i] = ctx.satisfied(i)
        if not sat[i] then rem[#rem + 1] = i end
    end
    if #rem == 0 then return nil, { reason = "done" } end

    -- Steps whose value was computed offline stay in plan order.
    local firstRem = rem[1]
    if PLAN_ORDER_TYPES[steps[firstRem].type] then
        return firstRem, { reason = "plan-order" }
    end

    local lambda = params.lambda
    local K, H = ctx.beam or 24, ctx.horizon or 6
    local level = ctx.level
    local start = { t = 0, xp = 0, x = ctx.x, y = ctx.y, done = {}, turned = {}, opened = ctx.openCount or 0,
        hearthReady = ctx.hearthReady and true or false, path = {}, score = 0 }
    local beam, best = { start }, nil

    local function eligible(i, node)
        local st = steps[i]
        if PLAN_ORDER_TYPES[st.type] or node.done[i] then return false end
        for _, d in ipairs(st.deps or {}) do
            if not (sat[d] or node.done[d]) then return false end
        end
        if st.type == "accept" then
            if node.opened >= params.questLogSlots then return false end
            for _, q in ipairs(st.preAll or {}) do
                if not (ctx.isDone(q) or node.turned[q]) then return false end
            end
            local any = st.preAny or {}
            if #any > 0 then
                local ok = false
                for _, q in ipairs(any) do if ctx.isDone(q) or node.turned[q] then ok = true break end end
                if not ok then return false end
            end
        end
        return true
    end

    for _ = 1, H do
        local nextBeam = {}
        for _, node in ipairs(beam) do
            for _, i in ipairs(rem) do
                if eligible(i, node) then
                    local st = steps[i]
                    local tr, usedHearth = R.travel(params, st, node.x, node.y, node.hearthReady)
                    local nx = {
                        t = node.t + tr + (st.work or 0), xp = node.xp + R.stepXP(params, st, level),
                        x = st.x, y = st.y, done = copy(node.done), turned = copy(node.turned),
                        opened = node.opened, hearthReady = node.hearthReady and not usedHearth,
                        path = copy(node.path),
                    }
                    nx.done[i] = true
                    nx.path[#nx.path + 1] = i
                    if st.type == "accept" then nx.opened = nx.opened + 1 end
                    if st.type == "turnin" then nx.opened = nx.opened - 1 nx.turned[st.quest] = true end
                    nx.score = nx.xp - lambda * nx.t
                    nextBeam[#nextBeam + 1] = nx
                    if not best or nx.score > best.score then best = nx end
                end
            end
        end
        if #nextBeam == 0 then break end
        table.sort(nextBeam, function(a, b) return a.score > b.score end)
        for k = #nextBeam, K + 1, -1 do nextBeam[k] = nil end
        beam = nextBeam
    end

    if not best then return firstRem, { reason = "fallback" } end
    return best.path[1], {
        reason = "search", score = best.score, xp = best.xp, seconds = best.t,
        rate = best.t > 0 and best.xp / best.t * 3600 or 0, path = best.path,
    }
end
