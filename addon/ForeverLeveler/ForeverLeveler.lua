-- Forever Leveler (prototype)
--
-- Shows the next step of a precomputed leveling plan (generated offline by the project's pipeline)
-- and points the TomTom arrow at it. It only DISPLAYS information and reads quest state; it does not
-- automate any gameplay.
--
-- The plan is a reference. The addon always picks the FIRST step whose goal is not yet reached, so
-- deviating from the plan (doing things earlier, skipping quests) is handled automatically.
--
-- Commands: /fl  (status) | list | skip | back | show | hide | arrow | reset | about

local ADDON = "ForeverLeveler"
local Plan = ForeverLevelerPlan
local db
local frame, lineHead, lineMain, lineHint, skipBtn
local current = 0
local waypointUID

local function safe(fn, ...)
    if type(fn) ~= "function" then return nil end
    local ok, a = pcall(fn, ...)
    if ok then return a end
    return nil
end

local function onQuest(q) return C_QuestLog and C_QuestLog.IsOnQuest and safe(C_QuestLog.IsOnQuest, q) or false end
local function flaggedDone(q) return C_QuestLog and C_QuestLog.IsQuestFlaggedCompleted and safe(C_QuestLog.IsQuestFlaggedCompleted, q) or false end
local function objectivesDone(q) return C_QuestLog and C_QuestLog.IsComplete and safe(C_QuestLog.IsComplete, q) or false end

-- A step is satisfied when its goal is reached or can no longer be reached.
local function satisfied(i, step)
    if db.skipped[i] then return true end
    if step.type == "accept" then
        return flaggedDone(step.quest) or onQuest(step.quest)
    elseif step.type == "turnin" then
        return flaggedDone(step.quest) or not onQuest(step.quest)
    elseif step.type == "misc" then
        local q = step.quest
        return flaggedDone(q) or not onQuest(q) or objectivesDone(q)
    elseif step.type == "kill" then
        for _, q in ipairs(step.forQuests or {}) do
            if onQuest(q) and not flaggedDone(q) and not objectivesDone(q) then return false end
        end
        return true
    elseif step.type == "grind" or step.type == "sethome" or step.type == "errand" or step.type == "discover" then
        -- Optional steps: done once the player has reached the level the plan expects after this step.
        return (UnitLevel("player") or 1) >= (step.level or 1)
    end
    return true
end

local function findNext()
    for i, step in ipairs(Plan.steps) do
        if not satisfied(i, step) then return i end
    end
    return nil
end

local VIA = { hearth = "Ruhestein benutzen, dann: ", flight = "Fliegen, dann: " }

local function baseTitle(step)
    if step.type == "accept" then
        return "Annehmen: " .. step.name .. (step.npc and (" bei " .. step.npc) or "")
    elseif step.type == "turnin" then
        return "Abgeben: " .. step.name .. (step.npc and (" bei " .. step.npc) or "")
    elseif step.type == "misc" then
        return "Ziel erledigen: " .. step.name
    elseif step.type == "kill" then
        if step.detour and step.detour > 0 then
            return string.format("Schlenker (+%d yd): %s x%d toeten", step.detour, step.mobName or "?", step.count or 0)
        end
        return string.format("Toeten: %s x%d", step.mobName or "?", step.count or 0)
    elseif step.type == "grind" then
        return string.format("Grinden: %s x%d", step.mobName or "?", step.count or 0)
    elseif step.type == "sethome" or step.type == "errand" or step.type == "discover" then
        return step.name or step.type
    end
    return "?"
end

local function title(step)
    return (VIA[step.via] or "") .. baseTitle(step)
end

local function reason(step)
    if step.type == "kill" then
        local names = table.concat(step.forNames or {}, ", ")
        return "fuer: " .. (names ~= "" and names or "-")
    elseif step.type == "turnin" and step.xp then
        return string.format("Belohnung ca. %d XP", step.xp)
    elseif step.type == "grind" then
        return string.format("bis Level %d (laut Plan)", step.level or 0)
    elseif step.type == "accept" and step.side then
        return "Nebenbei-Quest: im Log lassen, Ziele unterwegs miterledigen"
    elseif step.type == "accept" and step.qlevel then
        return string.format("Quest-Level %d", step.qlevel)
    end
    return ""
end

local function setArrow(step)
    if not step then return end
    if not (TomTom and TomTom.AddWaypoint) then return end
    if waypointUID and TomTom.RemoveWaypoint then pcall(TomTom.RemoveWaypoint, TomTom, waypointUID) end
    waypointUID = nil
    if db.arrowOff then return end
    local ok, uid = pcall(TomTom.AddWaypoint, TomTom, step.map, step.x / 100, step.y / 100,
        { title = title(step), persistent = false, minimap = true, world = true, crazy = true })
    if ok and uid then
        waypointUID = uid
        if TomTom.SetCrazyArrow then pcall(TomTom.SetCrazyArrow, TomTom, uid, 10, title(step)) end
    end
end

local function refresh(force)
    if not db or not Plan then return end
    local i = findNext()
    local level = UnitLevel("player") or 1
    if not i then
        lineHead:SetText("Forever Leveler")
        lineMain:SetText("Plan abgeschlossen (bis Level " .. tostring(Plan.meta.targetLevel) .. ").")
        lineHint:SetText("")
        current = 0
        return
    end
    local step = Plan.steps[i]
    lineHead:SetText(string.format("Schritt %d/%d  |  Level %d  |  Plan: Minute %.0f", i, #Plan.steps, level, step.minute or 0))
    lineMain:SetText(title(step))
    local nextStep = Plan.steps[i + 1]
    local sub = reason(step)
    if step.hint and step.hint ~= "" then sub = (sub ~= "" and (sub .. "  |  ") or "") .. step.hint end
    if nextStep then
        local label = (step.type == "kill" and step.detour and step.detour > 0) and "dann weiter: " or "danach: "
        sub = (sub ~= "" and (sub .. "\n") or "") .. label .. title(nextStep)
    end
    lineHint:SetText(sub)
    if force or i ~= current then
        current = i
        setArrow(step)
    end
end

local function build()
    local tmpl = BackdropTemplateMixin and "BackdropTemplate" or nil
    frame = CreateFrame("Frame", "ForeverLevelerFrame", UIParent, tmpl)
    frame:SetSize(380, 84)
    frame:SetPoint(db.point or "TOP", UIParent, db.relPoint or "TOP", db.x or 0, db.y or -120)
    frame:SetMovable(true)
    frame:EnableMouse(true)
    frame:RegisterForDrag("LeftButton")
    frame:SetScript("OnDragStart", frame.StartMoving)
    frame:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        local p, _, rp, x, y = self:GetPoint()
        db.point, db.relPoint, db.x, db.y = p, rp, x, y
    end)
    if frame.SetBackdrop then
        frame:SetBackdrop({ bgFile = "Interface\\Tooltips\\UI-Tooltip-Background", edgeFile = "Interface\\Tooltips\\UI-Tooltip-Border",
            edgeSize = 12, insets = { left = 3, right = 3, top = 3, bottom = 3 } })
        frame:SetBackdropColor(0, 0, 0, 0.7)
    end
    lineHead = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    lineHead:SetPoint("TOPLEFT", 8, -7)
    lineMain = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlight")
    lineMain:SetPoint("TOPLEFT", 8, -22)
    lineMain:SetWidth(360)
    lineMain:SetJustifyH("LEFT")
    lineHint = frame:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    lineHint:SetPoint("TOPLEFT", 8, -40)
    lineHint:SetWidth(360)
    lineHint:SetJustifyH("LEFT")
    skipBtn = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
    skipBtn:SetSize(70, 18)
    skipBtn:SetPoint("TOPRIGHT", -6, -4)
    skipBtn:SetText("Skip")
    skipBtn:SetScript("OnClick", function()
        if current > 0 then db.skipped[current] = true refresh(true) end
    end)
    if db.hidden then frame:Hide() end
end

local function list()
    local shown, i = 0, findNext()
    if not i then print("|cffffd200FL|r Plan abgeschlossen.") return end
    while i <= #Plan.steps and shown < 6 do
        if not satisfied(i, Plan.steps[i]) then
            print(string.format("|cffffd200FL|r %d. %s", i, title(Plan.steps[i])))
            shown = shown + 1
        end
        i = i + 1
    end
end

SLASH_FL1 = "/fl"
SlashCmdList["FL"] = function(msg)
    local cmd = string.lower(string.match(msg or "", "^(%S*)") or "")
    if cmd == "list" then list()
    elseif cmd == "side" then
        local side = Plan.meta.sideQuests or {}
        if #side == 0 then print("|cffffd200FL|r keine Nebenbei-Quests im Plan") end
        for _, q in ipairs(side) do
            print(string.format("|cffffd200FL|r Nebenbei: %s%s", q.name, onQuest(q.quest) and " (im Log)" or ""))
        end
        for _, q in ipairs(Plan.meta.background or {}) do
            print(string.format("|cffffd200FL|r Bleibt am Planende offen: %s", q.name))
        end
    elseif cmd == "skip" then
        if current > 0 then db.skipped[current] = true refresh(true) end
    elseif cmd == "back" then
        -- un-skip the most recently skipped step
        local last
        for i in pairs(db.skipped) do if not last or i > last then last = i end end
        if last then db.skipped[last] = nil refresh(true) end
    elseif cmd == "show" then db.hidden = false frame:Show()
    elseif cmd == "hide" then db.hidden = true frame:Hide()
    elseif cmd == "arrow" then
        db.arrowOff = not db.arrowOff
        if db.arrowOff and waypointUID and TomTom and TomTom.RemoveWaypoint then pcall(TomTom.RemoveWaypoint, TomTom, waypointUID) waypointUID = nil end
        print("|cffffd200FL|r TomTom-Pfeil " .. (db.arrowOff and "aus" or "an"))
        refresh(true)
    elseif cmd == "reset" then
        db.skipped = {}
        refresh(true)
        print("|cffffd200FL|r uebersprungene Schritte zurueckgesetzt")
    elseif cmd == "about" then
        print("|cffffd200FL|r Plan vom " .. tostring(Plan.meta.generated) .. " fuer " .. tostring(Plan.meta.race) .. ", bis Level " .. tostring(Plan.meta.targetLevel))
        print("|cffffd200FL|r " .. tostring(Plan.meta.note))
        print("|cffffd200FL|r Quellen: " .. tostring(Plan.meta.sources))
    else
        print("|cffffd200FL|r /fl list | side | skip | back | show | hide | arrow | reset | about")
        refresh(true)
    end
end

local ev = CreateFrame("Frame")
ev:SetScript("OnEvent", function(_, event, ...)
    if event == "ADDON_LOADED" then
        if (...) ~= ADDON then return end
        ForeverLevelerDB = ForeverLevelerDB or {}
        db = ForeverLevelerDB
        db.skipped = db.skipped or {}
        if not Plan or not Plan.steps then
            print("|cffffd200FL|r Plan.lua fehlt oder ist leer.")
            return
        end
        build()
        print("|cffffd200FL|r geladen. /fl fuer Befehle.")
        local _, race = UnitRace("player")
        if race and Plan.meta.race and string.lower(race) ~= string.lower(Plan.meta.race) then
            print("|cffffd200FL|r Hinweis: Der Plan ist fuer " .. Plan.meta.race .. " erstellt, du spielst " .. tostring(race) .. ".")
        end
        return
    end
    if not db or not frame then return end
    refresh(event == "PLAYER_ENTERING_WORLD")
end)
for _, e in ipairs({ "ADDON_LOADED", "PLAYER_ENTERING_WORLD", "QUEST_ACCEPTED", "QUEST_TURNED_IN", "QUEST_REMOVED",
    "QUEST_LOG_UPDATE", "UNIT_QUEST_LOG_CHANGED", "PLAYER_LEVEL_UP" }) do
    ev:RegisterEvent(e)
end
