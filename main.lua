local _               = require("gettext")
local UIManager       = require("ui/uimanager")
local InfoMessage     = require("ui/widget/infomessage")
local WidgetContainer = require("ui/widget/container/widgetcontainer")
local json            = require("json")

---------------------------------------------------------------------------------------
local JSON_File_Path  = "/mnt/onboard/.adds/koreader/plugins/philosopher.koplugin/data.json"
---------------------------------------------------------------------------------------
local Philosopher = WidgetContainer:new {
    name = 'philosopher',
}

function Philosopher:init()
    self.ui.menu:registerToMainMenu(self)
end

function Philosopher:addToMainMenu(menu_items)
    menu_items.philosopher = {
        text = _("Philosopher"),
        callback = function()
            UIManager:show(InfoMessage:new{
                text = _(
                    self:GetRandomEntryFromJSON(JSON_File_Path)
                ),
                show_icon = false,
            })
        end,
        hold_callback = function()
            UIManager:show(InfoMessage:new{
                text = _(
                    "<About/>\n"..
                    "Philosopher for KOReader（json Version）\n"..
                    "Version: V0.1.1\n"..
                    "Another: cxzx150133,whiteboat\n"..
                    "License: GPL v3"
                ),
            })
        end
    }
end

---------------------------------------------------------------------------------------
function Philosopher:GetRandomEntryFromJSON(json_path)
    local file = io.open(json_path, "r")
    if not file then return "Error: File not found" end
    
    local content = file:read("*a")
    file:close()
    
    local ok, data = pcall(json.decode, content)
    if not ok or type(data) ~= "table" then return "Error: Invalid JSON format" end
    if #data == 0 then return "Error: Empty dataset" end
    
    math.randomseed(os.time())
    local entry = data[math.random(#data)]
    
    -- 增强型安全处理函数
    local function safe_value(v)
        -- 类型安全检查
        if type(v) == "function" then
            return ""
        end
        
        -- 处理标准null值
        if v == nil then
            return ""
        end
        
        -- 处理JSON库的null表示
        if json.null and v == json.null then
            return ""
        elseif json.is_null and json.is_null(v) then
            return ""
        end
        
        -- 处理userdata类型的null
        if type(v) == "userdata" then
            local str = tostring(v):lower()
            if str:find("null") then
                return ""
            end
        end
        
        -- 最终转换为净化后的字符串
        return tostring(v):gsub("^%s+", ""):gsub("%s+$", "")
    end
    
    local hitokoto = safe_value(entry.hitokoto) or ""
    local from = safe_value(entry.from) or ""
    local from_who = safe_value(entry.from_who) or ""
    
    -- 构建来源信息
    local source = ""
    if from ~= "" then
        source = "来源自 - 「" .. from .. "」"
        if from_who ~= "" then
            source = source .. "（" .. from_who .. "）"
        end
    end
    
    -- 最终拼接处理
    local final_text = hitokoto
    if source ~= "" then
        final_text = final_text .. "\n" .. source
    end
    
    return final_text
end

return Philosopher
