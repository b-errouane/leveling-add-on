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

-- ---- State for the live re-evaluation ------------------------------------------------------------
local lastPos            -- last known position in the plan's map frame {x, y}

local function playerPos()
    if not (C_Map and C_Map.GetBestMapForUnit and C_Map.GetPlayerMapPosition) then return nil end
    local map = safe(C_Map.GetBestMapForUnit, "player")
    if not map or map ~= Plan.steps[1].map then return nil end
    local p = safe(C_Map.GetPlayerMapPosition, map, "player")
    if not p then return nil end
    local x, y = p:GetXY()
    if not x or (x == 0 and y == 0) then return nil end
    return x * 100, y * 100
end

local HEARTHSTONE_ITEM = 6948
local function hearthReady()
    -- Conservative: unknown API or cooldown running -> not ready.
    local start, duration
    if C_Container and C_Container.GetItemCooldown then
        start, duration = safe(C_Container.GetItemCooldown, HEARTHSTONE_ITEM)
    elseif GetItemCooldown then
        start, duration = safe(GetItemCooldown, HEARTHSTONE_ITEM)
    end
    if type(start) ~= "number" or type(duration) ~= "number" then return false end
    return duration == 0 or (start + duration) <= GetTime()
end

local function openQuestCount()
    if not (C_QuestLog and C_QuestLog.GetNumQuestLogEntries) then return 0 end
    local _, n = safe(C_QuestLog.GetNumQuestLogEntries)
    return tonumber(n) or 0
end

local function buildCtx(planNext)
    local x, y = playerPos()
    if x then
        lastPos = { x = x, y = y }
    elseif not lastPos then
        local s = Plan.steps[planNext or 1]
        lastPos = { x = s.x, y = s.y }
    end
    return {
        level = UnitLevel("player") or 1, x = lastPos.x, y = lastPos.y,
        satisfied = function(i) return satisfied(i, Plan.steps[i]) end,
        isDone = flaggedDone, openCount = openQuestCount(), hearthReady = hearthReady(),
    }
end

local lastInfo
local cache = { at = -1000, i = nil, planNext = nil }
local function recommended(force)
    -- Quest-log events arrive in bursts: unless forced, reuse a result that is less than a second old.
    if not force and cache.i and (GetTime() - cache.at) < 1 then return cache.i, cache.planNext end
    local planNext = findNext()
    if not planNext then cache.i, cache.planNext, cache.at = nil, nil, GetTime() return nil, nil end
    local i = planNext
    if not db.followPlan and ForeverLevelerReeval and Plan.meta.params then
        local ok, r, info = pcall(ForeverLevelerReeval.recommend, Plan, buildCtx(planNext))
        if ok and r then i, lastInfo = r, info end
    end
    cache.i, cache.planNext, cache.at = i, planNext, GetTime()
    return i, planNext
end

-- ---- Look ---------------------------------------------------------------------------------------------
local COLORS = {
    accept = { 1.00, 0.82, 0.10 }, turnin = { 0.35, 0.90, 0.45 }, kill = { 0.95, 0.35, 0.30 },
    grind = { 1.00, 0.60, 0.20 }, misc = { 0.40, 0.80, 1.00 }, hearth = { 0.45, 0.62, 1.00 },
    sethome = { 0.45, 0.62, 1.00 }, errand = { 0.75, 0.50, 1.00 }, discover = { 0.55, 0.85, 0.85 },
    done = { 0.35, 0.90, 0.45 },
}
local ICONS = {
    accept = "Interface\\GossipFrame\\AvailableQuestIcon", turnin = "Interface\\GossipFrame\\ActiveQuestIcon",
    kill = "Interface\\Icons\\INV_Sword_04", grind = "Interface\\Icons\\INV_Sword_04",
    misc = "Interface\\Icons\\INV_Misc_Map_01", hearth = "Interface\\Icons\\INV_Misc_Rune_01",
    sethome = "Interface\\Icons\\INV_Misc_Rune_01", errand = "Interface\\Icons\\INV_Misc_Book_09",
    discover = "Interface\\Icons\\INV_Misc_Map_01", done = "Interface\\RaidFrame\\ReadyCheck-Ready",
}
local icon, accent, bar, lineNext, distText, arrowBtn

local function kindOf(step)
    if step.via == "hearth" then return "hearth" end
    return step.type
end

local function setColor(tex, c, a)
    if tex.SetColorTexture then tex:SetColorTexture(c[1], c[2], c[3], a or 1) else tex:SetTexture(c[1], c[2], c[3], a or 1) end
end

local function updatePos(planNext)
    local x, y = playerPos()
    if x then
        lastPos = { x = x, y = y }
    elseif not lastPos and planNext then
        local s = Plan.steps[planNext]
        lastPos = { x = s.x, y = s.y }
    end
end

local function progress()
    local n, doneCount = #Plan.steps, 0
    for i = 1, n do if satisfied(i, Plan.steps[i]) then doneCount = doneCount + 1 end end
    return doneCount, n
end

local function refresh(force)
    if not db or not Plan or not frame then return end
    local i, planNext = recommended(force)
    local level = UnitLevel("player") or 1
    local doneCount, total = progress()
    bar:SetMinMaxValues(0, math.max(1, total))
    bar:SetValue(doneCount)
    if not i then
        lineHead:SetText(string.format("FOREVER LEVELER  |  Lv %d", level))
        lineMain:SetText("Plan abgeschlossen")
        lineHint:SetText("Zielstufe " .. tostring(Plan.meta.targetLevel) .. " erreicht oder alle Schritte erledigt.")
        lineNext:SetText("")
        distText:SetText("")
        icon:SetTexture(ICONS.done)
        setColor(accent, COLORS.done)
        bar:SetStatusBarColor(COLORS.done[1], COLORS.done[2], COLORS.done[3], 1)
        current = 0
        return
    end
    local step = Plan.steps[i]
    local kind = kindOf(step)
    local col = COLORS[kind] or COLORS.accept
    setColor(accent, col)
    bar:SetStatusBarColor(col[1], col[2], col[3], 1)
    icon:SetTexture(ICONS[kind] or ICONS.accept)

    local mode = db.followPlan and "Plan" or "Neubewertung"
    local dev = (i ~= planNext) and string.format("  (Plan: %d)", planNext) or ""
    lineHead:SetText(string.format("SCHRITT %d / %d%s  |  Lv %d  |  %s", i, total, dev, level, mode))
    lineMain:SetText(title(step))

    local sub = reason(step)
    if step.hint and step.hint ~= "" then sub = (sub ~= "" and (sub .. "  |  ") or "") .. step.hint end
    if i ~= planNext and lastInfo and lastInfo.reason == "search" then
        sub = (sub ~= "" and (sub .. "  |  ") or "") .. string.format("Neubewertung: ca. %d XP/h", lastInfo.rate)
    end
    lineHint:SetText(sub)

    local nextStep = Plan.steps[i + 1]
    if nextStep then
        local label = (step.type == "kill" and step.detour and step.detour > 0) and "dann weiter" or "danach"
        lineNext:SetText(label .. "  >  " .. title(nextStep))
    else
        lineNext:SetText("")
    end

    updatePos(i)
    if lastPos and ForeverLevelerReeval and Plan.meta.params then
        local yd = ForeverLevelerReeval.dist(Plan.meta.params, lastPos.x, lastPos.y, step.x, step.y)
        distText:SetText(yd >= 1000 and string.format("%.1f k yd", yd / 1000) or string.format("%d yd", yd))
    else
        distText:SetText("")
    end
    arrowBtn:SetText(db.arrowOff and "Pfeil: aus" or "Pfeil: an")

    if force or i ~= current then
        current = i
        setArrow(step)
    end
end

local function flatButton(parent, label, onClick)
    local b = CreateFrame("Button", nil, parent)
    local fs = b:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    fs:SetPoint("CENTER")
    b.label = fs
    b.SetText = function(self, t) fs:SetText(t) self:SetSize(math.max(24, #t * 6 + 8), 14) end
    b:SetText(label)
    b:SetScript("OnEnter", function() fs:SetTextColor(1, 1, 1) end)
    b:SetScript("OnLeave", function() fs:SetTextColor(0.6, 0.6, 0.6) end)
    b:SetScript("OnClick", onClick)
    return b
end

local function build()
    local tmpl = BackdropTemplateMixin and "BackdropTemplate" or nil
    frame = CreateFrame("Frame", "ForeverLevelerFrame", UIParent, tmpl)
    frame:SetSize(372, 104)
    frame:SetPoint(db.point or "TOP", UIParent, db.relPoint or "TOP", db.x or 0, db.y or -120)
    frame:SetScale(db.scale or 1)
    frame:SetClampedToScreen(true)
    frame:SetMovable(true)
    frame:EnableMouse(true)
    frame:RegisterForDrag("LeftButton")
    frame:SetScript("OnDragStart", function(self) if not db.locked then self:StartMoving() end end)
    frame:SetScript("OnDragStop", function(self)
        self:StopMovingOrSizing()
        local p, _, rp, x, y = self:GetPoint()
        db.point, db.relPoint, db.x, db.y = p, rp, x, y
    end)
    if frame.SetBackdrop then
        frame:SetBackdrop({ bgFile = "Interface\\Buttons\\WHITE8X8", edgeFile = "Interface\\Buttons\\WHITE8X8", edgeSize = 1 })
        frame:SetBackdropColor(0.04, 0.05, 0.08, 0.92)
        frame:SetBackdropBorderColor(0.20, 0.22, 0.28, 1)
    end

    -- NOTE: lineHead and lineMain are created first (the offline test addresses them by creation order).
    lineHead = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalSmall")
    lineHead:SetPoint("TOPLEFT", 12, -8)
    lineHead:SetTextColor(0.62, 0.66, 0.74)
    lineMain = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightLarge")
    lineMain:SetPoint("TOPLEFT", 52, -31)
    lineMain:SetWidth(240)
    lineMain:SetHeight(34)
    lineMain:SetJustifyH("LEFT")
    lineMain:SetJustifyV("TOP")
    lineHint = frame:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    lineHint:SetPoint("TOPLEFT", 52, -66)
    lineHint:SetWidth(310)
    lineHint:SetJustifyH("LEFT")
    lineHint:SetTextColor(0.75, 0.78, 0.84)
    lineNext = frame:CreateFontString(nil, "OVERLAY", "GameFontDisableSmall")
    lineNext:SetPoint("BOTTOMLEFT", 12, 7)
    lineNext:SetWidth(348)
    lineNext:SetJustifyH("LEFT")
    distText = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    distText:SetPoint("TOPRIGHT", -12, -33)
    distText:SetWidth(64)
    distText:SetJustifyH("RIGHT")

    accent = frame:CreateTexture(nil, "ARTWORK")
    accent:SetPoint("TOPLEFT", 0, 0)
    accent:SetPoint("BOTTOMLEFT", 0, 0)
    accent:SetWidth(3)
    icon = frame:CreateTexture(nil, "ARTWORK")
    icon:SetSize(30, 30)
    icon:SetPoint("TOPLEFT", 14, -31)

    bar = CreateFrame("StatusBar", nil, frame)
    bar:SetPoint("TOPLEFT", 12, -23)
    bar:SetSize(348, 3)
    bar:SetStatusBarTexture("Interface\\Buttons\\WHITE8X8")
    local barBg = bar:CreateTexture(nil, "BACKGROUND")
    barBg:SetAllPoints()
    setColor(barBg, { 1, 1, 1 }, 0.08)

    skipBtn = flatButton(frame, "Skip", function()
        if current > 0 then db.skipped[current] = true refresh(true) end
    end)
    skipBtn:SetPoint("TOPRIGHT", -8, -5)
    arrowBtn = flatButton(frame, "Pfeil: an", function()
        db.arrowOff = not db.arrowOff
        if db.arrowOff and waypointUID and TomTom and TomTom.RemoveWaypoint then pcall(TomTom.RemoveWaypoint, TomTom, waypointUID) waypointUID = nil end
        refresh(true)
    end)
    arrowBtn:SetPoint("RIGHT", skipBtn, "LEFT", -6, 0)
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
    elseif cmd == "plan" then
        db.followPlan = not db.followPlan
        print("|cffffd200FL|r " .. (db.followPlan and "strikt nach Plan (keine Neubewertung)" or "Neubewertung aktiv"))
        refresh(true)
    elseif cmd == "why" then
        local i, planNext = recommended(true)
        if not i then print("|cffffd200FL|r Plan abgeschlossen.") return end
        print(string.format("|cffffd200FL|r Empfohlen: Schritt %d (%s). Plan-Schritt: %d (%s).", i, title(Plan.steps[i]), planNext, title(Plan.steps[planNext])))
        if lastInfo and lastInfo.reason == "search" and lastInfo.path then
            local names = {}
            for _, k in ipairs(lastInfo.path) do names[#names + 1] = tostring(k) .. ":" .. baseTitle(Plan.steps[k]) end
            print(string.format("|cffffd200FL|r Beste Abfolge: %s | ca. %d XP in %d s (%d XP/h)", table.concat(names, " > "),
                lastInfo.xp, lastInfo.seconds, lastInfo.rate))
        else
            print("|cffffd200FL|r Entscheidung nach Plan-Reihenfolge (" .. tostring(lastInfo and lastInfo.reason or "-") .. ").")
        end
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
    elseif cmd == "scale" then
        local v = tonumber(string.match(msg or "", "^%S+%s+(%S+)"))
        if v and v >= 0.6 and v <= 1.8 then
            db.scale = v
            frame:SetScale(v)
            print("|cffffd200FL|r Skalierung " .. v)
        else
            print("|cffffd200FL|r /fl scale 0.6 bis 1.8 (aktuell " .. tostring(db.scale or 1) .. ")")
        end
    elseif cmd == "lock" then
        db.locked = not db.locked
        print("|cffffd200FL|r Fenster " .. (db.locked and "fixiert" or "verschiebbar"))
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
        print("|cffffd200FL|r /fl list | why | plan | side | skip | back | show | hide | arrow | scale | lock | reset | about")
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
    -- Changes that really alter the situation recompute immediately; bursty log updates are throttled.
    local immediate = event == "PLAYER_ENTERING_WORLD" or event == "QUEST_ACCEPTED" or event == "QUEST_TURNED_IN"
        or event == "QUEST_REMOVED" or event == "PLAYER_LEVEL_UP"
    refresh(immediate)
end)
for _, e in ipairs({ "ADDON_LOADED", "PLAYER_ENTERING_WORLD", "QUEST_ACCEPTED", "QUEST_TURNED_IN", "QUEST_REMOVED",
    "QUEST_LOG_UPDATE", "UNIT_QUEST_LOG_CHANGED", "PLAYER_LEVEL_UP" }) do
    ev:RegisterEvent(e)
end

-- The player moves, so the best next step can change without any event: re-evaluate every few seconds.
if C_Timer and C_Timer.NewTicker then
    C_Timer.NewTicker(3, function() if db and frame and frame:IsShown() then refresh(false) end end)
end
