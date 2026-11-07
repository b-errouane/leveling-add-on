-- Forever Data Collector (temporary helper for the private leveling add-on project)
--
-- Only READS information the game already shows to the player and writes it to SavedVariables.
-- It does not automate any gameplay (no clicks, no casting, no movement).
--
-- Collected (all optional, guarded with pcall so a missing API never breaks the game UI):
--   quests    : XP/money reward shown in the quest dialog, objectives with counts, turn-in XP
--   kills     : mob, XP gained, mob level, position, time
--   loots     : items looted per corpse (npc id), for drop-rate estimates
--   samples   : player position + speed every 2 s while moving (map scale / run speed check)
--   levelups  : UnitXPMax per level (XP curve)
--   timeline  : accept / progress / turn-in events with time
--
-- Commands: /fdc status | pause | resume | scan | reset | note <text>
-- NOTE: no combat-log access (restricted for addons since the Retail "Midnight" rules, which also apply to Forever).

local ADDON = "ForeverDataCollector"
local VERSION = "0.1.3"
local MAX = { kills = 6000, loots = 6000, samples = 20000, timeline = 6000, combats = 6000 }

local db
local paused = false
local frame = CreateFrame("Frame")

local function safe(fn, ...)
    if type(fn) ~= "function" then return nil end
    local ok, a, b, c, d, e = pcall(fn, ...)
    if ok then return a, b, c, d, e end
    return nil
end

local function now() return GetTime() end

local function pos()
    if not (C_Map and C_Map.GetBestMapForUnit and C_Map.GetPlayerMapPosition) then return nil end
    local map = C_Map.GetBestMapForUnit("player")
    if not map then return nil end
    local p = C_Map.GetPlayerMapPosition(map, "player")
    if not p then return nil end
    local x, y = p:GetXY()
    if not x or (x == 0 and y == 0) then return nil end
    return map, math.floor(x * 10000 + 0.5) / 100, math.floor(y * 10000 + 0.5) / 100
end

local function push(list, entry)
    local cap = MAX[list] or 5000
    local t = db[list]
    if #t < cap then t[#t + 1] = entry end
end

local function npcIdFromGuid(guid)
    if not guid then return nil end
    local kind, _, _, _, _, id = strsplit("-", guid)
    if kind == "Creature" or kind == "Vehicle" then return tonumber(id) end
    return nil
end

local function playerInfo()
    local _, class = UnitClass("player")
    local _, race = UnitRace("player")
    return { class = class, race = race, faction = UnitFactionGroup("player"), level = UnitLevel("player") }
end

local function questRecord(questID)
    local q = db.quests[questID]
    if not q then
        q = { id = questID }
        db.quests[questID] = q
    end
    return q
end

local function objectivesOf(questID)
    local out = {}
    local list = C_QuestLog and C_QuestLog.GetQuestObjectives and safe(C_QuestLog.GetQuestObjectives, questID)
    if type(list) == "table" then
        for i, o in ipairs(list) do
            out[i] = { text = o.text, type = o.type, have = o.numFulfilled, need = o.numRequired }
        end
    end
    return out
end

local function rewardXPInLog(questID)
    if GetQuestLogRewardXP then
        local xp = safe(GetQuestLogRewardXP, questID)
        if type(xp) == "number" then return xp end
    end
    if C_QuestLog and C_QuestLog.GetQuestLogRewardXP then
        local xp = safe(C_QuestLog.GetQuestLogRewardXP, questID)
        if type(xp) == "number" then return xp end
    end
    return nil
end

-- Quest dialog open (before accepting): XP and money reward are shown.
local function onQuestDetail()
    local id = safe(GetQuestID)
    if not id or id == 0 then return end
    local q = questRecord(id)
    q.title = safe(GetTitleText) or q.title
    q.xpShown = safe(GetRewardXP)
    q.moneyShown = safe(GetRewardMoney)
    q.giverName = UnitName("npc")
    q.giverId = npcIdFromGuid(UnitGUID("npc"))
    q.objectiveText = safe(GetObjectiveText) or q.objectiveText
    q.playerLevelWhenSeen = UnitLevel("player")
    q.seenAt = q.seenAt or now()
end

-- Turn-in dialog (before completing): reward XP shown for the player's level.
local function onQuestComplete()
    local id = safe(GetQuestID)
    if not id or id == 0 then return end
    local q = questRecord(id)
    q.title = safe(GetTitleText) or q.title
    q.xpOnTurnInDialog = safe(GetRewardXP)
    q.moneyOnTurnInDialog = safe(GetRewardMoney)
    q.turnInNpcName = UnitName("npc")
    q.turnInNpcId = npcIdFromGuid(UnitGUID("npc"))
    q.playerLevelAtTurnInDialog = UnitLevel("player")
end

local function onQuestAccepted(...)
    local n = select("#", ...)
    local questID = n >= 2 and select(2, ...) or select(1, ...)
    if type(questID) ~= "number" then return end
    local q = questRecord(questID)
    q.acceptedAt = now()
    q.acceptedAtLevel = UnitLevel("player")
    q.xpInLog = rewardXPInLog(questID) or q.xpInLog
    q.objectives = objectivesOf(questID)
    local map, x, y = pos()
    q.acceptPos = map and { map = map, x = x, y = y } or nil
    push("timeline", { t = now(), type = "accept", quest = questID, level = UnitLevel("player"), map = map, x = x, y = y })
end

local function onQuestTurnedIn(questID, xpReward, moneyReward)
    if type(questID) ~= "number" then return end
    local q = questRecord(questID)
    q.turnedInAt = now()
    q.turnedInAtLevel = UnitLevel("player")
    q.xpTurnedIn = xpReward
    q.moneyTurnedIn = moneyReward
    local map, x, y = pos()
    q.turnInPos = map and { map = map, x = x, y = y } or nil
    push("timeline", { t = now(), type = "turnin", quest = questID, xp = xpReward, level = UnitLevel("player"), map = map, x = x, y = y })
end

local function onQuestLogUpdate()
    -- Record objective completion times (only when counts change).
    if not (C_QuestLog and C_QuestLog.GetNumQuestLogEntries and C_QuestLog.GetInfo) then return end
    local n = safe(C_QuestLog.GetNumQuestLogEntries) or 0
    for i = 1, n do
        local info = safe(C_QuestLog.GetInfo, i)
        if info and not info.isHeader and info.questID then
            local q = db.quests[info.questID]
            if q then
                local objs = objectivesOf(info.questID)
                local sig = {}
                for k, o in ipairs(objs) do sig[k] = tostring(o.have) .. "/" .. tostring(o.need) end
                local s = table.concat(sig, ",")
                if q._sig ~= s then
                    q._sig = s
                    q.objectivesNow = objs
                    push("timeline", { t = now(), type = "progress", quest = info.questID, state = s })
                end
            end
        end
    end
end

-- Snapshot of the whole quest log, including XP rewards (works for quests currently in the log).
local function scan()
    if not (C_QuestLog and C_QuestLog.GetNumQuestLogEntries and C_QuestLog.GetInfo) then
        print("|cffffd200FDC|r Quest log API not available.")
        return
    end
    local n = safe(C_QuestLog.GetNumQuestLogEntries) or 0
    local count = 0
    for i = 1, n do
        local info = safe(C_QuestLog.GetInfo, i)
        if info and not info.isHeader and info.questID then
            local q = questRecord(info.questID)
            q.title = info.title or q.title
            q.level = info.level or q.level
            q.xpInLog = rewardXPInLog(info.questID) or q.xpInLog
            q.objectives = objectivesOf(info.questID)
            q.scanLevel = UnitLevel("player")
            count = count + 1
        end
    end
    print(string.format("|cffffd200FDC|r Scanned %d quests in the log.", count))
end

local function recordXPCurve()
    local lvl = UnitLevel("player")
    local mx = UnitXPMax("player")
    if lvl and mx and mx > 0 then db.xpcurve[lvl] = mx end
end

-- XP gained from a kill: "<Mob> dies, you gain 80 experience."
local lastKillAt = 0
local combatStart = nil
local targetLevels = {}
-- XP from a kill: "<Mob> dies, you gain 80 experience." (chat message, allowed for addons)
local function onXpMessage(text)
    local xp = tonumber(string.match(text or "", "(%d+) experience"))
    if not xp then return end
    local mob = string.match(text, "^(.-) dies") or string.match(text, "^(.-) die")
    local map, x, y = pos()
    push("kills", { t = now(), mob = mob, xp = xp, level = UnitLevel("player"), map = map, x = x, y = y,
        mobLevel = mob and targetLevels[mob] or nil, sinceLast = now() - lastKillAt,
        combatSecs = combatStart and (now() - combatStart) or nil })
    lastKillAt = now()
end

-- Combat segments (replace the combat log, which addons may no longer read): start/end of each fight with the
-- target at the start. Kills that give 0 XP (grey mobs) still show up as a segment.
local segment = nil
local function onCombatStart()
    combatStart = now()
    local name = safe(UnitName, "target")
    segment = { t = combatStart, level = UnitLevel("player"), mob = name,
        mobLevel = safe(UnitLevel, "target"), npc = npcIdFromGuid(safe(UnitGUID, "target")) }
    local map, x, y = pos()
    segment.map, segment.x, segment.y = map, x, y
end
local function onCombatEnd()
    if segment then
        segment.secs = now() - segment.t
        push("combats", segment)
        segment = nil
    end
    combatStart = nil
end

local function onTargetChanged()
    if UnitExists("target") and not UnitIsPlayer("target") then
        local name = UnitName("target")
        local lvl = UnitLevel("target")
        if name and lvl then targetLevels[name] = lvl end
    end
end

local function onLootOpened()
    local num = safe(GetNumLootItems) or 0
    local bySource = {}
    for slot = 1, num do
        local link = safe(GetLootSlotLink, slot)
        local sources = { safe(GetLootSourceInfo, slot) }
        local guid = sources[1]
        if guid then
            bySource[guid] = bySource[guid] or {}
            if link then
                local itemID = tonumber(string.match(link, "item:(%d+)"))
                local _, _, qty = safe(GetLootSlotInfo, slot)
                table.insert(bySource[guid], { item = itemID, qty = qty })
            end
        end
    end
    for guid, items in pairs(bySource) do
        push("loots", { t = now(), npc = npcIdFromGuid(guid), items = items, level = UnitLevel("player") })
    end
    if num == 0 then return end
end

local function onLevelUp(newLevel)
    local lvl = tonumber(newLevel) or UnitLevel("player")
    push("timeline", { t = now(), type = "levelup", level = lvl })
    -- UnitXPMax updates a moment after the event
    if C_Timer and C_Timer.After then C_Timer.After(1, recordXPCurve) else recordXPCurve() end
end

-- Movement sampling (every 2 s while the player moves or speed is non-zero)
local lastSample
local function sample()
    if paused then return end
    local speed = safe(GetUnitSpeed, "player")
    if not speed or speed == 0 then lastSample = nil return end
    local map, x, y = pos()
    if not map then return end
    push("samples", { t = now(), map = map, x = x, y = y, speed = math.floor(speed * 100 + 0.5) / 100,
        mounted = IsMounted and IsMounted() or false })
end

local function init()
    ForeverDataCollectorDB = ForeverDataCollectorDB or {}
    db = ForeverDataCollectorDB
    db.version = VERSION
    db.sessions = db.sessions or {}
    db.quests = db.quests or {}
    db.kills = db.kills or {}
    db.loots = db.loots or {}
    db.samples = db.samples or {}
    db.timeline = db.timeline or {}
    db.combats = db.combats or {}
    db.xpcurve = db.xpcurve or {}
    db.notes = db.notes or {}
    local version, build = GetBuildInfo()
    table.insert(db.sessions, { startedAt = date("%Y-%m-%d %H:%M:%S"), gameVersion = version, build = build,
        player = playerInfo(), uptimeStart = now() })
    recordXPCurve()
end

local function status()
    local function n(t) return #t end
    print(string.format("|cffffd200FDC|r %s | quests %d | kills %d | loots %d | samples %d | timeline %d | xpcurve levels %d",
        paused and "PAUSED" or "recording", (function() local c = 0 for _ in pairs(db.quests) do c = c + 1 end return c end)(),
        n(db.kills), n(db.loots), n(db.samples), n(db.timeline), (function() local c = 0 for _ in pairs(db.xpcurve) do c = c + 1 end return c end)()))
end

SLASH_FDC1 = "/fdc"
SlashCmdList["FDC"] = function(msg)
    local cmd, rest = string.match(msg or "", "^(%S*)%s*(.-)$")
    cmd = string.lower(cmd or "")
    if cmd == "pause" then paused = true print("|cffffd200FDC|r paused")
    elseif cmd == "resume" then paused = false print("|cffffd200FDC|r recording")
    elseif cmd == "scan" then scan()
    elseif cmd == "reset" then
        ForeverDataCollectorDB = nil
        init()
        print("|cffffd200FDC|r data cleared")
    elseif cmd == "note" then
        table.insert(db.notes, { t = now(), level = UnitLevel("player"), text = rest })
        print("|cffffd200FDC|r note saved")
    else status() end
end

frame:SetScript("OnEvent", function(_, event, ...)
    if event == "ADDON_LOADED" then
        if (...) == ADDON then
            init()
            print("|cffffd200FDC|r " .. VERSION .. " loaded. /fdc status | scan | pause | resume | note <text> | reset")
        end
        return
    end
    if not db or paused then return end
    if event == "QUEST_DETAIL" then onQuestDetail()
    elseif event == "QUEST_COMPLETE" then onQuestComplete()
    elseif event == "QUEST_ACCEPTED" then onQuestAccepted(...)
    elseif event == "QUEST_TURNED_IN" then onQuestTurnedIn(...)
    elseif event == "QUEST_LOG_UPDATE" then onQuestLogUpdate()
    elseif event == "CHAT_MSG_COMBAT_XP_GAIN" then onXpMessage((...))
    elseif event == "PLAYER_TARGET_CHANGED" then onTargetChanged()
    elseif event == "LOOT_OPENED" then onLootOpened()
    elseif event == "PLAYER_REGEN_DISABLED" then onCombatStart()
    elseif event == "PLAYER_REGEN_ENABLED" then onCombatEnd()
    elseif event == "PLAYER_LEVEL_UP" then onLevelUp((...))
    elseif event == "PLAYER_ENTERING_WORLD" then recordXPCurve()
    end
end)

frame:RegisterEvent("ADDON_LOADED")
for _, ev in ipairs({ "QUEST_DETAIL", "QUEST_COMPLETE", "QUEST_ACCEPTED", "QUEST_TURNED_IN", "QUEST_LOG_UPDATE",
    "CHAT_MSG_COMBAT_XP_GAIN", "PLAYER_TARGET_CHANGED", "LOOT_OPENED", "PLAYER_LEVEL_UP", "PLAYER_ENTERING_WORLD",
    "PLAYER_REGEN_DISABLED", "PLAYER_REGEN_ENABLED" }) do
    frame:RegisterEvent(ev)
end

if C_Timer and C_Timer.NewTicker then
    C_Timer.NewTicker(2, sample)
end
