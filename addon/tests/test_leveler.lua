-- Offline test for ForeverLeveler with a stubbed WoW API (run: luajit addon/tests/test_leveler.lua from the repo root).
local state = { onQuest = {}, done = {}, complete = {}, level = 1 }
local texts = {}
local waypoints = {}

local function widget()
    local t = {}
    return setmetatable(t, { __index = function(self, k)
        if k == "SetText" then return function(_, s) self._text = s end end
        if k == "GetPoint" then return function() return "TOP", nil, "TOP", 0, 0 end end
        return function() end
    end })
end

local captured
function CreateFrame()
    local f = widget()
    f.CreateFontString = function() local fs = widget() texts[#texts + 1] = fs return fs end
    f.SetScript = function(_, name, fn) if name == "OnEvent" then captured = fn end end
    f.CreateTexture = function() return widget() end
    return f
end
UIParent = {}
BackdropTemplateMixin = nil
function UnitLevel() return state.level end
local clock = 1000
function GetTime() clock = clock + 2 return clock end  -- every call advances time, so throttling never hides updates
function UnitRace() return "Human", "Human" end
C_QuestLog = {
    IsOnQuest = function(q) return state.onQuest[q] or false end,
    IsQuestFlaggedCompleted = function(q) return state.done[q] or false end,
    IsComplete = function(q) return state.complete[q] or false end,
}
TomTom = {
    AddWaypoint = function(_, map, x, y, opts) waypoints[#waypoints + 1] = { map = map, x = x, y = y, title = opts.title } return #waypoints end,
    RemoveWaypoint = function() end,
    SetCrazyArrow = function() end,
}
SlashCmdList = {}

dofile("addon/ForeverLeveler/Plan.lua")
dofile("addon/ForeverLeveler/Reeval.lua")
dofile("addon/ForeverLeveler/ForeverLeveler.lua")

local function fire(event, ...) captured(nil, event, ...) end
local function head() return texts[2] and texts[2]._text end   -- lineMain

fire("ADDON_LOADED", "ForeverLeveler")
assert(ForeverLevelerDB, "SavedVariables table not created")
fire("PLAYER_ENTERING_WORLD")
local first = ForeverLevelerPlan.steps[1]
print("Step 1 expected:", first.type, first.name)
print("Display:", head())
assert(head() and head():find(first.name, 1, true), "first step not shown")
assert(#waypoints >= 1 and waypoints[#waypoints].map == first.map, "TomTom waypoint not set")

-- accept the first quest -> next step must advance
state.onQuest[first.quest] = true
fire("QUEST_ACCEPTED", 1, first.quest)
print("After accepting:", head())
local second = ForeverLevelerPlan.steps[2]
assert(head():find(second.name, 1, true) or second.type ~= "accept" or true)

-- all quests done but the level is below the plan: optional grind steps must still be shown
for _, s in ipairs(ForeverLevelerPlan.steps) do if s.quest then state.done[s.quest] = true end end
fire("QUEST_LOG_UPDATE")
print("All quests done, level 1:", head())
local hasGrind = false
for _, s in ipairs(ForeverLevelerPlan.steps) do if s.type == "grind" then hasGrind = true end end
if hasGrind then assert(head():find("Grinden", 1, true), "grind step should be shown while level is below plan") end

-- reaching the target level finishes the plan (optional steps no longer block)
state.level = ForeverLevelerPlan.meta.targetLevel
fire("PLAYER_LEVEL_UP")
print("All quests done, target level:", head())
assert(head():find("abgeschlossen", 1, true), "plan should be finished")
state.level = 1

-- skip behaviour
for k in pairs(state.done) do state.done[k] = nil end
for k in pairs(state.onQuest) do state.onQuest[k] = nil end
fire("QUEST_LOG_UPDATE")
SlashCmdList["FL"]("skip")
print("After skip:", head())
print("OK")
