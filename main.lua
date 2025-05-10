local _ = require("gettext")
local UIManager = require("ui/uimanager")
local InfoMessage = require("ui/widget/infomessage")
local WidgetContainer = require("ui/widget/container/widgetcontainer")
local Device = require("device")
local json = require("json")
local logger = require("logger")
local Dispatcher = require("dispatcher")
local util = require("util")

---------------------------------------------------------------------------------------
local Philosopher = WidgetContainer:new {
    name = 'philosopher',
    action_philosopher_show_hitokoto_title = _("Show Hitokoto"),
    json_file_path = nil,
    types_file_path = nil,
    hitokoto_data = nil,
    type_definitions_map = nil, -- 缓存类型定义数据 (以小写 key 为键)
}

function Philosopher:init()
    if self.path then
        self.json_file_path = self.path .. "/data.json"
        self.types_file_path = self.path .. "/types.json"
        logger.info("Philosopher plugin: Attempting to load data.json from:", self.json_file_path)
        logger.info("Philosopher plugin: Attempting to load types.json from:", self.types_file_path)
        self:_loadHitokotoData()
        self:_loadTypeDefinitionsData()
    else
        logger.error("Philosopher plugin: self.path is not available. Cannot determine data file locations automatically.")
    end

    math.randomseed(os.time())

    self.ui.menu:registerToMainMenu(self)
    self:onDispatcherRegisterActions()
end

function Philosopher:_loadHitokotoData()
    if not self.json_file_path then
        logger.warn("Philosopher plugin: json_file_path is not set. Cannot load hitokoto data.")
        return
    end
    local file = io.open(self.json_file_path, "r")
    if not file then
        logger.warn("Philosopher plugin: data.json not found at:", self.json_file_path)
        self.hitokoto_data = nil
        return
    end
    logger.info("Philosopher plugin: data.json found, attempting to read and parse.")
    local content = file:read("*a")
    file:close()
    local ok, data = pcall(json.decode, content)
    if not ok or type(data) ~= "table" then
        logger.error("Philosopher plugin: Invalid JSON format in data.json:", self.json_file_path, data)
        self.hitokoto_data = nil
        return
    end
    if #data == 0 then
        logger.warn("Philosopher plugin: Empty dataset in data.json:", self.json_file_path)
        self.hitokoto_data = {}
        return
    end
    self.hitokoto_data = data
    logger.info("Philosopher plugin: Successfully loaded", #self.hitokoto_data, "entries from data.json.")
end

function Philosopher:_loadTypeDefinitionsData()
    if not self.types_file_path then
        logger.warn("Philosopher plugin: types_file_path is not set. Cannot load type definitions.")
        return
    end
    local file = io.open(self.types_file_path, "r")
    if not file then
        logger.warn("Philosopher plugin: types.json not found at:", self.types_file_path)
        self.type_definitions_map = nil
        return
    end
    logger.info("Philosopher plugin: types.json found, attempting to read and parse.")
    local content = file:read("*a")
    file:close()
    local ok, data = pcall(json.decode, content)
    if not ok or type(data) ~= "table" then
        logger.error("Philosopher plugin: Invalid JSON format in types.json:", self.types_file_path, data)
        self.type_definitions_map = nil
        return
    end
    if #data == 0 then
        logger.warn("Philosopher plugin: Empty dataset in types.json:", self.types_file_path)
        self.type_definitions_map = {}
        return
    end

    self.type_definitions_map = {}
    local valid_types_count = 0
    for _, type_entry in ipairs(data) do
        if type_entry.key and type_entry.desc then
            -- 规范化：将 key 转为小写字符串存储
            local key_as_string = tostring(type_entry.key):lower()
            self.type_definitions_map[key_as_string] = type_entry.desc
            valid_types_count = valid_types_count + 1
        else
            logger.warn("Philosopher plugin: Invalid entry in types.json (entry index " .. tostring(_) .. "), missing key or desc:", util.inspect(type_entry))
        end
    end
    logger.info("Philosopher plugin: Successfully loaded and mapped", valid_types_count, "type definitions from types.json.")
    if valid_types_count == 0 and #data > 0 then
        logger.warn("Philosopher plugin: types.json was parsed but contained no valid type entries (all entries missed key/desc or other issues).")
    end
end

function Philosopher:onDispatcherRegisterActions()
    Dispatcher:registerAction("philosopher_show_hitokoto_action",
        { category = "none", event = "PhilosopherShowHitokoto", title = _("Hitokoto"), general = true })
end

function Philosopher:onPhilosopherShowHitokoto()
    self:showHitokoto()
end

function Philosopher:showHitokoto()
    local data_reloaded = false
    if not self.hitokoto_data or #self.hitokoto_data == 0 then
        if self.json_file_path then
            logger.info("Philosopher plugin: Hitokoto data (data.json) not loaded or empty, attempting to reload.")
            self:_loadHitokotoData()
            data_reloaded = true
        end
    end

    local types_reloaded = false
    if not self.type_definitions_map then -- 检查 map 是否为 nil
        if self.types_file_path then
            logger.info("Philosopher plugin: Type definitions (types.json) not loaded, attempting to reload.")
            self:_loadTypeDefinitionsData()
            types_reloaded = true
        end
    end

    if not self.hitokoto_data or #self.hitokoto_data == 0 then
        local err_msg = "Error: data.json file not found, is empty, or contains invalid JSON. Please ensure data.json is in the philosopher.koplugin directory and is valid."
        if data_reloaded then
             err_msg = "Error: Failed to reload data.json or it remains invalid/empty."
        end
        UIManager:show(InfoMessage:new{
            text = _(err_msg),
            show_icon = true,
            timeout = 5,
        })
        logger.error("Philosopher plugin: Cannot show Hitokoto because hitokoto_data is not loaded or is empty.")
        return
    end

    if not self.type_definitions_map then -- 再次检查 map
        local type_err_msg = "Warning: Type definitions (types.json) not available. Hitokoto will be shown without type description."
        if types_reloaded then
            type_err_msg = "Warning: Failed to reload types.json or it remains invalid/empty. Hitokoto will be shown without type description."
        end
        logger.warn("Philosopher plugin: " .. type_err_msg)
        -- 可以选择是否在此处显示一个短暂的 InfoMessage 给用户
        -- UIManager:show(InfoMessage:new{ text = _(type_err_msg), timeout = 3 })
    end

    UIManager:show(InfoMessage:new{
        text = _(
            self:GetRandomEntryWithDetails()
        ),
        show_icon = false,
        timeout = 10,
    })
end

function Philosopher:addToMainMenu(menu_items)
    menu_items.philosopher = {
        text = _("Philosopher"),
        callback = function()
            self:showHitokoto()
        end,
        hold_callback = function()
            UIManager:show(InfoMessage:new{
                text = _(
                    "<About/>\n"..
                    "Philosopher for KOReader (json Version)\n"..
                    "Version: V0.1.4\n".. -- 版本号更新
                    "Author: cxzx150133, whiteboat\n"..
                    "License: GPL v3"
                ),
                timeout = 10,
            })
        end
    }
end

function Philosopher:GetRandomEntryWithDetails()
    if not self.hitokoto_data or #self.hitokoto_data == 0 then
        logger.error("GetRandomEntryWithDetails: No hitokoto data available.")
        return "Error: Hitokoto data not loaded or empty."
    end

    local entry = self.hitokoto_data[math.random(#self.hitokoto_data)]

    local function safe_value(v)
        if type(v) == "function" then return "" end
        if v == nil then return "" end
        if json.null and v == json.null then return "" end
        if json.is_null and json.is_null(v) then return "" end
        if type(v) == "userdata" then
            local str = tostring(v):lower()
            if str:find("null") then return "" end
        end
        return tostring(v):gsub("^%s+", ""):gsub("%s+$", "")
    end

    local hitokoto = safe_value(entry.hitokoto) or ""
    local from = safe_value(entry.from) or ""
    local from_who = safe_value(entry.from_who) or ""
    -- 规范化：将 entry.type 转为小写字符串进行查找
    local entry_type_key_original = entry.type -- 保留原始值用于日志
    local entry_type_key = safe_value(entry_type_key_original):lower()

    local source_info = ""
    if from ~= "" then
        if from_who ~= "" and from == from_who then
            source_info = "来源自 - 「" .. from .. "」"
        elseif from_who ~= "" then
            source_info = "来源自 - 「" .. from .. "」（" .. from_who .. "）"
        else
            source_info = "来源自 - 「" .. from .. "」"
        end
    end

    local type_desc_text = ""
    if entry_type_key ~= "" then -- 只有当条目本身声明了 type 时才尝试查找
        if self.type_definitions_map and self.type_definitions_map[entry_type_key] then
            type_desc_text = "类型：" .. self.type_definitions_map[entry_type_key]
        else
            -- 增强日志，区分 types.json 是否加载成功
            if not self.type_definitions_map then
                logger.warn("Philosopher plugin: Hitokoto entry has type key '" .. safe_value(entry_type_key_original) .. "' (normalized to '" .. entry_type_key .. "'), but type definitions (types.json) are not loaded/available.")
            else
                logger.warn("Philosopher plugin: Hitokoto entry has type key '" .. safe_value(entry_type_key_original) .. "' (normalized to '" .. entry_type_key .. "'), but it was not found in the loaded type definitions map. Check types.json or data.json entry.")
            end
        end
    else
        -- 如果需要，可以为没有type字段的条目添加debug日志
        -- logger.debug("Philosopher plugin: Hitokoto entry has no type field or it's empty. Original entry:", util.inspect(entry))
    end

    local final_text_parts = {}
    table.insert(final_text_parts, hitokoto)
    if source_info ~= "" then
        table.insert(final_text_parts, source_info)
    end
    if type_desc_text ~= "" then
        table.insert(final_text_parts, type_desc_text)
    end
    return table.concat(final_text_parts, "\n")
end

return Philosopher
